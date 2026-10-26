# Spec 005: Filtro por prioridad y filtros combinados

Estado: IMPLEMENTADO
Plan: [plans/005-combined-filters-plan.md](../plans/005-combined-filters-plan.md)

## Problema

`task list` ya permite filtrar por etiqueta (`--tag`) y por vencidas (`--overdue`),
y estos dos ya se combinan entre sí (son condiciones `AND` independientes desde
el ciclo 004). Lo que falta es poder filtrar también por **prioridad**, y
confirmar que los cuatro filtros (`--tag`, `--overdue`, `--priority`, `--all`)
se puedan usar juntos en cualquier combinación.

## Objetivo

Agregar `task list --priority <alta|media|baja>`, combinable con los filtros
existentes.

## Alcance (dentro)

- `task list --priority alta` muestra solo tareas de esa prioridad.
- Combinable con `--tag`, `--overdue` y `--all` simultáneamente
  (ej. `task list --priority alta --tag casa --overdue`).
- Validar que el valor de `--priority` sea uno de `alta/media/baja` (mismo
  mensaje de error que ya usa `task add`).

## Fuera de alcance

- Múltiples valores en un mismo filtro (ej. `--priority alta,media`).
- Filtros combinados en `--tree` (ya fuera de alcance desde el spec 003).

## Decisiones

Ninguna decisión de arquitectura nueva: se reutiliza el mismo patrón de
`AND` ya usado para `tag_filter`/`overdue_only` en `list_tasks`. No se necesita ADR.

## Criterios de aceptación

- [x] `task list --priority alta` muestra solo tareas de prioridad alta.
- [x] `task list --priority alta --tag casa` combina ambos filtros (AND).
- [x] `task list --priority alta --overdue` combina ambos filtros (AND).
- [x] `task list --priority invalida` muestra un error claro, no una lista vacía silenciosa.

## Verificación

Verificado manualmente + 3 tests nuevos en `test_db.py` (29 en total), todos en
verde. Sin divergencias del plan.
