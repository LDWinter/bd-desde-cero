# Guía de integración — Backend Knowledge System

Para quien conecta el front (`NickSPC/Knowledge-System`) y para quien hace el login.
Todo lo que está acá está probado con `back/probar_a.py` y `pytest back` (fecha: 2026-10-15).

## 1. Levantar el backend

```bash
# desde la raíz del repo
python3 -m venv .venv && source .venv/bin/activate
pip install -r back/requirements.txt
cd back
python3 semilla.py base.db          # crea base.db con los datos de los mocks (se puede correr varias veces)
flask --app app run                  # → http://localhost:5000
```

- La base por defecto es `back/base.db`. Si no existe, `crear_app()` crea las tablas vacías (sin semilla).
- Usuario de prueba de la semilla: `prueba@local` / `prueba123` (rol `admin`).
- `SECRET_KEY`: en desarrollo usa una fija. Para cualquier otra cosa, `export SECRET_KEY=...` antes de `flask run`.
- Verificar que todo anda: `pytest back -q` (desde la raíz) y `python3 back/probar_a.py` (tiene que terminar en `TODO OK`).

## 2. Mapa del código (`back/`)

| Archivo | Quién | Qué hace |
|---|---|---|
| `esquema.sql` | A+Oziel | Las 6 tablas: `tipos_nodo`, `fuentes`, `nodos`, `relaciones`, `usuarios`, `historial`. Se puede correr varias veces. |
| `db.py` | A | `conectar(ruta)` (con `foreign_keys=ON` y filas tipo diccionario) y `crear_esquema(conn)`. |
| `semilla.py` | Oziel | Carga los datos de `src/mocks/data.ts`: 3 fuentes, 14 nodos, 15 relaciones y el usuario de prueba. |
| `app.py` | Oziel | La aplicación Flask: abre una conexión por request (`g.conn`), registra los blueprints y devuelve todos los errores como JSON. |
| `formato.py` | Oziel | Traduce filas de la base al JSON del front (`a_entity`, `a_relationship`) y los ids (`id_front`, `id_base`). |
| `nodos.py` | A | CRUD de nodos: `crear_nodo`, `obtener_nodo`, `listar_nodos`, `editar_nodo`, `borrar_nodo` (borrado lógico). Cada cambio queda en el historial en la misma transacción. |
| `relaciones.py` | A | `relacionar`, `desrelacionar`, `vecinos`. Cada cambio queda en el historial de **los dos** nodos. |
| `historial.py` | Oziel | `registrar` (guarda un cambio y deja solo los últimos 5 de ese nodo) e `historial_de`. |
| `usuarios.py` | Oziel | `registrar_usuario` (guarda solo el hash de la clave) y `verificar_clave`. |
| `rutas_nodos.py` | A | Las rutas `/api/entities` y `/api/relationships` (sección 4). |
| `rutas_auth_provisional.py` | A | Login **provisional** para poder probar. Lo reemplaza `rutas_auth.py` (sección 6). |
| `consultas.sql` | A | Consultas de práctica (T12). No las usa la app. |
| `probar_a.py` | A | Prueba manual completa de punta a punta. |
| `tests/` | A+Oziel | `pytest`: fixture `conn` (base en memoria) en `conftest.py`. |

## 3. Reglas del contrato (leer antes de conectar)

1. **Ids.** En la base los nodos tienen id entero; el front usa texto `"<prefijo>-<id de la base>"`:
   `cli` = Cliente, `pro` = Producto, `ped` = Pedido. Ej.: el nodo 5 de tipo Producto es `"pro-5"`.
   - Los números **no** coinciden con los del mock salvo en los clientes: el Malbec es `pro-1` en el mock y
     `pro-5` en la API; el pedido 1001 es `ped-1` en el mock y `ped-9` en la API. Para el front da igual
     porque los ids son opacos y las relaciones usan los mismos ids, pero **no hay que escribir ids a mano**.
   - Un id con el prefijo equivocado (`pro-1` para el Cliente 1) da 404.
   - Si un PUT cambia el `type`, cambia el prefijo del id (`cli-3` → `pro-3`): usar el id que devuelve el PUT.
