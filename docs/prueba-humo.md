# T39 — Prueba de humo

## Parte back (A, 15/10) — HECHA

Servidor real (`flask run` sobre una base nueva cargada con `semilla.py`), probado con `curl`.
Rutas de Oziel todavía con las copias provisionales de A (`rutas_auth_provisional.py`,
`rutas_fuentes_provisional.py` y la ruta de historial marcada PROVISIONAL en `rutas_nodos.py`).

| Pantalla del front | Llamadas | Resultado |
|---|---|---|
| Inicio (`DashboardPage`) | `GET /api/sources`, `GET /api/entities`, `GET /api/relationships` | 200 · 3 fuentes, 14 entidades, 15 relaciones |
| Fuentes (`SourcesPage`) | `GET /api/sources` | 200 · `recordCount` 3 / 11 / 0 (cuenta los nodos reales, no los números inventados del mock: 120 / 840 / 0) |
| Grafo (`GraphPage`) | `GET /api/entities`, `GET /api/relationships` | 200 |
| Entidad (`EntityPage`) | `GET /api/entities/cli-1`, `GET /api/entities/cli-1/history` | 200 · id inexistente → 404 |
| Login | `POST /api/auth/login`, `POST /api/auth/logout` | 200 / 204 |
| Crear / editar / borrar | `POST` y `PUT /api/entities`, `DELETE /api/entities/<id>` | 201 / 200 / 204 · la borrada da 404 · sin login → 401 |
| Relacionar | `POST` / `DELETE /api/relationships` | 201 / 204 · repetida → 409 · historial en los dos nodos |

Sin errores en el log del servidor. Tests: `.venv/bin/pytest back -q` → 46 OK.

### Avisos para quien conecta el front (no son errores del back)
1. Los ids de Producto y Pedido **no** son los del mock (Malbec: `pro-1` en el mock, `pro-5` en la API). Ver `INTEGRACION.md` §3.
2. `lastSync` y las fechas del historial vienen en ISO (`2026-10-05T10:32:00`); el mock muestra `05/10/2026 10:32`: formatear en el front.
3. No hay CORS: usar el proxy de Vite (`INTEGRACION.md` §5) para que la cookie de sesión funcione.

## Parte front (A+Oziel con la compañera de T37) — PENDIENTE
Cuando `api.ts` llame al back: levantar back (`flask --app app run` en `back/`) y front (`npm run dev`),
recorrer Inicio, Grafo y Entidad con F12 abierto y anotar cada error abajo.

| Pantalla | Qué hice | Qué pasó | Gravedad |
|---|---|---|---|
| | | | |
