# Plan 003: Subtareas

Spec: [specs/003-subtasks.md](../specs/003-subtasks.md)
Decisiones: [004-subtasks-schema](../decisions/004-subtasks-schema.md), [005-subtask-autocomplete](../decisions/005-subtask-autocomplete.md)

## Cambios de esquema (`db.py`)

- Columna nueva en `tasks`: `parent_id INTEGER REFERENCES tasks(id) ON DELETE RESTRICT`.
- `init_db()` incluye la columna en el `CREATE TABLE IF NOT EXISTS` (bases nuevas) y
  además corre una migración idempotente (`PRAGMA table_info` + `ALTER TABLE ADD COLUMN`
  si falta) para bases ya existentes de los ciclos 001/002.
- `Task` (dataclass): nuevo campo `parent_id: Optional[int] = None`.

## Reglas internas nuevas en `db.py` (no expuestas como comandos)

- `_all_children_done(conn, parent_id) -> bool`: True solo si el padre tiene ≥1
  hijo directo y todos están `done`.
- `_bubble_up_autocomplete_from(conn, parent_id)`: si `_all_children_done`, marca
  ese padre como `done` y repite con su propio padre (recursivo hacia arriba).
- `_reopen_ancestors(conn, parent_id)`: si el padre dado está `done`, lo marca
  `done = 0` y repite con su propio padre (recursivo hacia arriba).
- `_get_descendant_ids(conn, root_id) -> list[int]`: usa `WITH RECURSIVE` para
  obtener todos los descendientes, ordenados del más profundo al menos profundo
  (para poder borrarlos en ese orden sin violar la foreign key).
- `HasSubtasksError(Exception)`: se lanza desde `delete_task` cuando se intenta
  borrar sin `--cascade` una tarea que tiene subtareas directas.

## Funciones modificadas

- `add_task(..., parent_id=None)` (parámetro nuevo al final de la firma, no en
  medio, para no repetir el bug de argumentos posicionales del ciclo 002):
  valida que `parent_id` exista (si no, `ValueError`), inserta la fila, y si
  `parent_id` fue dado llama a `_reopen_ancestors(conn, parent_id)`.
- `mark_done(task_id, db_path)`: tras marcar `done`, llama a
  `_bubble_up_autocomplete_from(conn, parent_id_de_la_tarea)`.
- `delete_task(task_id, db_path=DB_PATH, cascade=False)` (parámetro `cascade` al
  final): sin `cascade`, cuenta hijos directos y lanza `HasSubtasksError` si hay
  alguno; con `cascade`, borra todos los descendientes (del más profundo al
  padre) y luego la tarea. En ambos casos, al final llama a
  `_bubble_up_autocomplete_from` sobre el padre de la tarea borrada (por si su
  eliminación deja al resto de hermanos todos completos).
- `list_tasks`: sin cambios de firma; el `SELECT t.*` ya trae `parent_id`, solo
  se agrega al construir cada `Task`.

## Comandos en `cli.py`

- `task add "<desc>" --parent <id>` — crea una subtarea de `<id>`.
- `task list` (plano, sin cambios de comportamiento salvo nueva columna "Parent").
- `task list --tree` — vista anidada e indentada (ignora `--all`/`--tag`; siempre
  muestra todo el árbol, marcando estado por nodo). Se construye en Python:
  `list_tasks(include_done=True)` trae todo con `parent_id`, se agrupa por padre
  y se imprime recursivamente con indentación por nivel.
- `task rm <id> --cascade` — pasa `cascade=True` a `delete_task`; si se lanza
  `HasSubtasksError`, se captura y se muestra: "Task #<id> has N subtask(s); use
  --cascade to delete them too."

## Tests nuevos en `test_db.py`

1. Crear subtarea con `--parent`, aparece con ese `parent_id`.
2. Crear sub-subtarea (nivel 2) — anidamiento ilimitado funciona.
3. Completar todas las subtareas de un padre → el padre se autocompleta.
4. Autocompletado se propaga dos niveles hacia arriba.
5. Agregar una subtarea nueva a un padre completado → el padre se reabre.
6. Reapertura se propaga dos niveles hacia arriba.
7. `delete_task` sin cascade sobre una tarea con hijos → `HasSubtasksError`.
8. `delete_task` con `cascade=True` → borra todo el subárbol.
9. Borrar la última subtarea pendiente (hoja) de un padre → el padre se autocompleta.
10. `add_task` con `parent_id` inexistente → `ValueError`.

## Verificación manual (= criterios de aceptación del spec)

- [x] `task add "Comprar boletos" --parent 1` crea la subtarea.
- [x] `task add "Sub-sub" --parent <id de la subtarea anterior>` crea un nivel 2.
- [x] `task list --tree` muestra la jerarquía indentada.
- [x] `task list` muestra columna "Parent".
- [x] Completar todas las subtareas de una tarea autocompleta al padre (probado
      con 2 niveles de profundidad, se propaga correctamente).
- [x] Agregar una subtarea nueva a un padre completado lo reabre (y propaga hacia
      arriba hasta el abuelo).
- [x] `task rm <id-con-hijos>` se bloquea con mensaje claro.
- [x] `task rm <id-con-hijos> --cascade` borra todo el subárbol.

## Nota de implementación

Sin divergencias del plan original. La migración idempotente en `init_db()`
(`PRAGMA table_info` + `ALTER TABLE ADD COLUMN` si falta `parent_id`) no se probó
contra una base de datos real de los ciclos 001/002 porque las pruebas manuales
de este proyecto siempre usan un `tasks.db` limpio; queda como comportamiento
esperado pero no verificado en este ciclo.
