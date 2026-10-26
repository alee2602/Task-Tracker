# Spec 001: Task Tracker MVP

Estado: IMPLEMENTADO
Plan: [plans/001-task-tracker-mvp-plan.md](../plans/001-task-tracker-mvp-plan.md)

## Problema

Necesito una forma simple de llevar tareas pendientes desde la línea de comandos,
sin depender de una app externa.

## Objetivo

Un CLI en Python que permita crear, listar, completar y eliminar tareas.

## Alcance (dentro)

- Agregar una tarea con un texto descriptivo.
- Listar tareas (pendientes y/o completadas).
- Marcar una tarea como completada.
- Eliminar una tarea.
- Persistencia entre ejecuciones (las tareas sobreviven a cerrar la terminal).

## Fuera de alcance (por ahora)

- Interfaz gráfica o web.
- Sincronización entre dispositivos / multi-usuario.
- Recordatorios o notificaciones.
- Fechas de vencimiento, etiquetas, subtareas (candidatos a spec 002 si se quieren después).
- Modo interactivo / menú (se usa interfaz de subcomandos, ver decisión).

## Decisiones ya tomadas (ver `decisions/`)

1. **Almacenamiento**: SQLite. Ver [decisions/001-storage-sqlite.md](../decisions/001-storage-sqlite.md).
2. **Interfaz de comandos**: subcomandos tipo `task add "..."`, `task list`, `task done 3`, `task rm 3`.
3. **Identificación de tareas**: ID numérico autoincremental (clave primaria de SQLite).
4. **Prioridad**: incluida en el MVP (alta/media/baja), asignable al crear la tarea.

## Criterios de aceptación

- [x] Puedo agregar una tarea (con prioridad) y verla en la lista.
- [x] Puedo marcar una tarea como completada y se refleja en la lista.
- [x] Puedo eliminar una tarea.
- [x] La lista muestra la prioridad de cada tarea.
- [x] Cierro la terminal, la vuelvo a abrir, y mis tareas siguen ahí (persisten en SQLite).

## Verificación

Verificado manualmente (ver checklist en el plan) + 5 tests automatizados en
`tests/test_db.py`, todos en verde.
