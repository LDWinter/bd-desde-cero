# Backend Knowledge System — Base de datos desde cero

Backend (SQLite + Python/Flask) para el front `NickSPC/Knowledge-System`. Trabajo en grupo: A = Lautaro, compañero: Oziel (GitHub Ozis02).

## Estructura
| Ruta | Qué hay |
|---|---|
| `TAREAS.md` | Reparto completo T01–T40 (fuente de verdad, se sube a Drive con el respaldo) |
| `tareas/A-archivo/` | Fichas de las tareas de A, **todas terminadas** (qué, cómo, herramientas, cumplido cuando) |
| `tareas/B/` | Tareas de Oziel (índice en `tareas/B/README.md`) |
| `back/` | Código del backend: `esquema.sql` (SQLite), módulos Python, `tests/`, `requirements.txt` |
| `docs/` | Diseño: DER (`der.drawio`, `der.drawio.png`) y modelo (`modelo_relacional.md`) |
| `docs/BACKEND.md` | **Documentación completa del back**: arquitectura, decisiones, quién hizo qué, cada tabla, función, ruta y test |
| `docs/INTEGRACION.md` | **Guía para conectar el front y el login**: rutas, ids, errores, equivalencias con `api.ts` |
| `respaldar.sh` | Sube un zip del proyecto a Drive (correr desde la raíz) |

## Arrancar
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r back/requirements.txt
python3 back/semilla.py back/base.db   # base con los datos de los mocks
pytest back -q && python3 back/probar_a.py
cd back && flask --app app run         # http://localhost:5000 (ver docs/INTEGRACION.md)
```
