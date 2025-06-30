#!/usr/bin/env python3
"""
Minimal MCP Server for File Management Agent
Exposes conversational interface and recommended MCP methods
"""

import asyncio
import logging
import os
import sys
from pathlib import Path
from typing import Any, Dict, List, Optional

# Add the project root to the system path to allow for module imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

from agent.base_agent import build_agent
from agent.question_filtering_agent import build_filter_agent

# Configure logging to output to stderr to keep stdout clean for MCP protocol
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr
)
logger = logging.getLogger(__name__)

class FileAgentMCPServer:
    """MCP Server exposing conversational access and recommended methods"""
    
    def __init__(self, base_directory: str = "./workspace"):
        self.base_directory = Path(base_directory).resolve()
        self.base_directory.mkdir(exist_ok=True)
        
        self.file_agent = build_agent(str(self.base_directory))
        self.filter_agent = build_filter_agent()
        
        self.server = Server("file-agent")
        self._setup_handlers()
    
    def _setup_handlers(self):
        """Register tools and recommended MCP methods"""
        
        @self.server.list_tools()
        async def list_tools() -> List[Tool]:
            return [
                Tool(
                    name="chat_with_file_agent",
                    description="Chat with the file agent to manage files, read content, search, or ask questions.",
                    inputSchema={
                        "type": "object",
                        "properties": {
                            "message": {
                                "type": "string",
                                "description": "Your message or request"
                            }
                        },
                        "required": ["message"]
                    }
                )
            ]

        @self.server.call_tool()
        async def call_tool(name: str, arguments: Optional[Dict[str, Any]]) -> List[TextContent]:
            logger.info(f"Tool called: {name}, arguments: {arguments}")
            
            if name != "chat_with_file_agent":
                return [TextContent(type="text", text=f"Unknown tool: {name}")]
            
            message = (arguments or {}).get("message", "").strip()
            if not message:
                return [TextContent(type="text", text="Please provide a message")]
            
            try:
                filter_result = await self.filter_agent.run(message)
                if (filter_result.output or "").strip().lower() == "reject":
                    return [TextContent(type="text", text="I only assist with file-related tasks.")]
                
                result = await self.file_agent.run(message, deps={"base_directory": str(self.base_directory)})
                output = getattr(result, "output", str(result))
                return [TextContent(type="text", text=output)]
            
            except Exception as e:
                logger.error(f"Error processing request: {e}", exc_info=True)
                return [TextContent(type="text", text=f"Error: {str(e)}")]

        @self.server.list_resources()
        async def list_resources() -> List[Any]:
            """Expose workspace files as resources"""
            try:
                files = os.listdir(self.base_directory)
                return [
                    {"name": f, "description": f"File in workspace: {f}"}
                    for f in files
                ]
            except Exception as e:
                logger.error(f"Error listing resources: {e}", exc_info=True)
                return []

        
    async def run(self):
        """Start the MCP server"""
        logger.info(f"Starting File Agent MCP Server (workspace: {self.base_directory})")
        
        async with stdio_server() as (read_stream, write_stream):
            await self.server.run(
                read_stream,
                write_stream,
                self.server.create_initialization_options()
            )

async def main():
    """Main entry point"""
    import argparse
    
    parser = argparse.ArgumentParser(description="File Agent MCP Server")
    parser.add_argument(
        "--workspace",
        default="./workspace",
        help="Workspace directory for file operations (default: ./workspace)"
    )
    
    args = parser.parse_args()
    server = FileAgentMCPServer(args.workspace)
    await server.run()

if __name__ == "__main__":
    asyncio.run(main())