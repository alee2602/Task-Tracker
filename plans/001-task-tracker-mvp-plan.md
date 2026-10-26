# Plan 001: Task Tracker MVP

Spec: [specs/001-task-tracker-mvp.md](../specs/001-task-tracker-mvp.md)
Decisiones: [001-storage-sqlite](../decisions/001-storage-sqlite.md), [002-cli-typer](../decisions/002-cli-typer.md)

## Estructura de archivos

```
pyproject.toml              # dependencias + entry point `task`
src/tasktracker/
  __init__.py
  db.py                     # conexión SQLite, init de esquema, funciones CRUD
  cli.py                    # app Typer, subcomandos
tests/
  test_db.py                # tests de las funciones CRUD
```

## Esquema de base de datos (`tasks.db`)

```sql
CREATE TABLE tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    description TEXT NOT NULL,
    priority TEXT NOT NULL CHECK(priority IN ('alta', 'media', 'baja')),
    done INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL
);
```

## Funciones en `db.py`

- `init_db()` — crea la tabla si no existe.
- `add_task(description, priority) -> id`
- `list_tasks(include_done: bool) -> list[Task]`
- `mark_done(id)`
- `delete_task(id)`

## Comandos en `cli.py` (Typer)

- `task add "<descripción>" --priority alta|media|baja` (default: `media`)
- `task list` (pendientes) / `task list --all` (incluye completadas) → tabla con
  columnas: ID, Prioridad, Estado, Descripción
- `task done <id>`
- `task rm <id>`

## Pasos de implementación

1. Crear `pyproject.toml` con dependencia `typer` y entry point `task = "tasktracker.cli:app"`.
2. Implementar `db.py` con las funciones CRUD + `init_db()`.
3. Implementar `cli.py`: cada subcomando llama a `db.py`, formatea salida (tabla simple).
4. Tests en `test_db.py` para cada función CRUD (usando una DB temporal, no `tasks.db` real).
5. Instalar en modo editable (`pip install -e .`) y probar manualmente contra los
   criterios de aceptación del spec.

## Verificación (checklist manual, igual a criterios de aceptación del spec)

- [x] `task add "Comprar leche" --priority alta` y aparece en `task list`.
- [x] `task done <id>` y desaparece de `task list` (pero aparece en `task list --all`).
- [x] `task rm <id>` y ya no aparece en ningún listado.
- [x] Reabrir terminal → las tareas siguen ahí.

## Nota de implementación (divergencia menor)

El símbolo `✓` planeado para marcar tareas completadas en la tabla causaba un
`UnicodeEncodeError` en la consola clásica de Windows (code page 1252). Se cambió
a texto plano (`done` / `pending`) para que funcione en cualquier terminal, sin
afectar la funcionalidad.
