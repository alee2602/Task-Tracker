import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

DB_PATH = Path("tasks.db")

VALID_PRIORITIES = ("alta", "media", "baja")


@dataclass
class Task:
    id: int
    description: str
    priority: str
    done: bool
    created_at: str


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    return conn


def init_db(db_path: Path = DB_PATH) -> None:
    conn = get_connection(db_path)
    try:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                description TEXT NOT NULL,
                priority TEXT NOT NULL CHECK(priority IN ('alta', 'media', 'baja')),
                done INTEGER NOT NULL DEFAULT 0,
                created_at TEXT NOT NULL
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def add_task(description: str, priority: str = "media", db_path: Path = DB_PATH) -> int:
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}.")
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (description, priority, done, created_at) VALUES (?, ?, 0, ?)",
            (description, priority, datetime.now(timezone.utc).isoformat()),
        )
        conn.commit()
        return cursor.lastrowid
    finally:
        conn.close()


def list_tasks(include_done: bool = False, db_path: Path = DB_PATH) -> list[Task]:
    conn = get_connection(db_path)
    try:
        query = "SELECT * FROM tasks"
        if not include_done:
            query += " WHERE done = 0"
        query += " ORDER BY CASE priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END, id"
        rows = conn.execute(query).fetchall()
        return [
            Task(
                id=row["id"],
                description=row["description"],
                priority=row["priority"],
                done=bool(row["done"]),
                created_at=row["created_at"],
            )
            for row in rows
        ]
    finally:
        conn.close()


def mark_done(task_id: int, db_path: Path = DB_PATH) -> bool:
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("UPDATE tasks SET done = 1 WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()


def delete_task(task_id: int, db_path: Path = DB_PATH) -> bool:
    conn = get_connection(db_path)
    try:
        cursor = conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
        conn.commit()
        return cursor.rowcount > 0
    finally:
        conn.close()
