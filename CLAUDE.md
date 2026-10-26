# Task Tracker — Reglas del proyecto

Proyecto práctico para aprender metodología de desarrollo asistido por IA
(spec-driven development): specs, decisiones registradas (ADRs), planes y ciclos trazables.

## Flujo de trabajo

Todo feature o cambio de alcance sigue este ciclo:

1. **Spec** (`specs/NNN-nombre.md`) — qué se quiere y por qué, antes de tocar código.
2. **Decisiones** (`decisions/NNN-nombre.md`) — cuando se toma una decisión técnica no trivial,
   se registra el porqué (no solo el qué).
3. **Plan** (`plans/NNN-nombre.md`) — pasos técnicos concretos para implementar el spec.
4. **Implementación** — código en `src/`, tests en `tests/`.
5. **Cierre** — el spec se marca como implementado; se referencia el plan y las decisiones usadas.

Numeración secuencial consistente entre specs/decisions/plans (001, 002, ...).

## Reglas para cualquier agente que trabaje aquí

- No implementar nada que no esté cubierto por un spec aprobado.
- No tomar decisiones de arquitectura "en silencio": si hay más de una opción razonable,
  se para y se registra como decisión (ADR) antes de seguir.
- No expandir el alcance de un spec sin decirlo explícitamente.
- Mantener specs y decisiones actualizados si la implementación diverge de lo planeado.
- No hacer commits ni agregar la co-autoría de Claude en los commits. Solo el usuario puede hacer los commits de manera manual. Debes decirle al usuario cuando ya puede hacer algún commit luego de haber finalizado una funcionalidad y puedes ayudarle a sugerir mensajes de commits en ingles.

## Stack

- Lenguaje: Python
- Almacenamiento, estructura de comandos y demás: a definir vía specs/decisions (no asumir).
