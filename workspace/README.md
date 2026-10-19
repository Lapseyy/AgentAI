# mini_agent.py - A minimal ReAct-style agent (~70 lines)

mini_agent.py is a self-contained agent that uses a large language model (LLM) to perform file-system tasks. It implements the ReAct loop:

1. Prompt the model with the current conversation and a list of available tools.
2. If the model calls a tool, execute the function locally and feed the result back.
3. Repeat until the model produces a final answer without tool calls.

The agent runs entirely offline (no Anthropic, no extra frameworks) and only requires an NVIDIA-hosted LLM endpoint.

---

## Table of Contents

1. Prerequisites
2. Environment Setup
3. Running the Agent
4. Available Commands
5. Customising the Agent

---

## 1. Prerequisites

- Python 3.9+
- An NVIDIA API account (free tier is sufficient for experimentation). Obtain an API key from https://api.nvidia.com.
- Access to an NVIDIA-hosted model endpoint (e.g., https://integrate.api.nvidia.com/v1).

---

## 2. Environment Setup

1. Clone or download the repository containing mini_agent.py.

2. Create a `.env` file in the same directory as mini_agent.py. The file must contain three variables:

   ```
   NVIDIA_BASE_URL=https://integrate.api.nvidia.com/v1
   NVIDIA_API_KEY=sk-...          # your NVIDIA API key
   MODEL_NAME=nvidia/nemotron-70b   # or any model supported by the endpoint
   ```

   - `NVIDIA_BASE_URL` points to the inference endpoint (the default above works for most NVIDIA deployments).
   - `NVIDIA_API_KEY` is the secret key you received from NVIDIA.
   - `MODEL_NAME` should match a model available on your endpoint. Common choices:
     - nvidia/nemotron-70b
     - nvidia/mistral-7b
     - nvidia/llama-3.1-8b

   *Tip:* You can also use a `.env` manager like `python-dotenv` (already a dependency) to keep secrets out of version control.

3. Install required Python packages (a one-liner):

   ```
   pip install openai python-dotenv
   ```

   The script imports `openai` (to talk to the NVIDIA endpoint) and `python-dotenv` (to load `.env`).

---

## 3. Running the Agent

Open a terminal in the repository root and execute:

```
python mini_agent.py "Create notes.md summarizing what files are in the workspace"
```

- The first argument (or the default task if you pass none) is the natural-language request you want the agent to fulfil.
- The agent will:
  1. List files in its workspace/ directory.
  2. Perform any read/write operations the model requests.
  3. Continue the loop until the model finishes and prints a final answer.

### Example Interactions

| Command | What it does |
|---------|--------------|
| `python mini_agent.py "List all .py files"` | The agent calls `list_files` and prints the result. |
| `python mini_agent.py "Read mini_agent.py and write a short summary"` | The agent reads the file, processes its content, and returns a summary. |
| `python mini_agent.py "Create a file hello.txt with hello world"` | The agent writes `hello.txt` containing "hello world". |

---

## 4. Available Tools

The agent can call four built-in functions:

| Tool | Description | Parameters |
|------|-------------|------------|
| `list_files` | Lists files in the agent's workspace/ directory. | none |
| `read_file` | Reads the contents of a file inside workspace/. | `name` (relative path from workspace) |
| `write_file` | Creates or overwrites a file inside workspace/. | `name`, `content` |
| `get_datetime` | Returns the current date and time (formatted). | none |

All file operations are sandboxed to the workspace/ folder, preventing accidental access to outside paths.

---

## 5. Customising the Agent

- Change the model: Edit `MODEL_NAME` in `.env` or modify the `MODEL` variable in the script.
- Add more tools: Extend the `TOOL_SPECS` list and define corresponding Python functions (following the same signature pattern). Then add the function name to the `TOOLS` dict in `run()`.
- Adjust the turn limit: Change `MAX_TURNS` near the top of the script to allow more or fewer ReAct iterations.
- Different workspace: Set the `WORKSPACE` path (currently `pathlib.Path("workspace")`) to any directory you prefer, provided the sandbox checks still pass.

---

## 6. License

This project is open source and free to use under the MIT License (see the original source for details).

---

Happy prompting!