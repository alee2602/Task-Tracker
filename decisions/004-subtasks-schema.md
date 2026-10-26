# Decisión 004: Esquema auto-referenciado para subtareas, borrado seguro

Estado: ACEPTADA
Relacionado: [specs/003-subtasks.md](../specs/003-subtasks.md)

## Contexto

Se necesita anidamiento ilimitado (tarea → subtarea → sub-subtarea → ...). Opciones:

- **Tabla separada `subtasks`**: duplica columnas de `tasks` (prioridad, etiquetas,
  done), y solo soporta un nivel sin rediseñar.
- **Columna auto-referenciada `parent_id` en la propia tabla `tasks`**: una tarea
  y una subtarea son "lo mismo" (misma estructura, prioridad, etiquetas propias);
  `parent_id` apunta a otra fila de `tasks`, o es `NULL` si es una tarea raíz.
  El anidamiento ilimitado sale gratis (una subtarea es solo una tarea con `parent_id`
  distinto de `NULL`, y puede a su vez ser el `parent_id` de otra).

Para el borrado seguro (no eliminar en cascada por accidente), se evaluó:

- Borrar manualmente verificando hijos antes de cada `DELETE` (lógica a mano, propensa
  a bugs si se olvida en algún punto de código).
- **Foreign key con `ON DELETE RESTRICT`**: SQLite rechaza el `DELETE` con
  `IntegrityError` si existen filas hijas, sin tener que acordarse de verificar
  manualmente. El cascada explícito (`--cascade`) se implementa aparte, recorriendo
  el árbol con una consulta recursiva y borrando de las hojas hacia la raíz.

## Decisión

- Agregar `parent_id INTEGER REFERENCES tasks(id) ON DELETE RESTRICT` a la tabla `tasks`.
- Usar `WITH RECURSIVE` (soportado nativo en SQLite) para consultas de árbol completo
  (listar descendientes, vista `--tree`, borrado en cascada).

## Por qué

- Una subtarea no es conceptualmente distinta de una tarea: misma prioridad, mismas
  etiquetas, mismo flujo de `done`/`rm`. Reusar la tabla evita duplicar toda la lógica
  de `db.py` para un segundo tipo de entidad.
- `ON DELETE RESTRICT` da protección contra pérdida de datos "gratis" a nivel de base
  de datos, sin depender de que cada función de borrado se acuerde de chequear hijos.

## Consecuencias

- Toda consulta que calcule "estado de un padre" o "todo el árbol" necesita
  `WITH RECURSIVE`, más compleja que un `SELECT` plano.
- Debe seguir habilitado `PRAGMA foreign_keys = ON` (ya se activa desde la decisión 003)
  para que `ON DELETE RESTRICT` tenga efecto.
