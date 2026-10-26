from pathlib import Path

import pytest

from tasktracker.db import add_task, delete_task, init_db, list_tasks, mark_done


def test_add_and_list_task(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    task_id = add_task("Buy milk", "alta", db_path)

    tasks = list_tasks(db_path=db_path)
    assert len(tasks) == 1
    assert tasks[0].id == task_id
    assert tasks[0].description == "Buy milk"
    assert tasks[0].priority == "alta"
    assert tasks[0].done is False


def test_mark_done_hides_task_from_default_list(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    task_id = add_task("Walk the dog", db_path=db_path)

    assert mark_done(task_id, db_path) is True
    assert list_tasks(db_path=db_path) == []

    all_tasks = list_tasks(include_done=True, db_path=db_path)
    assert len(all_tasks) == 1
    assert all_tasks[0].done is True


def test_mark_done_unknown_task_returns_false(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    assert mark_done(999, db_path) is False


def test_delete_task(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    task_id = add_task("Temp task", db_path=db_path)

    assert delete_task(task_id, db_path) is True
    assert list_tasks(include_done=True, db_path=db_path) == []


def test_invalid_priority_raises(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    with pytest.raises(ValueError):
        add_task("Bad task", priority="urgent", db_path=db_path)
