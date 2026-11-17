# Referencia de la API — Backend Knowledge System

Todo lo que el front necesita para hablar con el back: cómo levantarlo, las reglas del contrato y cada ruta.
Cómo está hecho por dentro: [`BACKEND.md`](BACKEND.md). Tablas: [`modelo_relacional.md`](modelo_relacional.md).

## 1. Levantar el backend

```bash
# desde la raíz del repo
python3 -m venv .venv && source .venv/bin/activate
pip install -r back/requirements.txt
cd back
python3 semilla.py base.db          # crea base.db con datos de ejemplo (borra y recarga: se puede repetir)
flask --app app run                  # → http://localhost:5000
```

- La base por defecto es `back/base.db`. Si no existe, la app crea las tablas vacías (sin datos ni usuarios).
- Usuario de la semilla: `prueba@local` / `prueba123` (rol `admin`).
- `SECRET_KEY`: en desarrollo usa una fija que está en el código. Para cualquier otro uso,
  `export SECRET_KEY=...` antes de `flask run`.
- Si la base fue creada por una versión anterior (sin `AUTOINCREMENT` en `nodos.id`), al arrancar aparece un
  aviso en el log: conviene exportar los datos, borrar la base y volver a importarlos.
- Verificar: `pytest back -q` (desde la raíz; 86 tests) y `python3 back/probar_a.py` (termina en `TODO OK`).

## 2. Reglas del contrato

1. **Ids.** En la base los nodos tienen id entero; la API usa texto `"<prefijo>-<id de la base>"`.
   - Prefijos: `cli` = Cliente, `pro` = Producto, `ped` = Pedido. Cualquier otro tipo usa sus 3 primeras letras
     o números en minúscula (`Persona` → `per-7`, `Mi tipo` → `mit-15`); si no tiene ninguna, `nod`.
   - Los ids son opacos: no hay que armarlos a mano, se usan los que devuelve la API. En una URL van
     codificados (`encodeURIComponent`).
   - Un id con el prefijo equivocado (`pro-1` para el Cliente 1) da 404.
   - Si un PUT cambia el `type`, cambia el prefijo del id (`cli-1` → `pro-1`): usar el id que devuelve el PUT.
   - Los ids no se reutilizan: el de un nodo eliminado no vuelve a aparecer.
2. **Tipos libres.** `type` es cualquier texto de 1 a 40 caracteres; si el tipo no existe, se crea.
3. **Errores.** Siempre JSON: `{"error": "mensaje en español"}` con el código HTTP que corresponda.
4. **Login.** Las rutas que escriben (POST, PUT, DELETE) piden sesión: sin login dan **401**
   `{"error": "no autenticado"}`. Los GET no piden login. La sesión es una cookie de Flask: en `fetch` hay que
   mandar `credentials: "include"`, y conviene que el front y la API compartan origen (sección 4).
5. **Borrado lógico.** `DELETE /api/entities/<id>` marca la entidad como borrada: deja de aparecer en todas las
   rutas y sus relaciones también, pero la fila y su historial quedan en la base.
   `DELETE /api/sources/<id>` y `DELETE /api/data`, en cambio, borran de verdad.
6. **Historial.** Cada crear, editar, borrar, relacionar y desrelacionar se anota; se guardan los últimos 5
   cambios por nodo. Una relación se anota en el historial de sus dos nodos.
7. **Fechas.** En ISO (`2026-10-05T10:32:00`); las formatea el front.

## 3. Rutas

### Sesión

| Método y URL | Recibe | Devuelve | Errores |
|---|---|---|---|
| `POST /api/auth/login` | `{email, password}` | `200` `{id, email, nombre, rol}` | `400` falta algún dato o no es JSON, `401` email o clave incorrectos |
| `POST /api/auth/logout` | — | `204` sin cuerpo (aunque no haya sesión) | — |
| `GET /api/auth/me` | — | `200` `{id, email, nombre, rol}` | `401` sin sesión |

