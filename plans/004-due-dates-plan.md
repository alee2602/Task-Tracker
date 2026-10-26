# Plan 004: Fechas de vencimiento

Spec: [specs/004-due-dates.md](../specs/004-due-dates.md)
Decisión: [decisions/006-due-dates-dateparser.md](../decisions/006-due-dates-dateparser.md)

## Dependencia nueva

- `dateparser` en `pyproject.toml`.

## Cambios de esquema (`db.py`)

- Columna nueva en `tasks`: `due_date TEXT` (formato `YYYY-MM-DD`, `NULL` si no tiene).
- Migración idempotente en `init_db()` igual que se hizo para `parent_id`
  (`PRAGMA table_info` + `ALTER TABLE ADD COLUMN` si falta).
- `Task` (dataclass): nuevo campo `due_date: Optional[str] = None`.

## Parseo (`cli.py`, no en `db.py` — el parseo es una preocupación de entrada de
usuario, `db.py` solo guarda strings `YYYY-MM-DD` ya validados)

- `parse_due_date(text: str) -> str`: usa `dateparser.parse(text)`; si devuelve
  `None`, lanza `ValueError("No se pudo interpretar la fecha: '<text>'")`;
  si tiene éxito, formatea a `YYYY-MM-DD` con `.strftime("%Y-%m-%d")`.

## Funciones modificadas en `db.py`

- `add_task(..., due_date: Optional[str] = None)` — parámetro nuevo al final de
  la firma (mismo patrón que `parent_id` en el ciclo 003).
- `list_tasks`: el `SELECT t.*` ya trae `due_date`, se agrega al construir cada
  `Task`. Cambia el `ORDER BY`: ahora es
  `due_date IS NULL (los que no tienen fecha van al final), due_date ASC,
  luego la prioridad como desempate`.
- `list_tasks(..., overdue_only: bool = False)` — nuevo parámetro al final:
  si es `True`, filtra `due_date < hoy AND done = 0`.

## Comandos en `cli.py`

- `task add "<desc>" --due "<texto>"` — parsea con `parse_due_date`, pasa el
  resultado a `add_task`.
- `task list --overdue` — nuevo flag, pasa `overdue_only=True` a `list_tasks`.
- Columna nueva "Due" en la tabla de `list`: muestra la fecha o "-" si no tiene;
  en rojo si está vencida y pendiente, en amarillo si vence hoy, normal si no.
- `task list --tree`: también muestra la fecha de vencimiento por nodo (si tiene).

## Pasos de implementación

1. Agregar `dateparser` a `pyproject.toml`, reinstalar con `pip install -e ".[dev]"`.
2. Columna `due_date` + migración en `init_db()`.
3. `add_task` con parámetro `due_date`, `Task` con el campo nuevo.
4. `list_tasks` con nuevo `ORDER BY` y filtro `overdue_only`.
5. `parse_due_date()` en `cli.py`, opción `--due` en `add`, manejo de error si
   no se puede interpretar.
6. Opción `--overdue` en `list`, columna "Due" con resaltado de color, también
   en la vista `--tree`.
7. Tests en `test_db.py`: tarea con fecha, orden por fecha antes que prioridad,
   filtro `overdue_only`, tarea sin fecha va al final del orden, subtarea con
   fecha propia distinta del padre.

## Verificación manual (= criterios de aceptación del spec)

- [x] `task add "Entregar informe" --due tomorrow` crea la tarea con fecha de mañana.
- [x] `task add "Pagar impuestos" --due 2026-01-15` crea la tarea con esa fecha exacta.
- [x] `task list` ordena primero por fecha (vencidas/más próximas primero).
- [x] Una tarea vencida y pendiente se ve resaltada (color) en la lista.
- [x] `task list --overdue` solo muestra tareas vencidas y pendientes.
- [x] Una subtarea puede tener fecha distinta a la de su tarea padre.

## Nota de implementación (divergencia del plan)

Al probar manualmente, `dateparser` 1.4.3 resultó tener dos comportamientos
problemáticos sin configuración adicional:

1. `dateparser.parse("next friday")` devuelve `None` (no lo interpreta), a
   pesar de ser el ejemplo que proponía el spec original.
2. `dateparser.parse("friday")` sin más devuelve el viernes **pasado**, no
   el próximo — lo opuesto a lo esperado para una fecha de vencimiento.

Se corrigió pasando `settings={"PREFER_DATES_FROM": "future"}` en
`parse_due_date()`, lo cual arregla (2) para cualquier nombre de día suelto.
Para (1), no hay combinación de settings que haga funcionar la frase exacta
"next <día>" en esta versión de la librería; se actualizó el spec para usar
`friday` (sin "next") como ejemplo soportado en vez de prometer una frase que
la librería no interpreta.
