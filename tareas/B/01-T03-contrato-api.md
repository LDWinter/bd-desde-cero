# T03 — Contrato de la API

**Estado:** [ ] pendiente · **Prioridad 1** · **Día 1 · Jue 8 – Vie 9** · **Archivo:** `docs/API.md` · **Depende de:** T01

## Qué
Escribir la lista de todas las rutas que va a tener el back, para que el front y A sepan qué esperar. Es lo que más bloquea a los demás: va primero.

## Cómo
1. Tomá las rutas del plan: `GET/POST /api/entities`, `GET/PUT/DELETE /api/entities/<id>`, `GET /api/entities/<id>/history`, `GET/POST/DELETE /api/relationships`, `GET /api/sources`, `POST /api/auth/login`, `POST /api/auth/logout`, `GET /api/auth/me`.
2. Para cada una anotá: método, URL, JSON que entra, JSON que sale (con un ejemplo copiado del mock) y códigos de error (400, 401, 404, 409).
3. Usá los nombres de `src/types.ts` tal cual (`Entity`, `Relationship`, `Source`); los errores siempre como `{"error": "mensaje"}`.
4. Pasáselo al del front y anotá lo que pida cambiar.

## Herramientas
VS Code (Markdown), el repo del front (`src/types.ts`, `src/services/api.ts`)

## Cumplido cuando
- [ ] Están todas las rutas con entrada, salida y errores.
- [ ] El del front lo aprobó.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
