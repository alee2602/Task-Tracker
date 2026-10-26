# Plan 002: Etiquetas / categorías

Spec: [specs/002-tags.md](../specs/002-tags.md)
Decisión: [decisions/003-tags-normalized-schema.md](../decisions/003-tags-normalized-schema.md)

## Cambios de esquema (`db.py`)

```sql
CREATE TABLE IF NOT EXISTS tags (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS task_tags (
    task_id INTEGER NOT NULL REFERENCES tasks(id) ON DELETE CASCADE,
    tag_id INTEGER NOT NULL REFERENCES tags(id) ON DELETE CASCADE,
    PRIMARY KEY (task_id, tag_id)
);
```

Nombres de etiqueta se normalizan a minúsculas + `strip()` antes de guardar o
comparar, para evitar duplicados como "Casa" vs "casa ".

`init_db()` necesita habilitar `PRAGMA foreign_keys = ON` para que el `ON DELETE
CASCADE` funcione (SQLite lo tiene desactivado por default).

## Funciones nuevas/modificadas en `db.py`

- `get_or_create_tag(name) -> tag_id` — busca por nombre normalizado, crea si no existe.
- `add_task(description, priority, tags=None)` — modificada: tras insertar la tarea,
  crea/asocia cada tag de la lista.
- `list_tasks(include_done, tag_filter=None)` — modificada: hace JOIN con
  `task_tags`/`tags` para incluir `task.tags: list[str]`; si `tag_filter` viene,
  filtra solo tareas que tengan esa etiqueta.
- `add_tag_to_task(task_id, tag_name) -> bool`
- `remove_tag_from_task(task_id, tag_name) -> bool`
- `Task` (dataclass): nuevo campo `tags: list[str]`.
- `delete_task`: sin cambios funcionales (el `ON DELETE CASCADE` limpia `task_tags`
  automáticamente).

## Comandos nuevos/modificados en `cli.py`

- `task add "<desc>" --priority alta --tags casa,urgente` (tags opcional, split por coma)
- `task list --tag casa` (filtra; combinable con `--all`)
- `task tag <id> <etiqueta>` — agrega una etiqueta a una tarea existente
- `task untag <id> <etiqueta>` — quita una etiqueta de una tarea existente
- Tabla de `list` gana una columna "Tags" (etiquetas separadas por coma en la celda)

## Pasos de implementación

1. Actualizar `init_db()` con las dos tablas nuevas + `PRAGMA foreign_keys = ON`.
2. Implementar `get_or_create_tag`, modificar `add_task`, implementar
   `add_tag_to_task` / `remove_tag_from_task`, modificar `list_tasks` con JOIN y filtro.
3. Actualizar `cli.py`: opción `--tags` en `add`, opción `--tag` en `list`, comandos
   nuevos `tag`/`untag`, columna "Tags" en la tabla de salida.
4. Tests nuevos en `test_db.py`: crear tarea con tags, filtrar por tag, agregar tag
   a tarea existente, quitar tag, verificar que etiquetas no se duplican.

## Verificación (checklist manual = criterios de aceptación del spec)

- [x] `task add "Pagar renta" --tags casa,urgente` y aparece con ambas etiquetas en `task list`.
- [x] `task list --tag casa` muestra solo tareas con esa etiqueta.
- [x] `task tag <id> trabajo` agrega una etiqueta nueva a una tarea existente.
- [x] `task untag <id> urgente` la quita sin afectar las demás etiquetas de esa tarea.

## Nota de implementación (divergencia menor)

Al agregar el parámetro `tags` a `add_task()` entre `priority` y `db_path`, un test
existente que llamaba a `add_task` con argumentos posicionales empezó a escribir en
el `tasks.db` real del proyecto en vez de la base de datos temporal de prueba
(el argumento posicional cayó en el parámetro equivocado). Se corrigió el test para
pasar `db_path` por keyword, igual que los demás tests. Lección: cualquier función
con múltiples parámetros opcionales con default debería llamarse por keyword, no
posicional, para evitar este tipo de errores silenciosos al cambiar la firma.
