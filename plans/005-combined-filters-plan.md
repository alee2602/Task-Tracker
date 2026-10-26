# Plan 005: Filtro por prioridad y filtros combinados

Spec: [specs/005-combined-filters.md](../specs/005-combined-filters.md)

## Cambios en `db.py`

- `list_tasks(..., priority_filter: Optional[str] = None)` — parámetro nuevo al
  final de la firma. Si viene, agrega `AND t.priority = :priority_filter` al
  `WHERE` (misma técnica que `tag_filter`/`overdue_only`, se combina por `AND`
  con lo que ya exista).

## Cambios en `cli.py`

- `task list --priority <valor>`: valida contra `VALID_PRIORITIES` (mismo
  mensaje de error que `task add`) antes de llamar a `list_tasks`.

## Tests nuevos en `test_db.py`

1. `list_tasks(priority_filter="alta")` devuelve solo tareas de esa prioridad.
2. Combinar `priority_filter` + `tag_filter` → intersección correcta.
3. Combinar `priority_filter` + `overdue_only` → intersección correcta.

## Verificación manual (= criterios de aceptación del spec)

- [x] `task list --priority alta` muestra solo tareas de prioridad alta.
- [x] `task list --priority alta --tag casa` combina ambos filtros.
- [x] `task list --priority alta --overdue` combina ambos filtros.
- [x] `task list --priority invalida` da un error claro.
