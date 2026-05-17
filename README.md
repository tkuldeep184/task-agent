# Task Agent

> A personal AI task manager that understands natural language. Built with Python, Groq's Llama 3.3, and SQLite. Talk to it like a person — it actually does what you ask.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.11+-blue)
![License](https://img.shields.io/badge/license-MIT-green)

---

## What this is

This isn't a chatbot pretending to be useful — it's a genuine **AI agent** with real tools. You say *"add a task to finish sliding window problems by next Friday"* and the agent parses the deadline, stores it in a database, and proactively warns you when it's due.

The difference between a chatbot and an agent matters here: a chatbot only generates text. An agent reasons about your intent, calls real functions, observes results, and responds based on what actually happened.

## The agent loop
Perceive  →  Reason     →  Act         →  Observe     →  Respond
(message)    (which tool?)  (run function)  (read result)  (reply)

Every turn flows through this loop. The LLM decides which tool fits, the tool executes real Python code, and the result feeds back into the conversation.

## Features

- **Natural conversation** — say *"what's urgent?"* or *"add a task to call mom tomorrow"*
- **Smart date parsing** — `"next Friday"`, `"in 3 days"`, `"tomorrow"` all become real dates
- **Deadline awareness** — tasks sort by urgency, overdue items get flagged automatically
- **Persistent storage** — SQLite database survives restarts; your tasks don't vanish
- **Two interfaces** — terminal CLI for power users, web UI for everyday use
- **Tool calling** — the LLM uses real functions, not hallucinated text

## Tech stack

| Layer | Technology |
|-------|-----------|
| LLM | Groq API (Llama 3.3 70B) |
| Backend | Python 3.11, Flask |
| Database | SQLite |
| Date parsing | python-dateutil + custom logic |
| Frontend | Vanilla HTML/CSS/JS (no frameworks) |

## Project structure

```
task-agent/
├── agent.py           # LLM tool-calling loop
├── database.py        # SQLite task CRUD
├── date_parser.py     # Natural language → ISO date
├── app.py             # Flask web server
├── templates/
│   └── index.html     # Terminal-aesthetic chat UI
├── .env               # GROQ_API_KEY (gitignored)
├── .gitignore
└── README.md
```

## Quick start

### 1. Clone and set up

```bash
git clone https://github.com/tkuldeep184/task-agent.git
cd task-agent
python -m venv venv

# Windows
venv\Scripts\activate
# Mac/Linux
source venv/bin/activate

pip install groq python-dotenv python-dateutil flask
```

### 2. Add your Groq API key

Get a free key from [console.groq.com](https://console.groq.com), then create a `.env` file:

```
GROQ_API_KEY=your_key_here
```

### 3. Run it

**Web UI (recommended):**
```bash
python app.py
```
Open [http://127.0.0.1:5000](http://127.0.0.1:5000) in your browser.

**CLI:**
```bash
python agent.py
```

## Example session

```
user@kuldeep ›  add a task to finish sliding window by next Friday
agent ›         ✓ Task #1 added: finish sliding window (due 2026-05-22, in 5 days)

user@kuldeep ›  add a task to call mom tomorrow
agent ›         ✓ Task #2 added: call mom (due 2026-05-18, tomorrow)

user@kuldeep ›  what's urgent?
agent ›         ⚠ 1 task needs attention:
                #2 call mom — due tomorrow

user@kuldeep ›  mark task 2 as completed
agent ›         ✓ Task #2 marked as completed.
```

## How tool calling works

The agent exposes five tools to the LLM:

| Tool | What it does |
|------|-------------|
| `add_task` | Creates a task with optional natural-language deadline |
| `list_tasks` | Lists tasks, sorted by urgency |
| `complete_task` | Marks a task as done |
| `delete_task` | Removes a task |
| `get_urgent_tasks` | Returns tasks due within N days |

Each tool is described in a JSON schema the LLM reads. When you send a message, the LLM picks the right tool (or none), passes structured arguments, and the result feeds back into a second LLM call that phrases the response naturally.

## Engineering notes

A few decisions worth highlighting:

- **Parameterized SQL queries everywhere** — the LLM can generate task titles, and we treat that text as untrusted input. No string concatenation, no SQL injection risk.
- **Defensive arg parsing** — `json.loads(tool_call.function.arguments) if tool_call.function.arguments else {}` because Llama 3.3 occasionally returns `null` instead of `{}` for tool calls without args.
- **Strict system prompt** — early versions hallucinated tasks (*"buy groceries"*) when asked vaguely. The fix was a constraint-heavy system prompt explicitly forbidding invented tasks.
- **Low temperature (0.3)** — higher creativity means more malformed tool calls. Cooler outputs are more reliable.

## Roadmap

- [ ] Google Calendar two-way sync
- [ ] Voice input via Whisper
- [ ] Task analytics (completion rate, streaks)
- [ ] Multi-user with proper auth
- [ ] Push notifications for urgent tasks
- [ ] Mobile-responsive UI

## License

MIT — use it, fork it, build on it.

## Author

Built by [Kuldeep](https://github.com/tkuldeep184) while preparing for SWE interviews. Genuinely useful, not just a portfolio piece.