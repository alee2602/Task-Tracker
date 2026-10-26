# Decisión 002: CLI con Typer

Estado: ACEPTADA
Relacionado: [specs/001-task-tracker-mvp.md](../specs/001-task-tracker-mvp.md)

## Contexto

El spec pide una interfaz de subcomandos (`task add`, `task list`, `task done`, `task rm`).
Opciones evaluadas:

- **`argparse`**: incluido en Python, cero dependencias, pero más código repetitivo
  para declarar subcomandos y ayuda.
- **`click`**: maduro, muy usado en producción, basado en decoradores.
- **`typer`**: basado en `click`, usa type hints de Python como fuente de verdad
  (menos código), genera `--help` con buen formato, se integra con `rich` para
  salida con colores/tablas.

## Decisión

Usar **Typer** como librería de CLI.

## Por qué

- Código más corto y legible: los parámetros del comando se definen con type hints,
  no con configuración aparte.
- Mejor experiencia de usuario de entrada (ayuda autogenerada, validación de tipos).
- Es la opción que mejor equilibra "simple de mantener" con "se ve bien" para este proyecto práctico.

## Consecuencias

- Nueva dependencia: `typer` (y opcionalmente `rich` para tablas con color, que typer
  ya trae como dependencia opcional).
- Se necesita un `requirements.txt` (o `pyproject.toml`) para declarar la dependencia.
