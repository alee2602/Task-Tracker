# Spec 004: Fechas de vencimiento

Estado: IMPLEMENTADO
Plan: [plans/004-due-dates-plan.md](../plans/004-due-dates-plan.md)

## Problema

No hay forma de indicar cuándo debe estar lista una tarea, ni de ver cuáles están
atrasadas.

## Objetivo

Permitir asignar una fecha de vencimiento opcional a una tarea y usarla para
ordenar/resaltar/filtrar en `task list`.

## Alcance (dentro)

- Asignar una fecha de vencimiento al crear una tarea (opcional), aceptando
  fecha exacta o expresiones relativas en lenguaje natural (`--due 2026-11-15`,
  `--due tomorrow`, `--due "in 3 days"`, `--due friday`, etc. vía `dateparser`,
  siempre resuelto hacia la próxima ocurrencia futura).
- Ver la fecha de vencimiento en `task list`.
- Resaltar visualmente las tareas atrasadas (vencidas y aún pendientes).
- La fecha de vencimiento es el criterio principal de orden en `task list`
  (lo más urgente primero; tareas sin fecha van al final); la prioridad queda
  como criterio secundario de desempate.
- Filtro `task list --overdue` (solo tareas vencidas y pendientes).
- Las subtareas pueden tener su propia fecha de vencimiento, independiente de
  la de su padre (sin herencia automática).

## Fuera de alcance (ya definido en spec 001, se reafirma aquí)

- Recordatorios o notificaciones activas (push, email, etc.) — solo visualización/orden.

## Decisiones ya tomadas (ver `decisions/`)

Ver [decisions/006-due-dates-dateparser.md](../decisions/006-due-dates-dateparser.md).

## Criterios de aceptación

- [x] Puedo crear una tarea con fecha de vencimiento exacta o relativa.
- [x] `task list` muestra la fecha de vencimiento de cada tarea, ordenada por urgencia.
- [x] Las tareas vencidas y pendientes se ven resaltadas/diferenciadas en la lista.
- [x] `task list --overdue` muestra solo tareas vencidas y pendientes.
- [x] Puedo asignar una fecha de vencimiento a una subtarea, distinta de la de su padre.

## Verificación

Verificado manualmente + 5 tests nuevos en `test_db.py` (26 en total), todos en
verde. Se encontró y corrigió un bug real de la librería `dateparser` (ver nota
en el plan): expresiones tipo "next friday" no se interpretaban, y los nombres
de día sueltos ("friday") devolvían la ocurrencia pasada en vez de la futura.
