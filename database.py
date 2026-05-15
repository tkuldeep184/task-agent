import sqlite3
from datetime import datetime

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
    """Add a new task."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO tasks (title, deadline, created_at) VALUES (?, ?, ?)",
        (title, deadline, datetime.now().isoformat())
    )
    conn.commit()
    task_id = cursor.lastrowid
    conn.close()
    return f"Task added with ID {task_id}: {title}"

def list_tasks(status=None):
    """List all tasks, optionally filtered by status."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    if status:
        cursor.execute("SELECT id, title, deadline, status FROM tasks WHERE status = ?", (status,))
    else:
        cursor.execute("SELECT id, title, deadline, status FROM tasks")
    rows = cursor.fetchall()
    conn.close()
    
    if not rows:
        return "No tasks found."
    
    result = []
    for row in rows:
        task_id, title, deadline, status = row
        deadline_str = f" (due: {deadline})" if deadline else ""
        result.append(f"#{task_id} [{status}] {title}{deadline_str}")
    return "\n".join(result)

def complete_task(task_id):
    """Mark a task as completed."""
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE tasks SET status = 'completed' WHERE id = ?", (task_id,))
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