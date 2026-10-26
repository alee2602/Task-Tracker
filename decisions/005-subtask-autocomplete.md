# Decisión 005: Autocompletado y reapertura automática de padres

Estado: ACEPTADA
Relacionado: [specs/003-subtasks.md](../specs/003-subtasks.md)

## Contexto

Si todas las subtareas de una tarea se completan, ¿la tarea padre se marca como
completada sola, o se deja manual? Autocompletar sin más genera un problema: si
luego se agrega una subtarea nueva a un padre ya marcado como completo (por
ejemplo, porque se había olvidado una), el padre queda "mintiendo" como terminado
con trabajo pendiente.

## Decisión

- Al marcar una subtarea como `done`, se revisa si *todas* las subtareas directas
  de su padre están `done`; si sí, el padre se marca `done` automáticamente, y esto
  se repite hacia arriba (el abuelo, el bisabuelo, etc., mientras se cumpla la condición).
- Al agregar una subtarea nueva a un padre que está `done`, el padre se marca de
  vuelta como no completado, y esto también se propaga hacia arriba por la misma cadena.
- Al eliminar una subtarea (sin `--cascade`, es decir, una subtarea hoja), también
  se revisa si esto deja a su padre con todas las subtareas restantes en `done`,
  autocompletando si corresponde.

## Por qué

- Resuelve el caso de "se me olvidó agregar una subtarea": como agregar una subtarea
  reabre al padre automáticamente, nunca queda un padre marcado completo con trabajo
  pendiente por mucho tiempo — se corrige solo en el momento en que se nota el olvido.
- Propagar hacia arriba (no solo un nivel) mantiene la jerarquía completa consistente
  sin que el usuario tenga que completar manualmente cada nivel.

## Consecuencias

- `mark_done` y `add_task` (cuando recibe `parent_id`) ya no son operaciones de una
  sola fila: disparan una cadena de actualizaciones hacia los ancestros.
- Marcar una tarea como `done` manualmente cuando tiene subtareas pendientes NO está
  bloqueado (se permite completar un padre aunque falten subtareas); el autocompletado
  solo actúa en sentido ascendente, nunca fuerza completar subtareas desde el padre.
