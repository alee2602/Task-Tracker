import sqlite3
from dataclasses import dataclass, field
from datetime import datetime, timezone
from pathlib import Path
from typing import Optional

DB_PATH = Path("tasks.db")

VALID_PRIORITIES = ("alta", "media", "baja")


def normalize_tag(name: str) -> str:
    return name.strip().lower()


@dataclass
class Task:
    id: int
    description: str
    priority: str
    done: bool
    created_at: str
    tags: list[str] = field(default_factory=list)


def get_connection(db_path: Path = DB_PATH) -> sqlite3.Connection:
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA foreign_keys = ON")
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
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS tags (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE
            )
            """
        )
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS task_tags (
                task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
                tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
                PRIMARY KEY (task_id, tag_id)
            )
            """
        )
        conn.commit()
    finally:
        conn.close()


def _get_or_create_tag_id(conn: sqlite3.Connection, name: str) -> int:
    normalized = normalize_tag(name)
    row = conn.execute("SELECT id FROM tags WHERE name = ?", (normalized,)).fetchone()
    if row:
        return row["id"]
    cursor = conn.execute("INSERT INTO tags (name) VALUES (?)", (normalized,))
    return cursor.lastrowid


def add_task(
    description: str,
    priority: str = "media",
    tags: Optional[list[str]] = None,
    db_path: Path = DB_PATH,
) -> int:
    if priority not in VALID_PRIORITIES:
        raise ValueError(f"Invalid priority '{priority}'. Must be one of {VALID_PRIORITIES}.")
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            "INSERT INTO tasks (description, priority, done, created_at) VALUES (?, ?, 0, ?)",
            (description, priority, datetime.now(timezone.utc).isoformat()),
        )
        task_id = cursor.lastrowid
        for tag_name in tags or []:
            tag_id = _get_or_create_tag_id(conn, tag_name)
            conn.execute(
                "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
                (task_id, tag_id),
            )
        conn.commit()
        return task_id
    finally:
        conn.close()


def list_tasks(
    include_done: bool = False,
    tag_filter: Optional[str] = None,
    db_path: Path = DB_PATH,
) -> list[Task]:
    conn = get_connection(db_path)
    try:
        query = """
            SELECT t.*, GROUP_CONCAT(tg.name) AS tags
            FROM tasks t
            LEFT JOIN task_tags tt ON tt.task_id = t.id
            LEFT JOIN tags tg ON tg.id = tt.tag_id
            WHERE 1 = 1
        """
        params: dict = {}
        if not include_done:
            query += " AND t.done = 0"
        if tag_filter:
            query += """
                AND t.id IN (
                    SELECT tt2.task_id FROM task_tags tt2
                    JOIN tags tg2 ON tg2.id = tt2.tag_id
                    WHERE tg2.name = :tag_filter
                )
            """
            params["tag_filter"] = normalize_tag(tag_filter)
        query += """
            GROUP BY t.id
            ORDER BY CASE t.priority WHEN 'alta' THEN 0 WHEN 'media' THEN 1 ELSE 2 END, t.id
        """
        rows = conn.execute(query, params).fetchall()
        return [
            Task(
                id=row["id"],
                description=row["description"],
                priority=row["priority"],
                done=bool(row["done"]),
                created_at=row["created_at"],
                tags=sorted(row["tags"].split(",")) if row["tags"] else [],
            )
            for row in rows
        ]
    finally:
        conn.close()


def add_tag_to_task(task_id: int, tag_name: str, db_path: Path = DB_PATH) -> bool:
    conn = get_connection(db_path)
    try:
        task_exists = conn.execute("SELECT 1 FROM tasks WHERE id = ?", (task_id,)).fetchone()
        if not task_exists:
            return False
        tag_id = _get_or_create_tag_id(conn, tag_name)
        conn.execute(
            "INSERT OR IGNORE INTO task_tags (task_id, tag_id) VALUES (?, ?)",
            (task_id, tag_id),
        )
        conn.commit()
        return True
    finally:
        conn.close()


def remove_tag_from_task(task_id: int, tag_name: str, db_path: Path = DB_PATH) -> bool:
    conn = get_connection(db_path)
    try:
        cursor = conn.execute(
            """
            DELETE FROM task_tags
            WHERE task_id = ?
              AND tag_id = (SELECT id FROM tags WHERE name = ?)
            """,
            (task_id, normalize_tag(tag_name)),
        )
        conn.commit()
        return cursor.rowcount > 0
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
