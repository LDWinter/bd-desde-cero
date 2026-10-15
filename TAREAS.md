# Tareas — Backend de Knowledge System (base firme: jueves 15/10)

**Equipo backend:** **A** = Lautaro · **B** = compañero. El front lo hace otro compañero
(repo `NickSPC/Knowledge-System`, React + TypeScript).
**Código:** carpeta `back/` dentro de `bd-desde-cero`. **Respaldo:** `./respaldar.sh` al terminar **cada** tarea
(sube un .zip con fecha a Drive → `Base de datos desde cero/respaldos/`).

## Reglas
- Cada tarea dura entre 30 min y 2 h. Si una tarea pasa de 2 h, se avisa y se parte en dos.
- Antes de agarrar una tarea, poné tu inicial en la columna "Quién" y revisá que sus tareas previas ("Depende de") estén terminadas.
- Una tarea está **terminada** cuando se cumple su columna "Listo cuando" y se corrió `./respaldar.sh`.
- **Testing cruzado:** los tests de las funciones de A los escribe B, y los de las funciones de B los escribe A.
- Para no pisarse, cada uno trabaja en **sus** archivos (columna "Archivo"). Los archivos compartidos
  (`esquema.sql`, `app.py`) se tocan **de a uno**, avisando antes.
- El formato de datos lo define el front (`src/types.ts`). **No se cambian nombres de campos** sin hablar con el del front.

## Contrato con el front (resumen)
```ts
Entity       { id: string, type: "Cliente"|"Producto"|"Pedido", name, source, data: {clave: texto|número} }
Relationship { sourceId, targetId, type }
Source       { id, name, type, status: "ok"|"error", lastSync, recordCount }
```
Fechas en ISO (`2026-10-05T10:32:00`); las formatea el front. Historial corto: **cada nodo guarda sus últimos 5 cambios**, por separado (constante `HISTORIAL_MAX = 5`).
Se registra todo tipo de cambio: `crear`, `editar`, `borrar`, `relacionar` y `desrelacionar`. Una relación
cambia **dos** nodos, así que se registra en el historial de cada uno.

---

## Día 1 · Jue 8 – Vie 9 — Acuerdos y modelo
| # | Quién | Tarea | Archivo | Depende de | Listo cuando |
|---|---|---|---|---|---|
| T01 | A+B | Leer `src/types.ts` y `src/mocks/data.ts` del front y anotar las dudas | — | — | Hay una lista de dudas para el del front |
| T02 | A | DER con las 6 tablas: `tipos_nodo`, `fuentes`, `nodos`, `relaciones`, `usuarios`, `historial` | `docs/der.drawio.png` + `docs/modelo_relacional.md` | T01 | B lo revisó y lo aprobó |
| T03 | B | Contrato de la API: cada ruta con su método, el JSON que entra, el que sale y los errores | `docs/API.md` | T01 | El del front lo aprobó |
| T04 | B | Acordar con el del front: fechas ISO, ids en texto, login con cookie y proxy de Vite | `docs/API.md` | T03 | Queda anotado en API.md |
| T05 | A | Crear `back/`, el entorno virtual y `requirements.txt` (flask, pytest) | `back/` | — | `pytest` corre aunque haya 0 tests |

