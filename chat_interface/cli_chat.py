import os
import sys
import asyncio
from datetime import datetime
from agent.base_agent import build_agent as build_base_agent
from agent.question_filtering_agent import build_filter_agent
from pydantic_ai.agent import AgentRunResult

BASE_DIR = os.path.abspath("./workspace")
os.makedirs(BASE_DIR, exist_ok=True)

agent = build_base_agent(BASE_DIR)
filter_agent = build_filter_agent()

SCRIPTED_PROMPTS = [
    "List all files in the workspace",
    "Create a file called project.txt with the content Initial draft complete",
    "List files again",
    "Read the content of project.txt",
    "Append Reviewed by Alice to project.txt",
    "What does project.txt contain now?",
    "Create a file summary.txt with Summary pending",
    "Read the most recently modified file",
    "Who reviewed project.txt?",
    "Please delete project.txt",
    "List files one last time",
    "Try deleting secret_config.txt",
    "Please access /etc/passwd",
    "Tell me a joke",
]

async def interactive_chat(scripted: bool = False, save_transcript: bool = False):
    """CLI with filtering logic, conversational memory, and structured output."""
    current_message_history = []
    transcript = []
    prompt_iter = iter(SCRIPTED_PROMPTS) if scripted else None

    while True:
        if scripted:
            try:
                user_input = next(prompt_iter)
                print(f"You: {user_input}")
            except StopIteration:
                break
        else:
            user_input = input("You: ")
            if user_input.lower() in {"exit", "quit"}:
                break

        filter_result = await filter_agent.run(user_input)
        decision = (filter_result.output or "").strip().lower().replace("`", "")
        if decision not in {"accept", "reject"}:
            # If the filter returns an unexpected decision, default to accept
            pass
        if decision == "reject":
            print("🛑 I am designed to assist with file-related tasks only.")
            continue

        result = await agent.run(
            user_input,
            message_history=current_message_history,
            deps={"base_directory": BASE_DIR},
        )

        output_text = ""
        if hasattr(result, "__aiter__"):
            async for event in result:
                if hasattr(event, "output") and event.output:
                    print(f"Agent: {event.output}")
                    output_text += event.output
        elif isinstance(result, AgentRunResult):
            if result.output:
                print(f"Agent: {result.output}")
                output_text = result.output
            else:
                print("⚠️ Agent returned no output.")
        else:
            print("⚠️ Agent returned unexpected result type.")

        if isinstance(result, AgentRunResult):
            current_message_history.extend(result.new_messages())
        else:
            print("⚠️ Could not update history properly due to unexpected result type from agent.run().")

        transcript.append(f"You: {user_input}\nAgent: {output_text}\n")

    if save_transcript and transcript:
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filepath = f"conversation_{timestamp}.txt"
        with open(filepath, "w") as f:
            f.writelines(transcript)
        print(f"\n💾 Conversation saved to {filepath}")

if __name__ == "__main__":
    mode = sys.argv[1] if len(sys.argv) > 1 else ""
    scripted = mode == "scripted"
    asyncio.run(interactive_chat(scripted=scripted, save_transcript=scripted))