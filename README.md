# Knowledge System — backend

Backend (SQLite + Python/Flask) del front Knowledge System (repositorio `NickSPC/Knowledge-System`, React + TypeScript).
Guarda entidades de cualquier tipo, las relaciones entre ellas (un grafo), las fuentes de donde salieron y el
historial de cambios, y lo sirve con una API HTTP/JSON.

## Estructura
| Ruta | Qué hay |
|---|---|
| `back/` | Código del backend: `esquema.sql`, módulos Python, `tests/`, `requirements.txt` |
| `iniciar.sh`, `Iniciar (Windows).bat` | **Levantan todo con un doble clic**: preparan Python la primera vez, crean la base y abren la app en el navegador (`iniciar.py`) |
| `web/` | El front ya compilado, que sirve `iniciar.py` |
| `paquete/` | `armar.sh <carpeta del front>` recompila el front en `web/` y arma `KnowledgeSystem.zip` para llevar a otra PC |
| `docs/BACKEND.md` | Cómo está armado el back: capas, decisiones, archivos, paquete y pruebas |
| `docs/INTEGRACION.md` | **Referencia de la API**: cada ruta con lo que recibe, lo que devuelve y sus errores |
| `docs/modelo_relacional.md` | Las 6 tablas; diagrama en `docs/der.drawio` y `docs/der.drawio.png` |
| `docs/ejemplo-*.json` | Archivos de ejemplo para `POST /api/import`; `docs/guion-ejemplo-obras.md` explica el de obras |
| `respaldar.sh` | Sube un zip del proyecto a Drive (necesita `rclone` configurado) |

## Arrancar
Para usarlo: doble clic en `Iniciar (Windows).bat` (Windows) o `./iniciar.sh` (Linux / macOS; también el acceso
directo `Knowledge System.desktop`). Hace falta Python 3 e internet la primera vez (instala Flask). Abre
`http://127.0.0.1:5001`; usuario `prueba@local`, clave `prueba123`. Los datos quedan en `datos/`.

Para desarrollar el back:
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r back/requirements.txt
python3 back/semilla.py back/base.db   # base con datos de ejemplo y el usuario prueba@local / prueba123
pytest back -q && python3 back/probar_a.py   # 89 tests y "TODO OK"
cd back && flask --app app run         # http://localhost:5000 (rutas en docs/INTEGRACION.md)
```
