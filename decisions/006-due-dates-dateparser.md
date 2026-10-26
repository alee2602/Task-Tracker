# Decisión 006: Parseo de fechas con `dateparser`

Estado: ACEPTADA
Relacionado: [specs/004-due-dates.md](../specs/004-due-dates.md)

## Contexto

Las fechas de vencimiento deben aceptar tanto formato exacto (`2026-11-15`) como
expresiones relativas en lenguaje natural (`tomorrow`, `in 3 days`, `next friday`).
Opciones evaluadas:

- **Parser manual**: cubre un set fijo de patrones (`YYYY-MM-DD`, `today`,
  `tomorrow`, `Nd`, `Nw`). Cero dependencias nuevas, pero limitado y requiere
  mantenimiento propio si se quiere soportar más expresiones.
- **`dateparser`**: librería madura que interpreta lenguaje natural en varios
  idiomas ("next friday", "in 2 weeks", "15 de noviembre"), sin tener que escribir
  ni mantener la lógica de interpretación.

## Decisión

Usar `dateparser` para interpretar cualquier texto pasado a `--due`.

## Por qué

- Cobertura de expresiones mucho mayor sin esfuerzo de mantenimiento propio.
- Da margen a futuro (ej. soportar fechas en español) sin rediseñar el parseo.

## Consecuencias

- Nueva dependencia: `dateparser`.
- Fechas inválidas o no interpretables (`dateparser.parse()` devuelve `None`)
  deben manejarse con un error claro en el CLI, no dejar pasar `None` a la base
  de datos.
- La fecha se normaliza y guarda como `YYYY-MM-DD` (solo fecha, sin hora) en SQLite,
  para que el orden lexicográfico de la columna coincida con el orden cronológico.
