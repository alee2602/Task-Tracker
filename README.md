# Task Tracker

![CI](https://github.com/alee2602/Task-Tracker/actions/workflows/tests.yml/badge.svg)

Gestor de tareas por línea de comandos, escrito en Python con [Typer](https://typer.tiangolo.com/)
y SQLite. Proyecto práctico para aprender metodología de desarrollo asistido por IA
(specs, decisiones registradas, planes, ciclos trazables) — ver [Metodología](#metodología).

## Features

- Crear, listar, completar y eliminar tareas, con prioridad (`alta`/`media`/`baja`).
- Etiquetas múltiples por tarea, con filtro por etiqueta.
- Subtareas con anidamiento ilimitado, autocompletado y reapertura automática
  del padre, borrado seguro (bloqueado salvo `--cascade`).
- Fechas de vencimiento (exactas o en lenguaje natural), orden por urgencia,
  filtro de vencidas.
- Filtros combinables: prioridad + etiqueta + vencidas, todos a la vez.
- Persistencia en SQLite (`tasks.db`, local, sin servidor).

## Instalación

Requiere Python 3.9+.

```bash
git clone https://github.com/alee2602/Task-Tracker.git
cd Task-Tracker
pip install -e ".[dev]"
```

Esto instala el paquete en modo editable junto con `pytest` (dependencia de desarrollo)
y deja disponible el comando `task`. Si `task` no se reconoce en tu terminal, la
carpeta `Scripts` (Windows) o `bin` (Linux/Mac) de tu entorno de Python no está en el
`PATH`; como alternativa siempre puedes correr cualquier comando como
`python -m tasktracker.cli <comando>`.

## Uso

### Agregar tareas

```bash
task add "Comprar leche"
task add "Pagar renta" --priority alta --tags casa,urgente
task add "Entregar informe" --due tomorrow
task add "Pagar impuestos" --due 2026-11-15
task add "Reunión de equipo" --due "in 3 days"
```

Crear una subtarea (referencia al id de la tarea padre):

```bash
task add "Comprar boletos" --parent 1
task add "Elegir asiento" --parent 2   # anidamiento ilimitado
```

### Listar tareas

```bash
task list                                   # pendientes, orden por vencimiento y prioridad
task list --all                             # incluye completadas
task list --tag casa                        # filtra por etiqueta
task list --priority alta                   # filtra por prioridad
task list --overdue                         # solo vencidas y pendientes
task list --priority alta --tag casa        # filtros combinables (AND)
task list --tree                            # vista jerárquica indentada
```

### Completar y eliminar

```bash
task done 3                 # marca como completada (autocompleta al padre si aplica)
task rm 3                   # elimina; se bloquea si tiene subtareas
task rm 3 --cascade         # elimina la tarea y todas sus subtareas
```

### Etiquetas en tareas existentes

```bash
task tag 3 urgente          # agrega una etiqueta
task untag 3 urgente        # la quita
```

### Referencia rápida

| Comando | Descripción |
|---|---|
| `task add "<desc>" [--priority alta\|media\|baja] [--tags a,b] [--parent <id>] [--due <texto>]` | Crea una tarea o subtarea |
| `task list [--all] [--tag <t>] [--priority <p>] [--overdue] [--tree]` | Lista/filtra tareas |
| `task done <id>` | Marca como completada |
| `task rm <id> [--cascade]` | Elimina una tarea |
| `task tag <id> <etiqueta>` | Agrega una etiqueta |
| `task untag <id> <etiqueta>` | Quita una etiqueta |

## Desarrollo

```bash
pytest          # correr la suite de tests
```

Los tests corren automáticamente en GitHub Actions en cada push a `master` y en
cada Pull Request (ver badge arriba).

## Estructura del proyecto

```
src/tasktracker/
  db.py       # acceso a datos (SQLite), toda la lógica de negocio
  cli.py      # comandos de Typer, presentación
tests/
  test_db.py  # tests de la capa de datos
specs/        # qué se construye y por qué, por ciclo
decisions/    # decisiones técnicas registradas (ADRs)
plans/        # cómo se implementa cada spec
.github/workflows/  # CI
```

## Metodología

Cada feature de este proyecto se desarrolló siguiendo un ciclo documentado:
**spec → decisiones → plan → implementación → cierre**. Ver [CLAUDE.md](CLAUDE.md)
para las reglas completas del flujo de trabajo.

- `specs/` — qué se construye y por qué, con criterios de aceptación verificables.
- `decisions/` — ADRs: decisiones técnicas no triviales, con su razonamiento.
- `plans/` — el "cómo" técnico de cada spec (funciones, esquema, pasos).

Cada spec termina en estado `IMPLEMENTADO` con una sección de verificación
(tests automatizados + pruebas manuales), y cualquier divergencia encontrada
entre lo planeado y lo construido queda documentada ahí mismo.
