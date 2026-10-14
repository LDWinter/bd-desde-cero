# Backend Knowledge System — Base de datos desde cero

Backend (SQLite + Python/Flask) para el front `NickSPC/Knowledge-System`. Trabajo en grupo: A = Lautaro, B = compañero.

## Estructura
| Ruta | Qué hay |
|---|---|
| `TAREAS.md` | Reparto completo T01–T40 (fuente de verdad, se sube a Drive con el respaldo) |
| `MIS-TAREAS.md` | Tareas de A, en orden, con enlaces a `tareas/` |
| `tareas/` | Un archivo por tarea de A (qué, cómo, herramientas, cumplido cuando) |
| `tareas/B/` | Tareas de B (índice en `tareas/B/README.md`) |
| `back/` | Código del backend: `esquema.sql` (SQLite), módulos Python, `tests/`, `requirements.txt` |
| `docs/` | Diseño: DER (`der.drawio`, `der.drawio.png`) y modelo (`modelo_relacional.md`) |
| `respaldar.sh` | Sube un zip del proyecto a Drive (correr desde la raíz) |

## Arrancar
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r back/requirements.txt
sqlite3 prueba.db < back/esquema.sql   # crea las tablas (se puede correr varias veces)
pytest back
```
