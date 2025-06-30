#!/bin/bash

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Change to the project directory
cd "$SCRIPT_DIR"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Creating one..." >&2
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install/update dependencies
echo "Installing dependencies..." >&2
pip install -r requirements.txt >&2 

# Set environment variables
export WORKSPACE_DIR="$SCRIPT_DIR/workspace"
export OPENAI_API_KEY=#YOUR_OPENAI_API_KEY
export GROQ_API_KEY=#YOUR_GROQ_API_KEY

# Ensure workspace directory exists
mkdir -p "$WORKSPACE_DIR"

# Run the MCP server
echo "Starting MCP server..." >&2
python server/mcp_server.py