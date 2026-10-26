from pathlib import Path

import pytest

from tasktracker.db import (
    HasSubtasksError,
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


def test_create_subtask_with_parent(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    parent_id = add_task("Organizar viaje", db_path=db_path)

    child_id = add_task("Comprar boletos", db_path=db_path, parent_id=parent_id)

    tasks = {t.id: t for t in list_tasks(db_path=db_path)}
    assert tasks[child_id].parent_id == parent_id
    assert tasks[parent_id].parent_id is None


def test_unlimited_nesting(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    grandparent_id = add_task("Nivel 0", db_path=db_path)
    parent_id = add_task("Nivel 1", db_path=db_path, parent_id=grandparent_id)
    child_id = add_task("Nivel 2", db_path=db_path, parent_id=parent_id)

    tasks = {t.id: t for t in list_tasks(db_path=db_path)}
    assert tasks[child_id].parent_id == parent_id
    assert tasks[parent_id].parent_id == grandparent_id


def test_add_task_with_nonexistent_parent_raises(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    with pytest.raises(ValueError):
        add_task("Huerfana", db_path=db_path, parent_id=999)


def test_completing_all_subtasks_autocompletes_parent(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    parent_id = add_task("Organizar viaje", db_path=db_path)
    child1 = add_task("Comprar boletos", db_path=db_path, parent_id=parent_id)
    child2 = add_task("Reservar hotel", db_path=db_path, parent_id=parent_id)

    mark_done(child1, db_path)
    tasks = {t.id: t for t in list_tasks(include_done=True, db_path=db_path)}
    assert tasks[parent_id].done is False  # aun falta child2

    mark_done(child2, db_path)
    tasks = {t.id: t for t in list_tasks(include_done=True, db_path=db_path)}
    assert tasks[parent_id].done is True


def test_autocomplete_propagates_two_levels_up(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    grandparent_id = add_task("Nivel 0", db_path=db_path)
    parent_id = add_task("Nivel 1", db_path=db_path, parent_id=grandparent_id)
    child_id = add_task("Nivel 2", db_path=db_path, parent_id=parent_id)

    mark_done(child_id, db_path)

    tasks = {t.id: t for t in list_tasks(include_done=True, db_path=db_path)}
    assert tasks[parent_id].done is True
    assert tasks[grandparent_id].done is True


def test_adding_subtask_reopens_completed_parent(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    parent_id = add_task("Organizar viaje", db_path=db_path)
    child1 = add_task("Comprar boletos", db_path=db_path, parent_id=parent_id)
    mark_done(child1, db_path)

    tasks = {t.id: t for t in list_tasks(include_done=True, db_path=db_path)}
    assert tasks[parent_id].done is True  # se autocompleto con una sola subtarea

    add_task("Reservar hotel", db_path=db_path, parent_id=parent_id)

    tasks = {t.id: t for t in list_tasks(include_done=True, db_path=db_path)}
    assert tasks[parent_id].done is False


def test_reopen_propagates_two_levels_up(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    grandparent_id = add_task("Nivel 0", db_path=db_path)
    parent_id = add_task("Nivel 1", db_path=db_path, parent_id=grandparent_id)
    child_id = add_task("Nivel 2", db_path=db_path, parent_id=parent_id)
    mark_done(child_id, db_path)

    tasks = {t.id: t for t in list_tasks(include_done=True, db_path=db_path)}
    assert tasks[grandparent_id].done is True

    add_task("Otro nivel 2", db_path=db_path, parent_id=parent_id)

    tasks = {t.id: t for t in list_tasks(include_done=True, db_path=db_path)}
    assert tasks[parent_id].done is False
    assert tasks[grandparent_id].done is False


def test_delete_without_cascade_raises_when_has_subtasks(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    parent_id = add_task("Organizar viaje", db_path=db_path)
    add_task("Comprar boletos", db_path=db_path, parent_id=parent_id)

    with pytest.raises(HasSubtasksError):
        delete_task(parent_id, db_path)


def test_delete_with_cascade_removes_whole_subtree(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    parent_id = add_task("Organizar viaje", db_path=db_path)
    child_id = add_task("Comprar boletos", db_path=db_path, parent_id=parent_id)
    grandchild_id = add_task("Elegir asiento", db_path=db_path, parent_id=child_id)

    assert delete_task(parent_id, db_path, cascade=True) is True

    remaining_ids = {t.id for t in list_tasks(include_done=True, db_path=db_path)}
    assert parent_id not in remaining_ids
    assert child_id not in remaining_ids
    assert grandchild_id not in remaining_ids


def test_deleting_last_pending_subtask_autocompletes_parent(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    parent_id = add_task("Organizar viaje", db_path=db_path)
    child1 = add_task("Comprar boletos", db_path=db_path, parent_id=parent_id)
    child2 = add_task("Reservar hotel", db_path=db_path, parent_id=parent_id)
    mark_done(child1, db_path)

    assert delete_task(child2, db_path) is True

    tasks = {t.id: t for t in list_tasks(include_done=True, db_path=db_path)}
    assert tasks[parent_id].done is True


def test_add_task_with_due_date(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    task_id = add_task("Pagar impuestos", db_path=db_path, due_date="2026-01-15")

    tasks = {t.id: t for t in list_tasks(db_path=db_path)}
    assert tasks[task_id].due_date == "2026-01-15"


def test_task_without_due_date_has_none(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)

    task_id = add_task("Sin fecha", db_path=db_path)

    tasks = {t.id: t for t in list_tasks(db_path=db_path)}
    assert tasks[task_id].due_date is None


def test_list_orders_by_due_date_before_priority(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_task("Vence tarde", priority="alta", db_path=db_path, due_date="2026-12-01")
    add_task("Vence pronto", priority="baja", db_path=db_path, due_date="2026-01-01")
    add_task("Sin fecha", priority="alta", db_path=db_path)

    ordered = [t.description for t in list_tasks(db_path=db_path)]
    assert ordered == ["Vence pronto", "Vence tarde", "Sin fecha"]


def test_overdue_only_filters_past_due_pending_tasks(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    overdue_id = add_task("Tarea vencida", db_path=db_path, due_date="2000-01-01")
    add_task("Tarea futura", db_path=db_path, due_date="2999-01-01")
    done_but_overdue = add_task("Vencida pero completa", db_path=db_path, due_date="2000-01-01")
    mark_done(done_but_overdue, db_path)

    overdue = list_tasks(db_path=db_path, overdue_only=True)
    assert [t.id for t in overdue] == [overdue_id]


def test_subtask_has_independent_due_date(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    parent_id = add_task("Organizar viaje", db_path=db_path, due_date="2026-06-01")
    child_id = add_task("Comprar boletos", db_path=db_path, parent_id=parent_id, due_date="2026-05-01")

    tasks = {t.id: t for t in list_tasks(db_path=db_path)}
    assert tasks[parent_id].due_date == "2026-06-01"
    assert tasks[child_id].due_date == "2026-05-01"


def test_priority_filter(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_task("Alta", priority="alta", db_path=db_path)
    add_task("Media", priority="media", db_path=db_path)
    add_task("Otra alta", priority="alta", db_path=db_path)

    filtered = list_tasks(db_path=db_path, priority_filter="alta")
    assert {t.description for t in filtered} == {"Alta", "Otra alta"}


def test_priority_filter_combines_with_tag_filter(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_task("Alta casa", priority="alta", tags=["casa"], db_path=db_path)
    add_task("Alta trabajo", priority="alta", tags=["trabajo"], db_path=db_path)
    add_task("Media casa", priority="media", tags=["casa"], db_path=db_path)

    filtered = list_tasks(db_path=db_path, priority_filter="alta", tag_filter="casa")
    assert [t.description for t in filtered] == ["Alta casa"]


def test_priority_filter_combines_with_overdue_only(tmp_path: Path):
    db_path = tmp_path / "test.db"
    init_db(db_path)
    add_task("Alta vencida", priority="alta", due_date="2000-01-01", db_path=db_path)
    add_task("Media vencida", priority="media", due_date="2000-01-01", db_path=db_path)
    add_task("Alta futura", priority="alta", due_date="2999-01-01", db_path=db_path)

    filtered = list_tasks(db_path=db_path, priority_filter="alta", overdue_only=True)
    assert [t.description for t in filtered] == ["Alta vencida"]