## Día 2 · Sáb 10 — Base de datos (SQL puro)
| # | Quién | Tarea | Archivo | Depende de | Listo cuando |
|---|---|---|---|---|---|
| T06 | A | `CREATE TABLE tipos_nodo` y `fuentes` (nombre, tipo, estado, última sincronización) | `back/esquema.sql` | T02 | El script se ejecuta 2 veces sin error |
| T07 | A | `CREATE TABLE nodos`: FK a tipo, fuente y usuario; `contenido` con `CHECK(json_valid)`; `borrado` | `back/esquema.sql` | T06 | Rechaza un JSON inválido y un tipo inexistente |
| T08 | A | `CREATE TABLE relaciones`: dos FK a nodos, `UNIQUE(origen,destino,tipo)`, `CHECK(origen<>destino)` | `back/esquema.sql` | T07 | Rechaza duplicados y lazos |
| T09 | B | `CREATE TABLE usuarios`: email UNIQUE, `hash_clave` y rol con CHECK | `back/esquema.sql` | T06 | Rechaza un email repetido |
| T10 | B | `CREATE TABLE historial` (nodo, usuario, acción, antes, después, fecha) + índice `(nodo_id, fecha)` | `back/esquema.sql` | T07, T09 | Se crea sin error |
| T11 | B | Semilla con **los mismos datos de los mocks**: 3 fuentes, 4 clientes, 4 productos, 6 pedidos y 15 relaciones, más 1 usuario de prueba | `back/semilla.py` | T08, T10 | Los conteos dan 3, 14 y 15 |
| T12 | A | Consultas de práctica: nodos con el nombre de su tipo (JOIN), vecinos de un nodo, cantidad por tipo | `back/consultas.sql` | T11 | Las 3 dan el resultado esperado sobre la semilla |

## Día 3 · Dom 11 — Python: repositorio de nodos y relaciones
| # | Quién | Tarea | Archivo | Depende de | Listo cuando |
|---|---|---|---|---|---|
| T13 | A | `conectar(ruta)` (con `foreign_keys=ON` y `row_factory`) y `crear_esquema(conn)` | `back/db.py` | T08 | Abre la base y crea las tablas |
| T14 | B | Fixture `conn` con la base en memoria + esquema + datos mínimos | `back/tests/conftest.py` | T13 | Un test vacío que usa `conn` pasa |
| T15 | A | `crear_nodo`, `obtener_nodo` | `back/nodos.py` | T13 | Prueba manual OK |
| T16 | A | `listar_nodos(tipo=None)`, `editar_nodo`, `borrar_nodo` (borrado lógico) | `back/nodos.py` | T15 | Prueba manual OK |
| T17 | A | `relacionar`, `desrelacionar`, `vecinos(nodo_id)` | `back/relaciones.py` | T15 | Prueba manual OK |
| T18 | B | Tests de T15 a T17: un caso que funciona y uno que falla por función | `back/tests/test_nodos.py`, `test_relaciones.py` | T14, T17 | `pytest` en verde |
| T19 | B | `a_entity(fila)` y `a_relationship(fila)`: pasan una fila de la base al formato del front | `back/formato.py` | T15 | El JSON es idéntico al del mock `cli-1` |

## Día 4 · Lun 12 — Historial y usuarios
| # | Quién | Tarea | Archivo | Depende de | Listo cuando |
|---|---|---|---|---|---|
| T20 | B | `registrar(conn, nodo_id, usuario_id, accion, antes, despues)` y `historial_de(nodo_id)` | `back/historial.py` | T10, T13 | Prueba manual OK |
| T21 | B | Purga: después de registrar, quedan solo los últimos `HISTORIAL_MAX` (5) **de ese nodo**, sin tocar los de otros nodos | `back/historial.py` | T20 | Con 8 cambios en el nodo 1 y 3 en el nodo 2, quedan 5 y 3 |
| T22 | A | Que crear, editar y borrar nodo registren en el historial **dentro de la misma transacción** | `back/nodos.py` | T16, T20 | Editar un nodo deja su "antes" y "después" |
| T22b | A | Que `relacionar` y `desrelacionar` registren el cambio en el historial de **los dos** nodos (misma transacción) | `back/relaciones.py` | T17, T20 | Al unir el nodo 1 con el 2, aparece en el historial de ambos |
| T23 | B | `registrar_usuario` (con hash, usando `werkzeug.security`) y `verificar_clave` | `back/usuarios.py` | T09, T13 | La clave nunca se guarda en texto plano |
| T24 | A | Tests de historial y usuarios: el tope de 5 por nodo, los 5 tipos de cambio y el rollback (si hay un error a mitad, no queda nada guardado) | `back/tests/test_historial.py`, `test_usuarios.py` | T21, T22, T22b, T23 | `pytest` en verde |

