# Decisión 001: Almacenamiento con SQLite

Estado: ACEPTADA
Relacionado: [specs/001-task-tracker-mvp.md](../specs/001-task-tracker-mvp.md)

## Contexto

El MVP necesita persistir tareas entre ejecuciones del CLI. Las opciones evaluadas:

- **Archivo JSON**: trivial de implementar, legible a simple vista, pero concurrencia y
  queries (filtrar por prioridad/estado) requieren lógica manual.
- **SQLite**: motor embebido, sin servidor ni Docker (archivo `.db` local), soportado
  nativo por Python (`sqlite3`), permite queries reales (filtros, orden) sin escribir
  esa lógica a mano.

## Decisión

Usar **SQLite**, archivo local `tasks.db` en la raíz del proyecto (ignorado por git).

## Por qué

- No agrega infraestructura (no requiere Docker ni proceso de servidor).
- Da espacio para crecer (spec 002 con filtros/fechas) sin rediseñar el almacenamiento.
- Es la elección estándar para CLIs de este tamaño en Python.

## Consecuencias

- `tasks.db` debe agregarse a `.gitignore` (datos del usuario, no del repo).
- El esquema de la tabla `tasks` se define en el plan de implementación (`plans/001-*.md`).
