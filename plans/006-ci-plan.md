# Plan 006: CI con GitHub Actions

Spec: [specs/006-ci.md](../specs/006-ci.md)

## Archivo nuevo

`.github/workflows/tests.yml`:

- Trigger: `push` a `main` + `pull_request` (cualquier rama destino).
- Un solo job, Python 3.12, `ubuntu-latest`.
- Pasos: checkout → setup-python 3.12 → `pip install -e ".[dev]"` → `pytest`.

## Cambios en `README.md`

- Badge al inicio del archivo:
  `![CI](https://github.com/alee2602/Task-Tracker/actions/workflows/tests.yml/badge.svg)`

## Verificación

- [ ] El workflow es YAML válido (se valida al hacer push, GitHub lo parsea).
- [ ] Al hacer push, aparece una ejecución en la pestaña "Actions" del repo.
- [ ] El badge se ve en el README una vez que el workflow corrió al menos una vez.
