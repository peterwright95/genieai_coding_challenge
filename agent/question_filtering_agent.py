from pydantic_ai import Agent
from pathlib import Path

def build_filter_agent():
    prompt_path = Path(__file__).parent / "prompts" / "question_filtering_agent_prompt.txt"
    with open(prompt_path, "r") as f:
        system_prompt = f.read()
    return Agent(
        model="groq:llama-3.1-8b-instant",
        system_prompt=system_prompt
    )