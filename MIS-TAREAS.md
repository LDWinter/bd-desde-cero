# Mis tareas (A = Lautaro) — Backend Knowledge System

Base firme: **jueves 15/10**. Fuente completa (con las de B): `TAREAS.md`.
Modo **aprendizaje**: vos escribís el código; Claude explica, revisa y corrige.
Al terminar cada tarea: se cumple "Listo cuando" → `./respaldar.sh` → commit → marcar `[x]` acá y en su archivo.
Cada tarea tiene su archivo en `tareas/` con **qué**, **cómo**, **herramientas** y **cumplido cuando**.

## Herramientas y lenguajes
| Para qué | Qué se usa |
|---|---|
| Diagrama de la base (DER) | **draw.io** (ya instalado) → exportar `docs/der.png` |
| Base de datos | **SQLite** + lenguaje **SQL** (CREATE TABLE, FK, CHECK, JOIN). Para mirarla: **DB Browser for SQLite** o `sqlite3` |
| Lógica del backend | **Python 3** con el módulo `sqlite3` (viene con Python) y `json` |
| API web | **Flask** (rutas, JSON, sesión con cookie) |
| Tests | **pytest** y `app.test_client()` de Flask |
| Probar la API a mano | **curl** |
| Entorno | **venv** (`python3 -m venv .venv`), **VS Code**, **Git** |
| Integración | Front en **React + TypeScript** con **Vite** (solo tocás `vite.config.ts` y `api.ts`) |

## Contrato con el front (no cambiar nombres)
```ts
Entity       { id: string, type: "Cliente"|"Producto"|"Pedido", name, source, data: {clave: texto|número} }
Relationship { sourceId, targetId, type }
```
Fechas ISO (`2026-10-05T10:32:00`). Historial: últimos 5 cambios **por nodo** (`HISTORIAL_MAX = 5`);
acciones `crear`, `editar`, `borrar`, `relacionar`, `desrelacionar` (una relación se anota en **los dos** nodos).

---

## Tareas (en orden)
- [ ] [T01 — Leer el contrato del front](tareas/01-T01-leer-contrato-front.md) · Día 1 · Jue 8 – Vie 9
- [ ] [T05 — Crear el entorno de Python](tareas/02-T05-entorno.md) · Día 1
- [ ] [T02 — DER de las 6 tablas](tareas/03-T02-der.md) · Día 1
- [ ] [T06 — CREATE TABLE tipos_nodo y fuentes](tareas/04-T06-tipos-y-fuentes.md) · Día 2 · Sáb 10
- [ ] [T07 — CREATE TABLE nodos](tareas/05-T07-nodos.md) · Día 2
- [ ] [T08 — CREATE TABLE relaciones](tareas/06-T08-relaciones.md) · Día 2
- [ ] [T12 — Consultas de práctica](tareas/07-T12-consultas.md) · Día 2
- [ ] [T13 — conectar() y crear_esquema()](tareas/08-T13-db.md) · Día 3 · Dom 11
- [ ] [T15 — crear_nodo y obtener_nodo](tareas/09-T15-crear-obtener-nodo.md) · Día 3
- [ ] [T16 — listar_nodos, editar_nodo y borrar_nodo](tareas/10-T16-listar-editar-borrar.md) · Día 3
- [ ] [T17 — relacionar, desrelacionar y vecinos](tareas/11-T17-relaciones.md) · Día 3
- [ ] [T22 — Historial en crear/editar/borrar nodo](tareas/12-T22-historial-nodos.md) · Día 4 · Lun 12
- [ ] [T22b — Historial en relacionar/desrelacionar](tareas/13-T22b-historial-relaciones.md) · Día 4
- [ ] [T24 — Tests de historial y usuarios (código de B)](tareas/14-T24-tests-historial-usuarios.md) · Día 4
- [ ] [T26 — GET /api/entities y /api/entities/<id>](tareas/15-T26-get-entities.md) · Día 5 · Mar 13
- [ ] [T27 — GET /api/relationships](tareas/16-T27-get-relationships.md) · Día 5
- [ ] [T31 — POST /api/entities](tareas/17-T31-post-entity.md) · Día 6 · Mié 14
- [ ] [T32 — PUT y DELETE /api/entities/<id>](tareas/18-T32-put-delete-entity.md) · Día 6
- [ ] [T33 — POST y DELETE /api/relationships](tareas/19-T33-post-delete-relationship.md) · Día 6
- [ ] [T36 — Tests de API de las rutas de B](tareas/20-T36-tests-api-auth.md) · Día 6
- [ ] [T37 — Conectar el front al back](tareas/21-T37-integracion-front.md) · Día 7 · Jue 15
- [ ] [T39 — Prueba de humo](tareas/22-T39-prueba-humo.md) · Día 7
- [ ] [T40 — Respaldo final y versión "base firme"](tareas/23-T40-respaldo-final.md) · Día 7

## Después del jueves (para coordinar)
- `GET /api/history?limit=10` para "Actividad reciente" · grafo recursivo con `WITH RECURSIVE` · más tests y demo.
