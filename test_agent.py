from agent import chat

tests = [
    "hi — basic chat works?",
    "show me my tasks",
    "add a task to finish sliding window by next Friday",
    "add a task to call mom tomorrow",
    "what's urgent?",
    "show me my tasks again",
]

for msg in tests:
    print(f"You: {msg}")
    print(f"Agent: {chat(msg)}")
    print()
