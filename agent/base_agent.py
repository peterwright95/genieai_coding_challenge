from pydantic_ai import Agent, RunContext, Tool
from tools.file_tools import (
    list_files,
    read_file,
    write_file,
    delete_file,
    answer_question_about_files
)
from pathlib import Path

def build_agent(base_directory: str) -> Agent:
    """
    Initializes the file agent scoped to a specific base directory.
    """
    prompt_path = Path(__file__).parent / "prompts" / "base_agent_prompt.txt"
    with open(prompt_path, "r") as f:
        system_prompt = f.read()
        
    agent = Agent(
        model='openai:gpt-4o',
        tools = [Tool(
                    name="list_files",
                    description="List all files in the workspace with their modification times and sizes.",
                    function=list_files
                ), Tool(
                    name="read_file",
                    description="Read the content of a file within the workspace.",
                    function=read_file
                ), Tool(
                    name="write_file",
                    description="Write or append content to a file within the workspace.",
                    function=write_file
                ), Tool(
                    name="delete_file",
                    description="Delete a file within the workspace.",
                    function=delete_file
                ), Tool(
                    name="answer_question_about_files",
                    description="Answer questions about files by analyzing their contents.",
                    function=answer_question_about_files
                )],
        system_prompt=system_prompt
    )


    return agent