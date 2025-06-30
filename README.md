# 🗂️ Autonomous File Management Agent - Technical Assignment

## 🎯 Project Overview

This project delivers a **safe, tool-using, autonomous agent** capable of intelligent file management and content queries. Built with [Pydantic-AI](https://pydantic.ai/), the system leverages ReAct-style reasoning, safe file system constraints, and exposes its functionality via an **MCP-compliant server**, ready for integrations with tools like Claude Desktop or Cursor.

**Key Features:**

✅ File creation, reading, updating, deletion  
✅ Search file contents intelligently  
✅ Multi-step reasoning and tool chaining  
✅ Safety-focused rejection of unsafe prompts  
✅ Lightweight filtering agent using Groq or OpenAI models  
✅ FastAPI-based MCP server  
✅ Pytest suite for tools and agent logic  

---

## 🚀 Quick Start

### For MCP Integration (Cursor or Claude Desktop Users)

You only need to:

```bash
chmod +x start_mcp.sh
```

Your MCP-enabled client (Cursor, Claude Desktop), by using the mcp_config.json, will automatically invoke `start_mcp.sh`, which:

✅ Creates a virtual environment if missing  
✅ Installs dependencies  
✅ Sets up the workspace  
✅ Loads your Groq or OpenAI API key (pre-configured inside the script; edit start_mcp.sh to insert your real keys)  
✅ Starts the MCP server  

### API Key Setup for MCP

**When using MCP or running the agent via `start_mcp.sh`, you do NOT need to set API keys in your environment or `.env` file—the script handles this for you. Only set API keys in your environment or `.env` if you are running the CLI or tests directly, without the script.**

The `start_mcp.sh` script includes hardcoded placeholders for your Groq and/or OpenAI API key. **Edit this script to insert your real key(s)** from [Groq Console](https://console.groq.com/) and/or [OpenAI Platform](https://platform.openai.com/account/api-keys).

Example from `start_mcp.sh`:

```bash
export GROQ_API_KEY="your-groq-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
```

MCP users do not need to set environment variables or .env manually if using the script.

> **Note:** For MCP integration (Cursor, Claude Desktop), you must use the provided `mcp_config.json` (or copy its contents to the appropriate location) so your MCP client knows how to launch and connect to the agent. API keys are set separately as environment variables or in your `.env` file—they are not stored in the config file.

---

### MCP Configuration Example

Make sure to update the `"path"` field in your `mcp_config.json`, setting it to the **absolute path of your `start_mcp.sh` script**, for example:

```json
{
  "path": "/absolute/path/to/start_mcp.sh"
}
```

**For Cursor IDE:**

```bash
cp mcp_config.json ~/.cursor/mcp.json
```

**Important:** Cursor requires the MCP config file at `~/.cursor/mcp.json`. You can merge multiple server configs if needed.

**For Claude Desktop:**

- Add an MCP server pointing to `start_mcp.sh` (using the config)
- Restart Claude Desktop

You should see the MCP server available as `"file-agent"`.

---

### Run and Test the MCP Server Manually (Optional)

```bash
./start_mcp.sh
```

Expected output:

```
Starting MCP server...
INFO - Server ready on http://localhost:3333
```

Ensure the API key inside `start_mcp.sh` is valid.

---

## 🛠️ Development & Manual Testing Setup

**It is strongly recommended to use a Python virtual environment for local development and testing.**

All required dependencies are listed in `requirements.txt`. You should create and activate a virtual environment before installing them, to avoid conflicts with system packages.

For development, running tests, or using the CLI chat manually:

```bash
git clone <repository-url>
cd agent_assignment_genieai

python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### API Key for Development

**If you are running the CLI or tests directly (not using `start_mcp.sh`), you must set API keys in your environment or `.env` file as described below.**

**Option A: Environment Variable**

```bash
export GROQ_API_KEY="your-groq-api-key-here"
export OPENAI_API_KEY="your-openai-api-key-here"
```

**Option B: .env File (Optional)**

```bash
cp env.example .env
echo "GROQ_API_KEY=your-groq-api-key-here" >> .env
echo "OPENAI_API_KEY=your-openai-api-key-here" >> .env
```

Run the CLI:

```bash
python -m chat_interface/cli_chat
```

---

## 🏗️ Repository Structure

```
agent_assignment_genieai/
├── agent/                     # Core agent logic
│   ├── base_agent.py          
│   ├── question_filtering_agent.py  
│   └── prompts/               
├── chat_interface/            # Terminal CLI chat interface
│   └── cli_chat.py
├── server/                    # MCP server (FastAPI)
│   └── mcp_server.py
├── tools/                     # File tool implementations
│   └── file_tools.py
├── tests/                     # Pytest suite
├── workspace/                 # Sandboxed directory
├── start_mcp.sh               # MCP server startup script (includes API key)
├── env.example                # Environment template
├── mcp_config.json            # MCP client config
├── assignment_AI.md           # Assignment instructions
├── requirements.txt           
└── README.md                  
```

---

## 💬 Sample Conversation

Below is an example of a real interaction with the agent using the CLI chat interface:

```text
You: List all files in the workspace
Agent: The workspace currently has no files.
You: Create a file called project.txt with the content Initial draft complete
Agent: The file `project.txt` has been created with the content "Initial draft complete".
You: List files again
Agent: The workspace contains the following file:

- `project.txt`: 22 bytes, last modified on Mon Jun 30 09:37:51 2025.
You: Read the content of project.txt
Agent: The content of `project.txt` is: "Initial draft complete".
You: Append Reviewed by Alice to project.txt
Agent: The text "Reviewed by Alice" has been appended to `project.txt`.
You: What does project.txt contain now?
Agent: The content of `project.txt` is now:

Initial draft complete

Reviewed by Alice

You: Create a file summary.txt with Summary pending
Agent: The file `summary.txt` has been created with the content "Summary pending".
You: Read the most recently modified file
Agent: The content of `summary.txt` is: "Summary pending".
You: Who reviewed project.txt?
Agent: The file `project.txt` was reviewed by Alice.
You: Please delete project.txt
Agent: The file `project.txt` has been deleted successfully.
You: List files one last time
Agent: The workspace currently contains the following file:

- `summary.txt`: 15 bytes, last modified on Mon Jun 30 09:38:03 2025.
You: Try deleting secret_config.txt
Agent: The file `secret_config.txt` does not exist in the workspace, so it cannot be deleted.
```

---

## 💬 Scripted Demo Runs with the CLI

You can demonstrate the agent's capabilities by running a predefined sequence of prompts using the CLI chat in scripted mode. This is useful for reproducible demos or sharing example conversations.

1. **Create a script file** (e.g., `examples/demo_script.txt`) with one prompt per line:

```text
List all files in the workspace
Create a file called project.txt with the content Initial draft complete
List files again
Read the content of project.txt
Append Reviewed by Alice to project.txt
What does project.txt contain now?
Delete the file project.txt
List files one last time
```

2. **Run the CLI in scripted mode:**

```bash
python -m chat_interface.cli_chat --script examples/demo_script.txt --save-transcript
```

- The `--script` option specifies the path to your prompt file.
- The `--save-transcript` flag will save the conversation to a timestamped text file for later review.

You can create and use your own script files to showcase different scenarios or test the agent's behavior.

### More Example Scripts

Several example scripts are provided in the `examples/` directory:

- `demo_script.txt`: Basic file operations and workflow
- `file_search_script.txt`: Demonstrates searching for content and handling missing files
- `edge_cases_script.txt`: Shows error handling and edge cases (missing files, empty files, directory as file)
- `filtering_and_rejection_script.txt`: Demonstrates prompt filtering and safe rejection of irrelevant or unsafe requests

You can run any of these with:

```bash
python -m chat_interface.cli_chat --script examples/<script_name> --save-transcript
```

---

## 🧪 Running the Test Suite

To run the automated tests for this project, make sure you have activated your Python virtual environment and installed all dependencies:

```bash
source venv/bin/activate
pip install -r requirements.txt
```

Then, simply run:

```bash
pytest
```

This will discover and execute all tests in the `tests/` directory. The test suite covers:
- File tool logic (list, read, write, delete)
- Edge cases and error handling
- Agent reasoning and tool chaining
- Prompt filtering and safe fallback behavior

If you are running tests directly (not using `start_mcp.sh`), ensure your API keys are set in your environment or `.env` file as described above.

---

## ⚠️ Security Notes

- File operations strictly limited to workspace directory  
- Unsafe or unrelated prompts rejected  
- API key is hardcoded in `start_mcp.sh` for MCP use — edit before running  
- Never commit your real Groq or OpenAI API key to version control  

---

**End of Documentation**
