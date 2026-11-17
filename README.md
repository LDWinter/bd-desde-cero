# Knowledge System — backend

Backend (SQLite + Python/Flask) del front Knowledge System (repositorio `NickSPC/Knowledge-System`, React + TypeScript).
Guarda entidades de cualquier tipo, las relaciones entre ellas (un grafo), las fuentes de donde salieron y el
historial de cambios, y lo sirve con una API HTTP/JSON.

## Estructura
| Ruta | Qué hay |
|---|---|
| `back/` | Código del backend: `esquema.sql`, módulos Python, `tests/`, `requirements.txt` |
| `paquete/` | Versión para correr en cualquier PC con solo Python: `armar.sh` arma `KnowledgeSystem.zip` (este back + el front compilado) |
| `docs/BACKEND.md` | Cómo está armado el back: capas, decisiones, archivos, paquete y pruebas |
| `docs/INTEGRACION.md` | **Referencia de la API**: cada ruta con lo que recibe, lo que devuelve y sus errores |
| `docs/modelo_relacional.md` | Las 6 tablas; diagrama en `docs/der.drawio` y `docs/der.drawio.png` |
| `docs/ejemplo-*.json` | Archivos de ejemplo para `POST /api/import`; `docs/guion-ejemplo-obras.md` explica el de obras |
| `respaldar.sh` | Sube un zip del proyecto a Drive (necesita `rclone` configurado) |

## Arrancar
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r back/requirements.txt
python3 back/semilla.py back/base.db   # base con datos de ejemplo y el usuario prueba@local / prueba123
pytest back -q && python3 back/probar_a.py   # 86 tests y "TODO OK"
cd back && flask --app app run         # http://localhost:5000 (rutas en docs/INTEGRACION.md)
```
