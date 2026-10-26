# Spec 003: Subtareas

Estado: IMPLEMENTADO
Plan: [plans/003-subtasks-plan.md](../plans/003-subtasks-plan.md)

## Problema

Algunas tareas son en realidad varios pasos más pequeños (ej. "Organizar viaje" →
"Comprar boletos", "Reservar hotel"). Ahora mismo cada tarea es atómica, sin
forma de desglosarla.

## Objetivo

Permitir que una tarea tenga subtareas asociadas.

## Alcance (dentro)

- Crear una subtarea asociada a una tarea existente (`--parent <id>` en `task add`).
- Anidamiento ilimitado (una subtarea puede a su vez tener sus propias subtareas).
- Ver la jerarquía completa con `task list --tree` (vista indentada).
- `task list` (sin `--tree`) sigue siendo una lista plana, con una columna "Parent"
  que muestra el id del padre (o "-" si es una tarea raíz).
- Autocompletado hacia arriba: al completar la última subtarea pendiente de un padre,
  el padre se marca `done` automáticamente; esto se propaga hacia arriba en toda la cadena.
- Reapertura automática: si se agrega una subtarea nueva a un padre ya completado
  (en cualquier nivel), ese padre (y sus ancestros que se habían autocompletado) se
  reabren automáticamente.
- `task rm <id>` se bloquea con un mensaje claro si la tarea tiene subtareas
  (sin importar si están pendientes o completas); `task rm <id> --cascade` borra
  la tarea y todo su subárbol.
- Prioridad y etiquetas: cada subtarea tiene las suyas propias, independientes del padre.

## Fuera de alcance (por ahora)

- Mover una subtarea de un padre a otro.
- Combinar `--tree` con `--all`/`--tag` (la vista en árbol muestra siempre todo,
  pendiente y completo; los filtros solo aplican a la lista plana).

## Decisiones ya tomadas (ver `decisions/`)

Ver [decisions/004-subtasks-schema.md](../decisions/004-subtasks-schema.md) y
[decisions/005-subtask-autocomplete.md](../decisions/005-subtask-autocomplete.md).

## Criterios de aceptación

- [x] Puedo crear una subtarea asociada a una tarea existente, con su propia prioridad/etiquetas.
- [x] Puedo crear una sub-subtarea (nivel 2+) sin problema.
- [x] `task list --tree` muestra la jerarquía completa e indentada.
- [x] `task list` (plano) muestra la columna "Parent".
- [x] Al completar todas las subtareas de un padre, el padre se autocompleta.
- [x] Al agregar una subtarea nueva a un padre ya completado, el padre se reabre.
- [x] `task rm <id>` de una tarea con subtareas se bloquea con mensaje claro.
- [x] `task rm <id> --cascade` borra la tarea y todas sus subtareas descendientes.

## Verificación

Verificado manualmente (3 niveles de anidamiento, autocompletado/reapertura
propagados, borrado bloqueado y en cascada) + 10 tests nuevos en `test_db.py`
(21 en total), todos en verde.
