"""
mini_agent.py - a complete agent in ~70 lines. No framework.

This is the ReAct loop from Lecture 5, with nothing hidden:
  1. Send the model the conversation + a list of tools.
  2. If it asks for a tool, run it yourself and send the result back.
  3. Repeat until it answers without asking for a tool.

Setup:
  pip install anthropic
  export ANTHROPIC_API_KEY=sk-ant-...   # from console.anthropic.com (API billing is separate from a Claude subscription)
  python mini_agent.py "Create notes.md summarizing what files are in the workspace"
"""
import json
import pathlib
import sys
# import anthropic
from openai import OpenAI
from openai import OpenAI
from dotenv import load_dotenv
import os
import datetime
import time


load_dotenv()  

for var in ("NVIDIA_BASE_URL", "NVIDIA_API_KEY", "MODEL_NAME"):
    if not os.getenv(var):
        sys.exit(f"Missing {var} in .env")

client = OpenAI(base_url=os.environ["NVIDIA_BASE_URL"], api_key=os.environ["NVIDIA_API_KEY"])
MODEL = os.environ["MODEL_NAME"]
MAX_TURNS = 10

WORKSPACE = pathlib.Path("workspace")
WORKSPACE.mkdir(exist_ok=True)

def get_datetime() -> str:
    return datetime.datetime.now().strftime("%A, %B %d, %Y %I:%M %p")

def safe_path(name: str) -> pathlib.Path:
    p = (WORKSPACE / name).resolve()
    if WORKSPACE.resolve() not in p.parents and p != WORKSPACE.resolve():
        raise ValueError("path escapes workspace")
    return p


# ---- Tools: plain Python functions. This is all an agent "can do". ----
def list_files(name: str) -> str:
    return safe_path(os.name).read_text(encoding="utf-8")


def read_file(name: str) -> str:
    return safe_path(name).read_text(encoding="utf-8")


def read_file(name: str) -> str:
    return safe_path(name).read_text(encoding="utf-8")


def write_file(name: str, content: str) -> str:
    safe_path(name).write_text(content)
    return f"wrote {len(content)} chars to {name}"


TOOL_SPECS = [
    {"type": "function", "function": {
        "name": "list_files", "description": "List files in the workspace.",
        "parameters": {"type": "object", "properties": {}}}},
    {"type": "function", "function": {
        "name": "read_file", "description": "Read a text file from the workspace.",
        "parameters": {"type": "object", "properties": {"name": {"type": "string"}}, "required": ["name"]}}},
    {"type": "function", "function": {
        "name": "write_file", "description": "Create or overwrite a text file in the workspace.",
        "parameters": {"type": "object",
                       "properties": {"name": {"type": "string"}, "content": {"type": "string"}},
                       "required": ["name", "content"]}}},
    {"type": "function", "function": {
        "name": "get_datetime", "description": "Get the current date and time.",
        "parameters": {"type": "object", "properties": {}}}}, 
]


def run(task: str) -> None:
    messages = [
        {"role": "system", "content": "You are a file assistant. Use the tools to act; do not guess file contents."},
        {"role": "user", "content": task},
    ]

    for turn in range(MAX_TURNS):
        print(f"[turn {turn}] thinking...", flush=True)
        t0 = time.perf_counter()
        resp = client.chat.completions.create(model=MODEL, messages=messages, tools=TOOL_SPECS, max_tokens=2000)
        print(f"   ({time.perf_counter() - t0:.1f}s)")
        msg = resp.choices[0].message

        if not msg.tool_calls:
            print(msg.content)
            return

        messages.append({
            "role": "assistant",
            "content": msg.content or "",
            "tool_calls": [{"id": tc.id, "type": "function",
                            "function": {"name": tc.function.name, "arguments": tc.function.arguments}}
                           for tc in msg.tool_calls],
        })

        for tc in msg.tool_calls:
            print(f"[turn {turn}] {tc.function.name}({tc.function.arguments})")
            try:
                args = json.loads(tc.function.arguments or "{}")
                TOOLS = {"list_files": list_files, "read_file": read_file, "write_file": write_file, "get_datetime": get_datetime}
                out = TOOLS[tc.function.name](**args)
            except Exception as e:
                out = f"ERROR: {e}"
            print(f"   -> {out[:200]}")
            messages.append({"role": "tool", "tool_call_id": tc.id, "content": out})

    print("Stopped: hit MAX_TURNS")


if __name__ == "__main__":
    run(" ".join(sys.argv[1:]) or "List the workspace files and write a short README.md describing them.")