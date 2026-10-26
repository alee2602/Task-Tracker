# Spec 002: Etiquetas / categorías

Estado: IMPLEMENTADO
Plan: [plans/002-tags-plan.md](../plans/002-tags-plan.md)

## Problema

Con varias tareas acumuladas, cuesta agruparlas por tema (ej. "trabajo", "casa", "estudio").

## Objetivo

Permitir asociar etiquetas a las tareas y filtrar la lista por etiqueta.

## Alcance (dentro)

- Asignar una o más etiquetas a una tarea al crearla (`--tags casa,urgente`).
- Ver las etiquetas de cada tarea en `task list`.
- Filtrar `task list` por etiqueta (`--tag casa`).
- Agregar/quitar etiquetas a una tarea ya existente (`task tag <id> <etiqueta>` / `task untag <id> <etiqueta>`).

## Fuera de alcance (por ahora)

- Etiquetas predefinidas/administradas (cualquier texto libre sirve como etiqueta).
- Jerarquía de etiquetas (sub-categorías).
- Colores personalizados por etiqueta (se puede reusar el esquema de colores existente de prioridad, no uno nuevo).

## Decisiones ya tomadas (ver `decisions/`)

1. **Cardinalidad**: una tarea puede tener varias etiquetas (no excluyentes).
2. **Sintaxis al crear**: `task add "Pagar renta" --tags casa,urgente` (separado por comas).
3. **Edición posterior**: sí, se puede agregar/quitar etiquetas de una tarea existente.
4. **Filtro**: `task list --tag casa` muestra solo tareas con esa etiqueta.
5. **Almacenamiento**: esquema normalizado (tabla `tags` + tabla puente `task_tags`).
   Ver [decisions/003-tags-normalized-schema.md](../decisions/003-tags-normalized-schema.md).

## Criterios de aceptación

- [x] Puedo crear una tarea con una o más etiquetas.
- [x] `task list` muestra las etiquetas de cada tarea.
- [x] Puedo filtrar la lista por etiqueta.
- [x] Puedo agregar una etiqueta a una tarea existente.
- [x] Puedo quitar una etiqueta de una tarea existente.

## Verificación

Verificado manualmente (ver checklist en el plan) + 7 tests nuevos en
`tests/test_db.py` (11 en total), todos en verde.
