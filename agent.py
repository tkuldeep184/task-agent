import os
import json
from groq import Groq
from dotenv import load_dotenv
from database import init_db, add_task, list_tasks, complete_task, delete_task, get_urgent_tasks

# Load API key and initialize database
load_dotenv()
init_db()

client = Groq(api_key=os.getenv("GROQ_API_KEY"))

# Define the tools the agent can use
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "add_task",
            "description": "Add a new task to the task list. Use this when the user wants to add, create, or track a new task.",
            "parameters": {
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title or description of the task"
                    },
                    "deadline": {
                        "type": "string",
                        "description": "Optional deadline. Can be natural language like 'tomorrow', 'next Friday', 'in 3 days', or a date like '2026-05-22'."
                    }
                },
                "required": ["title"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "list_tasks",
            "description": "List all tasks. Use this when the user asks to see their tasks, what's pending, or what they need to do.",
            "parameters": {
                "type": "object",
                "properties": {
                    "status": {
                        "type": "string",
                        "enum": ["pending", "completed"],
                        "description": "Filter by status. Omit to see all tasks."
                    }
                }
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "complete_task",
            "description": "Mark a task as completed by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to complete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "delete_task",
            "description": "Delete a task by its ID.",
            "parameters": {
                "type": "object",
                "properties": {
                    "task_id": {
                        "type": "integer",
                        "description": "The ID of the task to delete"
                    }
                },
                "required": ["task_id"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_urgent_tasks",
            "description": "Get tasks that are due soon or overdue. Use this when the user asks what's urgent, what's due soon, what's overdue, or what they should focus on.",
            "parameters": {
                "type": "object",
                "properties": {
                    "within_days": {
                        "type": "integer",
                        "description": "Tasks due within this many days. Default is 2."
                    }
                }
            }
        }
    }
]

# Map tool names to actual Python functions
AVAILABLE_FUNCTIONS = {
    "add_task": add_task,
    "list_tasks": list_tasks,
    "complete_task": complete_task,
    "delete_task": delete_task,
    "get_urgent_tasks": get_urgent_tasks
}

SYSTEM_PROMPT = """You are Kuldeep's personal task manager assistant.

You have tools to add, list, complete, delete, and check urgent tasks. Always use the tools - never make up task data.

When adding a task, pass the deadline as natural language like 'tomorrow' or 'next Friday' - the system parses it.
When the user asks what's urgent or due soon, use get_urgent_tasks.

Be concise and practical."""

conversation_history = [
    {"role": "system", "content": SYSTEM_PROMPT}
]

def chat(user_message):
    """Send a message to the agent and let it use tools if needed."""
    conversation_history.append({
        "role": "user",
        "content": user_message
    })
    
    # First call - agent decides whether to use a tool
    try:
        response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history,
            tools=TOOLS,
            tool_choice="auto",
            temperature=0.5,
        )
    except Exception as e:
        # Remove the failed user message so it doesn't pollute history
        conversation_history.pop()
        return f"Sorry, I had trouble processing that. Try rephrasing? (Error: {str(e)[:100]})"
    
    response_message = response.choices[0].message
    tool_calls = response_message.tool_calls
    
    # If the agent wants to use tools
    if tool_calls:
        conversation_history.append({
            "role": "assistant",
            "content": response_message.content,
            "tool_calls": [
                {
                    "id": tc.id,
                    "type": "function",
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                } for tc in tool_calls
            ]
        })
        
        # Execute each tool call
        for tool_call in tool_calls:
            function_name = tool_call.function.name
            parsed = json.loads(tool_call.function.arguments) if tool_call.function.arguments else None
            function_args = parsed if isinstance(parsed, dict) else {}
            function_to_call = AVAILABLE_FUNCTIONS[function_name]
            function_response = function_to_call(**function_args)
            
            conversation_history.append({
                "role": "tool",
                "tool_call_id": tool_call.id,
                "name": function_name,
                "content": str(function_response)
            })
        
        # Second call - agent generates a final response based on tool results
        second_response = client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=conversation_history,
            temperature=0.7,
        )
        final_message = second_response.choices[0].message.content
        conversation_history.append({
            "role": "assistant",
            "content": final_message
        })
        return final_message
    
    # No tool needed - just return the response
    conversation_history.append({
        "role": "assistant",
        "content": response_message.content
    })
    return response_message.content

def main():
    print("Task Agent ready. Type 'quit' to exit.\n")
    
    while True:
        user_input = input("You: ").strip()
        
        if user_input.lower() in ['quit', 'exit']:
            print("Bye!")
            break
        
        if not user_input:
            continue
        
        response = chat(user_input)
        print(f"\nAgent: {response}\n")

if __name__ == "__main__":
    main()