El email se compara sin espacios y en minúsculas. La respuesta nunca incluye la clave ni su hash.

### Entidades — `Entity` = `{id, type, name, source, data}`

| Método y URL | Login | Recibe | Devuelve | Errores |
|---|---|---|---|---|
| `GET /api/entities` | no | opcional `?type=Cliente` | `200` lista de `Entity` (orden por id) | — |
| `GET /api/entities/<id>` | no | — | `200` `Entity` | `404` no existe, está borrada o el id está mal formado |
| `POST /api/entities` | sí | `{type, name, source?, data?}` | `201` la `Entity` creada | `400` datos inválidos, `401` |
| `PUT /api/entities/<id>` | sí | `{type, name, data?}` | `200` la `Entity` actualizada | `400`, `401`, `404` |
| `DELETE /api/entities/<id>` | sí | — | `204` sin cuerpo | `401`, `404` no existe o ya estaba borrada |

Validación de POST y PUT (si falla → `400` con el motivo):
- `type`: texto de 1 a 40 caracteres (se le sacan los espacios de los bordes).
- `name`: texto no vacío (se le sacan los espacios de los bordes).
- `data`: objeto `{clave: texto | número}`, sin listas, objetos anidados, `true`/`false`, `NaN` ni `Infinity`.
  Opcional: en POST queda `{}`; en PUT, si no viene, **no se toca** (los datos actuales se conservan).
- `source`: nombre de la fuente (texto no vacío; se le sacan los espacios de los bordes). Opcional en POST:
  por defecto `"Manual"`; si esa fuente no existe, se crea. **PUT no cambia la fuente**: si viene `source`,
  se valida pero no se aplica.

```bash
curl -s localhost:5000/api/entities/cli-1
# {"id":"cli-1","type":"Cliente","name":"Acme S.A.","source":"clientes_2025.xlsx",
#  "data":{"email":"contacto@acme.com","ciudad":"Córdoba"}}
```

### Relaciones — `Relationship` = `{sourceId, targetId, type}`

| Método y URL | Login | Recibe | Devuelve | Errores |
|---|---|---|---|---|
| `GET /api/relationships` | no | — | `200` lista de `Relationship` (sin las de nodos borrados) | — |
| `POST /api/relationships` | sí | `{sourceId, targetId, type}` | `201` la `Relationship` creada | `400` falta `type` o algún id, `401`, `404` algún nodo no existe, `409` ya existe o une un nodo consigo mismo |
| `DELETE /api/relationships` | sí | `{sourceId, targetId, type}` (en el cuerpo) | `204` sin cuerpo | `400`, `401`, `404` algún nodo o la relación no existe |

```bash
curl -s -c cookies.txt -H 'Content-Type: application/json' \
  -d '{"email":"prueba@local","password":"prueba123"}' localhost:5000/api/auth/login
curl -s -b cookies.txt -H 'Content-Type: application/json' \
  -d '{"sourceId":"cli-1","targetId":"pro-5","type":"compró"}' localhost:5000/api/relationships
```

### Historial

`GET /api/entities/<id>/history` (sin login) → `200` con hasta 5 cambios, el más nuevo primero; `404` si la
entidad no existe.

```json
[{"accion": "editar", "usuario": "Usuario de prueba", "fecha": "2026-11-16T16:55:24",
  "antes":   {"name": "Acme S.A.", "type": "Cliente", "source": "clientes_2025.xlsx", "data": {"ciudad": "Córdoba"}},
  "despues": {"name": "Acme",      "type": "Cliente", "source": "clientes_2025.xlsx", "data": {"ciudad": "Córdoba"}}}]
```

- `accion`: `crear`, `editar`, `borrar`, `relacionar` o `desrelacionar`.
- `antes` / `despues`: foto de la entidad (`{name, type, source, data}`) o de la relación
  (`{sourceId, targetId, type}`, con ids de la API). `antes` es `null` al crear o relacionar; `despues`, al
  borrar o desrelacionar.
