import os
import sys
import asyncio
from datetime import datetime
from agent.base_agent import build_agent as build_base_agent
from agent.question_filtering_agent import build_filter_agent
from pydantic_ai.agent import AgentRunResult
import argparse

BASE_DIR = os.path.abspath("./workspace")
os.makedirs(BASE_DIR, exist_ok=True)

agent = build_base_agent(BASE_DIR)
filter_agent = build_filter_agent()

async def interactive_chat(scripted: bool = False, save_transcript: bool = False, script_file: str = None):
    """CLI with filtering logic, conversational memory, and structured output."""
    current_message_history = []
    transcript = []
    prompt_iter = None
    if scripted and script_file:
        with open(script_file, "r") as f:
            prompts = [line.strip() for line in f if line.strip()]
        prompt_iter = iter(prompts)

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
        runs_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "runs"))
        os.makedirs(runs_dir, exist_ok=True)
        if script_file:
            import re
            base_name = os.path.splitext(os.path.basename(script_file))[0]
            safe_base_name = re.sub(r'[^a-zA-Z0-9_-]', '', base_name)
            filename = f"{safe_base_name}_conversation_{timestamp}.txt"
        else:
            filename = f"conversation_{timestamp}.txt"
        filepath = os.path.join(runs_dir, filename)
        with open(filepath, "w") as f:
            f.writelines(transcript)
        print(f"\n💾 Conversation saved to {filepath}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="CLI chat interface for the file agent.")
    parser.add_argument("--script", type=str, help="Path to a file containing scripted prompts (one per line). If provided, runs in scripted mode.")
    parser.add_argument("--save-transcript", action="store_true", help="Save the conversation transcript to a file.")
    args = parser.parse_args()

    asyncio.run(interactive_chat(scripted=bool(args.script), save_transcript=args.save_transcript, script_file=args.script))