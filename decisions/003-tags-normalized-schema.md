# Decisión 003: Esquema normalizado para etiquetas

Estado: ACEPTADA
Relacionado: [specs/002-tags.md](../specs/002-tags.md)

## Contexto

Una tarea puede tener varias etiquetas, y varias tareas pueden compartir la misma
etiqueta (relación muchos-a-muchos). Opciones evaluadas:

- **Columna de texto con comas** (`tags = "casa,urgente"` en la tabla `tasks`):
  simple de implementar, pero filtrar por etiqueta exacta requiere `LIKE` (propenso
  a falsos positivos, ej. "casa" vs "casamiento"), y quitar una etiqueta sin tocar
  las demás implica parsear y reescribir el string a mano.
- **Esquema normalizado** (tabla `tags` + tabla puente `task_tags`): cada etiqueta
  existe una sola vez, se relaciona con N tareas vía filas en `task_tags`. Filtrar,
  agregar y quitar son operaciones SQL directas (INSERT/DELETE en la tabla puente).

## Decisión

Usar esquema normalizado: tabla `tags(id, name UNIQUE)` + tabla puente
`task_tags(task_id, tag_id)`.

## Por qué

- Filtrar por etiqueta exacta es una consulta SQL simple y correcta (sin `LIKE`).
- Agregar/quitar una etiqueta de una tarea es una fila insertada/eliminada, no
  un string reconstruido.
- Evita etiquetas duplicadas por typos de mayúsculas/espacios si se normaliza el
  nombre al guardar (ej. todo en minúsculas, trim).

## Consecuencias

- Dos tablas nuevas en `tasks.db` en vez de una columna.
- `list_tasks` necesita un JOIN para traer las etiquetas de cada tarea.
- Al eliminar una tarea (`task rm`), se deben limpiar sus filas en `task_tags`
  (pero no las etiquetas en sí, que pueden seguir usándose en otras tareas).