2. **Errores.** Siempre JSON: `{"error": "mensaje en español"}` con el código HTTP que corresponda.
3. **Login.** Las rutas que escriben (POST, PUT, DELETE) piden sesión: sin login dan **401**. La sesión es una
   cookie de Flask; en `fetch` hay que mandar `credentials: "include"` (o usar el proxy de Vite, sección 5,
   que hace que todo sea del mismo origen).
4. **Borrado lógico.** Borrar una entidad la marca como borrada: deja de aparecer en todas las rutas y sus
   relaciones también dejan de aparecer (igual que hace el mock), pero la fila y su historial quedan.
5. **Historial.** Cada crear, editar, borrar, relacionar y desrelacionar se anota; se guardan los últimos 5
   cambios por nodo. La ruta para leerlo es `GET /api/entities/<id>/history` (T34: ya responde con una copia provisional de A; Oziel la puede reemplazar).

## 4. Rutas

### Entidades (`Entity` = `{id, type, name, source, data}`)

| Método y URL | Login | Recibe | Devuelve | Errores |
|---|---|---|---|---|
| `GET /api/entities` | no | opcional `?type=Cliente` | `200` lista de `Entity` (orden por id) | — |
| `GET /api/entities/<id>` | no | — | `200` `Entity` | `404` no existe / borrada / id mal formado |
| `POST /api/entities` | sí | `{type, name, source?, data?}` | `201` la `Entity` creada | `400` datos inválidos, `401` |
| `PUT /api/entities/<id>` | sí | `{type, name, source?, data?}` | `200` la `Entity` actualizada | `400`, `401`, `404` |
| `DELETE /api/entities/<id>` | sí | — | `204` sin cuerpo | `401`, `404` |

Validación de POST y PUT (si falla → `400` con el motivo):
- `type`: `"Cliente"`, `"Producto"` o `"Pedido"`.
- `name`: texto no vacío (se le sacan los espacios de los bordes).
- `data`: objeto `{clave: texto | número}`. Opcional: en POST queda `{}`; en PUT, si no viene, **no se toca** (los datos actuales se conservan).
- `source`: texto. Opcional: por defecto `"Manual"`. Si no existe esa fuente, se crea.

Ejemplo:
```bash
curl -s localhost:5000/api/entities/cli-1
# {"id":"cli-1","type":"Cliente","name":"Acme S.A.","source":"clientes_2025.xlsx",
#  "data":{"email":"contacto@acme.com","ciudad":"Córdoba"}}
```

### Relaciones (`Relationship` = `{sourceId, targetId, type}`)

| Método y URL | Login | Recibe | Devuelve | Errores |
|---|---|---|---|---|
| `GET /api/relationships` | no | — | `200` lista de `Relationship` (sin las de nodos borrados) | — |
| `POST /api/relationships` | sí | `{sourceId, targetId, type}` | `201` la `Relationship` creada | `400` falta `type`, `401`, `404` algún nodo no existe, `409` ya existe o es un lazo (un nodo consigo mismo) |
| `DELETE /api/relationships` | sí | `{sourceId, targetId, type}` (en el cuerpo) | `204` sin cuerpo | `400`, `401`, `404` no existe |

Ejemplo:
```bash
curl -s -X POST localhost:5000/api/relationships -b cookies.txt \
  -H 'Content-Type: application/json' -d '{"sourceId":"cli-1","targetId":"pro-5","type":"compró"}'
```

### Rutas de otras personas (ya responden con copias provisionales de A)
Mientras falte el archivo real, `app.py` usa `<nombre>_provisional.py`; cuando Oziel suba el suyo, se usa ese solo.
- `GET /api/sources` (T28, `rutas_fuentes.py`) → `[{id, name, type, status, lastSync, recordCount}]`, sin login.
- `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me` (T29/T30, `rutas_auth.py`): ver sección 6.
- `GET /api/entities/<id>/history` (T34) → hasta 5 `{accion, usuario, antes, despues, fecha}`, el más nuevo primero; 404 si no existe.

## 5. Conectar el front (T37)