## Día 5 · Mar 13 — API: lectura y login
| # | Quién | Tarea | Archivo | Depende de | Listo cuando |
|---|---|---|---|---|---|
| T25 | B | `app.py`: Flask, conexión por request, errores en JSON (`{"error": ...}`) y `SECRET_KEY` | `back/app.py` | T13 | `flask run` levanta |
| T26 | A | `GET /api/entities` y `GET /api/entities/<id>` | `back/rutas_nodos.py` | T19, T25 | `curl` devuelve lo mismo que `getEntities()` del mock |
| T27 | A | `GET /api/relationships` | `back/rutas_nodos.py` | T26 | Igual a `getRelationships()` |
| T28 | B | `GET /api/sources` (con `recordCount` calculado contando nodos) | `back/rutas_fuentes.py` | T25 | Igual a `getSources()` |
| T29 | B | `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` (sesión con cookie) | `back/rutas_auth.py` | T23, T25 | Con `curl`, login → me → logout funciona |
| T30 | B | Decorador `@requiere_login` (401 si no hay sesión) | `back/rutas_auth.py` | T29 | Una ruta protegida da 401 sin login |

## Día 6 · Mié 14 — API: escritura y tests
| # | Quién | Tarea | Archivo | Depende de | Listo cuando |
|---|---|---|---|---|---|
| T31 | A | `POST /api/entities`: valida tipo, name y data, y devuelve 201 con la Entity | `back/rutas_nodos.py` | T22, T30 | Crea un nodo y aparece en el historial |
| T32 | A | `PUT` y `DELETE /api/entities/<id>` | `back/rutas_nodos.py` | T31 | 404 si no existe |
| T33 | A | `POST` y `DELETE /api/relationships` | `back/rutas_nodos.py` | T17, T30 | 409 si es un duplicado o un lazo |
| T34 | B | `GET /api/entities/<id>/history` | `back/rutas_nodos.py` (avisar a A) | T20, T26 | Devuelve como máximo 5 cambios de ese nodo, del más nuevo al más viejo |
| T35 | B | Tests de API para las rutas de A (T26, T27, T31 a T33) con `app.test_client()` | `back/tests/test_api_nodos.py` | T33 | Verde |
| T36 | A | Tests de API para las rutas de B (T28 a T30, T34) | `back/tests/test_api_auth.py` | T34 | Verde |

## Día 7 · Jue 15 — Integración: BASE FIRME
| # | Quién | Tarea | Archivo | Depende de | Listo cuando |
|---|---|---|---|---|---|
| T37 | A | Junto al del front: proxy `/api` → `localhost:5000` en `vite.config.ts` y cambiar el cuerpo de `api.ts` por `fetch` | repo del front | T27, T28 | El front muestra los datos de SQLite |
| T38 | B | `back/README.md`: cómo instalar, cargar la semilla, levantar y correr los tests | `back/README.md` | T36 | Un tercero lo puede levantar siguiendo el README |
| T39 | A+B | Prueba de humo: Inicio, Grafo y Entidad con el back real; anotar los errores encontrados | `docs/prueba-humo.md` | T37 | Sin errores bloqueantes |
| T40 | A+B | Respaldo final + marcar la versión "base firme" | — | T39 | El zip está en Drive |

## Después del jueves (Vie 16 – Lun 19) — para coordinar con el front
- Pantalla de login, formulario "agregar nodo / relación" y panel de historial en `/entidad/:id` (los hace el front y nosotros damos soporte).
- "Actividad reciente" del inicio alimentada por el historial (`GET /api/history?limit=10`).
- Grafo recursivo con `WITH RECURSIVE` (alcanzables desde un nodo).
- Más tests y la demo.

## Reparto de carga
- **A (Lautaro):** base de datos, nodos, relaciones, grafo e integración con el front: 20 tareas.
- **B (compañero):** contrato API, usuarios/login, historial, fuentes y API base: 18 tareas.
- **Compartidas:** T01, T39 y T40.
