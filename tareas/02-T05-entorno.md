# T05 — Crear el entorno de Python

**Estado:** [ ] pendiente · **Día 1** · **Archivo:** `back/requirements.txt`, `back/.venv/` · **Depende de:** —

## Qué
Dejar listo un Python aislado con las librerías del proyecto.

## Cómo
1. En `back/`: `python3 -m venv .venv` y `source .venv/bin/activate`.
2. Escribí en `requirements.txt` los dos paquetes que se usan (uno por línea).
3. `pip install -r requirements.txt` y después `pytest`.

## Herramientas
Terminal, venv, pip, pytest

## Cumplido cuando
- [ ] `pytest` corre aunque haya 0 tests (sale "no tests ran" sin errores de import).
- [ ] `.venv/` no se sube a git (ya está en `.gitignore`).
- [ ] Corriste `./respaldar.sh` e hiciste commit.