1. **Proxy de Vite** en `vite.config.ts` (así el front y la API comparten origen y la cookie de sesión anda sola):
   ```ts
   export default defineConfig({
     plugins: [react()],
     server: { proxy: { "/api": "http://localhost:5000" } },
   })
   ```
2. **`src/services/api.ts`**: cambiar el cuerpo de cada función por un `fetch`. Equivalencias:

| Función del front | Llamada al back | Ojo |
|---|---|---|
| `getEntities()` | `GET /api/entities` | — |
| `getRelationships()` | `GET /api/relationships` | — |
| `getSources()` | `GET /api/sources` | Provisional de A (T28). `recordCount` cuenta los nodos reales; `lastSync` viene en ISO. |
| `createEntity(input)` | `POST /api/entities` con `{type, name}` y después **un** `POST /api/relationships` por cada id de `input.connectedIds` con `{sourceId: nueva.id, targetId, type: input.relationType}` | El back no recibe `connectedIds`: las relaciones se crean aparte. El mock agrega `data: {creado: fecha}`; el back deja `data: {}` salvo que se mande. |
| `updateEntity(id, {name, type})` | `PUT /api/entities/<id>` con `{name, type}` | `data` no se toca si no se manda. Si cambia el tipo, cambia el id: recargar entidades y relaciones. |
| `deleteEntity(id)` | `DELETE /api/entities/<id>` | Las relaciones del nodo desaparecen solas del `GET /api/relationships`. |

   Plantilla:
   ```ts
   async function api<T>(url: string, init?: RequestInit): Promise<T> {
     const r = await fetch(url, {
       credentials: "include",
       headers: { "Content-Type": "application/json" },
       ...init,
     });
     if (!r.ok) throw new Error((await r.json().catch(() => ({}))).error ?? r.statusText);
     return (r.status === 204 ? undefined : await r.json()) as T;
   }
   export const getEntities = () => api<Entity[]>("/api/entities");
   export const deleteEntity = (id: string) => api<void>(`/api/entities/${id}`, { method: "DELETE" });
   ```
3. Hasta que exista el login real, para probar las escrituras: ver sección 6.

## 6. Enchufar el login (T29/T30)

`app.py` registra automáticamente un archivo `back/rutas_auth.py` en cuanto exista. Tiene que:

1. Exponer un `Blueprint` llamado **`bp`** con nombre `"auth"`: `bp = Blueprint("auth", __name__)`.
2. Tener el decorador **`requiere_login`**: si no hay sesión → `401` con `{"error": ...}`; si hay, dejar el id
   del usuario en **`g.usuario_id`** (las rutas de nodos lo usan para el historial).
3. Usar `usuarios.verificar_clave(g.conn, email, clave)`: devuelve `{id, email, nombre, rol}` o `None`.
4. Cuando exista, cambiar en `rutas_nodos.py` el import
   `from rutas_auth_provisional import requiere_login` por `from rutas_auth import requiere_login`
   y borrar `rutas_auth_provisional.py`. `probar_a.py` usa el login real solo (detecta la ruta `auth.login`).

`rutas_auth_provisional.py` ya cumple ese contrato (login con `{email, password}`, logout y me) y sirve de
referencia. **Hoy `app.py` no lo registra**, así que con `flask run` las escrituras dan 401 hasta que esté
`rutas_auth.py`. Para probar el front antes, se puede copiar `rutas_auth_provisional.py` como `rutas_auth.py`
en la copia local (sin commitearlo).

## 7. Dudas abiertas para el front (T01)

1. `source` es el **nombre** de la fuente (texto), no su id. Si el front manda una fuente nueva, el back la crea.
2. `data` solo admite valores texto o número (sin anidados, sin listas, sin `true/false`).
3. Los ids no son los del mock (sección 3): ¿el front guarda ids en algún lado (URL, localStorage)? Si sí, se rompen.
4. `updateEntity` no devuelve la entidad, pero si cambia el tipo cambia el id: ¿conviene que devuelva la `Entity`?
5. `createEntity` crea las relaciones aparte: si una falla (409), la entidad ya quedó creada. ¿Se avisa o se ignora?
6. `Source.id` es número en `types.ts` (las entidades usan texto): confirmar con quien hace T28.
