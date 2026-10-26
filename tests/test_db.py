from pathlib import Path

import pytest

from tasktracker.db import (
    add_tag_to_task,
    add_task,
    delete_task,
    init_db,
    list_tasks,
    mark_done,
    remove_tag_from_task,
)


def test_add_and_list_task(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    task_id = add_task("Buy milk", "alta", db_path=db_path)

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


def test_add_task_with_tags(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    task_id = add_task("Pagar renta", tags=["casa", "Urgente"], db_path=db_path)

    tasks = list_tasks(db_path=db_path)
    assert len(tasks) == 1
    assert tasks[0].id == task_id
    assert tasks[0].tags == ["casa", "urgente"]


def test_list_tasks_filtered_by_tag(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_task("Pagar renta", tags=["casa"], db_path=db_path)
    add_task("Terminar informe", tags=["trabajo"], db_path=db_path)

    filtered = list_tasks(tag_filter="casa", db_path=db_path)
    assert len(filtered) == 1
    assert filtered[0].description == "Pagar renta"


def test_add_and_remove_tag_from_existing_task(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    task_id = add_task("Comprar pan", db_path=db_path)

    assert add_tag_to_task(task_id, "casa", db_path) is True
    tasks = list_tasks(db_path=db_path)
    assert tasks[0].tags == ["casa"]

    assert remove_tag_from_task(task_id, "casa", db_path) is True
    tasks = list_tasks(db_path=db_path)
    assert tasks[0].tags == []


def test_add_tag_to_unknown_task_returns_false(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    assert add_tag_to_task(999, "casa", db_path) is False


def test_duplicate_tag_is_not_duplicated(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    task_id = add_task("Lavar el carro", tags=["casa", "casa "], db_path=db_path)

    tasks = list_tasks(db_path=db_path)
    assert tasks[0].tags == ["casa"]


def test_deleting_task_cleans_up_tag_links(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    task_id = add_task("Tarea temporal", tags=["casa"], db_path=db_path)

    assert delete_task(task_id, db_path) is True
    # La etiqueta "casa" sigue existiendo para otras tareas, pero el link se limpió.
    other_id = add_task("Otra tarea", tags=["casa"], db_path=db_path)
    assert list_tasks(db_path=db_path)[0].id == other_id
