# Para Oziel — lo que falta y con qué contás

Estado al 15/10/2026. La parte de A está terminada (fichas en `tareas/A-archivo/`). Este doc junta lo que te
queda, en orden, y para cada cosa qué ya está hecho para que no arranques de cero.

**Antes de empezar:** `git pull`, después `pytest back -q` (tiene que dar 48 passed) y
`python3 back/probar_a.py` (tiene que terminar en `TODO OK`). Cómo está armado todo: [`docs/BACKEND.md`](BACKEND.md).

## 1. Marcar lo que ya hiciste (5 minutos)
Tu código ya existe y sus tests pasan, pero las fichas siguen en `[ ]`. Marcalas `[x]` en `tareas/B/` y en
`tareas/B/README.md`:

| Tarea | Archivo | Lo prueba |
|---|---|---|
| T09 tabla usuarios, T10 tabla historial | `back/esquema.sql` | `test_usuarios.py`, `test_historial.py` |
| T14 fixture `conn` | `back/tests/conftest.py` | todos los tests |
| T18 tests de nodos y relaciones | `test_nodos.py`, `test_relaciones.py` | (son los tests) |
| T19 formato | `back/formato.py` | `test_api_auth.py`, `probar_a.py` |
| T20, T21 historial + purga | `back/historial.py` | `test_historial.py` |
| T23 usuarios | `back/usuarios.py` | `test_usuarios.py` |
| T25 app.py | `back/app.py` | todos los tests de API |

## 2. Rutas que hoy andan con copias de A (prioridad alta: las usa el front)
A dejó copias **provisionales** que cumplen tus fichas. `app.py` usa tu archivo apenas exista; mientras, usa la copia.
Podés **copiar la provisional como punto de partida**, revisarla y renombrarla.

| Tarea | Tenés que crear | Copia de referencia | Qué no puede cambiar (lo usa el front o los tests) |
|---|---|---|---|
| T29 login/logout/me + T30 `@requiere_login` | `back/rutas_auth.py` | `back/rutas_auth_provisional.py` | `bp = Blueprint("auth", ...)`, función `requiere_login` que deja `g.usuario_id`, login con `{email, password}`, 401 `{"error": ...}`. Detalle en `docs/INTEGRACION.md` §6 |
| T28 GET /api/sources | `back/rutas_fuentes.py` | `back/rutas_fuentes_provisional.py` | `{id (número), name, type, status ("ok"/"error"), lastSync ("dd/mm/aaaa hh:mm" o ""), recordCount}` |
| T34 GET /api/entities/<id>/history | (ya está en `back/rutas_nodos.py`, sección T34) | — | Revisala y, si te sirve, marcá T34. Si la cambiás, avisale a A (el archivo es de A) |

Cuando subas cada archivo: corré los tests (T36 ya prueba estas rutas: `tests/test_api_auth.py`) y avisale a A
para borrar la copia provisional.

## 3. T35 — tests de API de las rutas de A (`back/tests/test_api_nodos.py`)
Hoy esas rutas solo las prueba `probar_a.py`: pytest cubre el 56 % de `rutas_nodos.py`. Podés copiar el fixture
`cliente` y el login de `tests/test_api_auth.py`. Casos que conviene cubrir (todos ya funcionan, solo falta el test):

- `GET /api/entities` → 14 entidades; `?type=Pedido` → 6; `?type=Otro` → `[]`.
- `GET /api/entities/cli-1` → 200; `pro-1` (prefijo equivocado) → 404; `cli-99` → 404; `abc` → 404.
- `GET /api/relationships` → 15, con ids tipo `"ped-9"`.
- `POST /api/entities` → 201 y aparece en GET y en su history; 400 por: falta `type`, tipo inválido, `name` vacío,
  `data` que no es objeto, `data` con lista/bool/NaN, `source` vacío; 401 sin login.
- `PUT` → 200; sin `data` conserva los datos; cambiar `type` cambia el prefijo del id; 404 si no existe.
- `DELETE /api/entities/<id>` → 204; después GET → 404 y sus relaciones ya no salen en `/api/relationships`.
- `POST /api/relationships` → 201; duplicado → 409; lazo (mismo id) → 409; id inexistente → 404; sin `sourceId` → 400.
- `DELETE /api/relationships` → 204; repetirlo → 404.

## 4. Documentación
- **T03/T04 `docs/API.md`:** la información ya está en `docs/INTEGRACION.md` §3–4 y en `docs/BACKEND.md` §8 (cada
  ruta con entrada, salida y errores). Podés armar `API.md` a partir de ahí, o acordar con A que `INTEGRACION.md`
  cuente como T03.
- **T38 `back/README.md`:** el `README.md` de la raíz y `docs/BACKEND.md` §2 ya explican instalar, semilla, levantar
  y tests; alcanza con un README corto en `back/` que apunte ahí.

## 5. Con el resto del grupo
- **T37** (conectar el front): guía en `docs/INTEGRACION.md` §5.
- **T39 / T40:** prueba de humo con el front y respaldo "base firme", juntos.

## Dudas que hay que cerrar
- ¿El login (T29/T30) lo hacés vos o "otra compañera"? `TAREAS.md` te lo asigna a vos, pero en otras notas figura otra persona.
