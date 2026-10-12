# T29 — Login, logout y me

**Estado:** [ ] pendiente · **Prioridad 13** · **Día 5** · **Archivo:** `back/rutas_auth.py` · **Depende de:** T23, T25

## Qué
Rutas de sesión con cookie.

## Cómo
1. `POST /api/auth/login` recibe `{email, password}`, usa `verificar_clave`; si está bien guarda `session['usuario_id']` y devuelve el usuario (sin hash); si no, 401.
2. `POST /api/auth/logout` hace `session.clear()`.
3. `GET /api/auth/me` devuelve el usuario logueado o 401.
4. Probalo con `curl -c cookies.txt` y `curl -b cookies.txt`.

## Herramientas
Flask (`session`), curl

## Cumplido cuando
- [ ] Con curl, login → me → logout funciona.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
