import sqlite3
from datetime import datetime
from date_parser import parse_date, days_until, format_deadline

DB_NAME = "tasks.db"


def init_db():
    """Create the tasks table if it doesn't exist."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tasks (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT NOT NULL,
            deadline TEXT,
            status TEXT DEFAULT 'pending',
            created_at TEXT NOT NULL
        )
    """)
    conn.commit()
    conn.close()


def add_task(title, deadline=None):
    """Add a new task. Deadline can be natural language like 'next Friday'."""
    parsed_deadline = parse_date(deadline) if deadline else None
    
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, deadline, created_at) VALUES (?, ?, ?)",
        (title, parsed_deadline, datetime.now().isoformat())
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    
    if parsed_deadline:
        return f"Task #{task_id} added: {title} (due {format_deadline(parsed_deadline)})"
    return f"Task #{task_id} added: {title}"


def list_tasks(status=None):
    """List tasks, sorted by deadline urgency. Pending tasks with deadlines come first."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if status:
        cursor.execute(
            "SELECT id, title, deadline, status FROM tasks WHERE status = ?",
            (status,)
        )
    else:
        cursor.execute("SELECT id, title, deadline, status FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No tasks found."
    
    # Sort: pending with deadlines first (by urgency), then pending without, then completed
    def sort_key(row):
        task_id, title, deadline, status = row
        if status == 'completed':
            return (2, 0)
        if deadline:
            return (0, days_until(deadline) or 9999)
        return (1, 0)
    
    rows.sort(key=sort_key)
    
    result = []
    for row in rows:
        task_id, title, deadline, status = row
        deadline_str = f" — due {format_deadline(deadline)}" if deadline else ""
        status_marker = "✓" if status == 'completed' else "○"
        result.append(f"{status_marker} #{task_id} {title}{deadline_str}")
    return "\n".join(result)


def complete_task(task_id):
    """Mark a task as completed."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,)
    )
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    if rows_affected == 0:
        return f"No task found with ID {task_id}"
    return f"Task #{task_id} marked as completed."


def delete_task(task_id):
    """Delete a task."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
    rows_affected = cursor.rowcount
    conn.commit()
    conn.close()
    if rows_affected == 0:
        return f"No task found with ID {task_id}"
    return f"Task #{task_id} deleted."


def get_urgent_tasks(within_days=2):
    """Get pending tasks due within N days (including overdue)."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT id, title, deadline FROM tasks WHERE status = 'pending' AND deadline IS NOT NULL"
    )
    rows = cursor.fetchall()
    conn.close()
    
    urgent = []
    for task_id, title, deadline in rows:
        days = days_until(deadline)
        if days is not None and days <= within_days:
            urgent.append((task_id, title, deadline, days))
    
    if not urgent:
        return "No urgent tasks right now."
    
    # Sort by urgency (overdue first, then soonest)
    urgent.sort(key=lambda x: x[3])
    
    result = ["⚠️ Urgent tasks:"]
    for task_id, title, deadline, days in urgent:
        result.append(f"  #{task_id} {title} — {format_deadline(deadline)}")
    return "\n".join(result)