- `usuario`: nombre de quien hizo el cambio (o su email si no tiene nombre).
- Los datos cargados con `semilla.py` no tienen historial: empieza con el primer cambio hecho por la API.

`GET /api/history?limit=N` (login) → `200` con los últimos cambios de **todas** las entidades, el más nuevo
primero. `limit` es opcional: por defecto 10, entre 1 y 50. Cada cambio trae lo mismo que arriba más
`entityId` y `entityName` (la entidad afectada, aunque después se haya borrado). Una relación aparece dos veces,
una por cada nodo. Sin login, `401`.

### Fuentes — `Source` = `{id, name, type, status, lastSync, recordCount}`

| Método y URL | Login | Devuelve | Errores |
|---|---|---|---|
| `GET /api/sources` | no | `200` lista de `Source` | — |
| `DELETE /api/sources/<id>` | sí | `204`; borra la fuente, sus nodos, el historial y las relaciones de esos nodos | `401`, `404` no existe |

- `id` es un número (las entidades usan texto). `status` es `"ok"` o `"error"`.
- `lastSync`: fecha ISO, o `null` si nunca se sincronizó.
- `recordCount` se calcula contando los nodos no borrados de la fuente.
- Las fuentes que se crean solas (al mandar un `source` nuevo) quedan con `type: "Manual"`, `status: "ok"` y
  `lastSync: null`.

### Importar y vaciar

`POST /api/import` (login) carga entidades y relaciones desde un JSON, **todo o nada**:

```json
{"replace": false,
 "entities": [{"id": "ana", "type": "Persona", "name": "Ana", "source": "Importado", "data": {"edad": 29}}],
 "relationships": [{"sourceId": "ana", "targetId": "pro-3", "type": "trabaja en"}]}
```

- `entities[].id` es una referencia **local** del archivo (texto no vacío, única dentro del archivo). El resto
  de cada entidad se valida igual que en `POST /api/entities`; si no trae `source`, queda en `"Importado"`.
- `sourceId` / `targetId`: primero se buscan entre las referencias locales; si no están, se toman como id de
  una entidad que ya existe (`pro-3`).
- `replace` (opcional, `true` o `false`): con `true` se vacían los datos antes de importar, y las relaciones
  solo pueden unir entidades del archivo.
- Responde `201` `{"entities": n, "relationships": n, "ids": {"ana": "per-15"}}` (`ids` traduce cada referencia
  local al id definitivo).
- Ante cualquier error responde `400` `{"error": ...}` indicando dónde (`entities[1]: ...`,
  `relationships[0]: ...`) y no guarda nada. Sin login, `401`.
- Ejemplos listos para importar: `docs/ejemplo-import.json` (7 entidades, 7 relaciones),
  `docs/ejemplo-obras.json` (34 y 41; guion en `docs/guion-ejemplo-obras.md`) y
  `docs/ejemplo-obras-corregido.json` (36 y 41).

`DELETE /api/data` (login) → `204`. Vacía historial, relaciones, nodos y fuentes; no toca los usuarios ni la
lista de tipos.

## 4. Conectar el front

- **Mismo origen.** En desarrollo, el front usa el proxy de Vite para `/api` (`vite.config.ts`), así la cookie de
  sesión funciona sin configurar CORS. El back no envía cabeceras CORS.
- **Puerto.** `flask run` escucha en el 5000; el paquete (`paquete/iniciar.py`), en el 5001. El proxy tiene que
  apuntar al que corresponda.
- **Crear una entidad con conexiones.** El back no recibe las conexiones junto con la entidad: primero
  `POST /api/entities` y después un `POST /api/relationships` por cada una, con el id que devolvió el primero.
  Si una relación falla (por ejemplo `409`), la entidad ya quedó creada.
- **Después de un PUT que cambia el tipo** cambia el id: recargar entidades y relaciones.
- **Al borrar una entidad** sus relaciones desaparecen solas de `GET /api/relationships`.
