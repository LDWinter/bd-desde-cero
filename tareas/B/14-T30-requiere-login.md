# T30 — Decorador @requiere_login

**Estado:** [ ] pendiente · **Prioridad 14** · **Día 5** · **Archivo:** `back/rutas_auth.py` · **Depende de:** T29

## Qué
Proteger las rutas de escritura. A lo necesita para T31 y T33.

## Cómo
1. Decorador con `functools.wraps`: si no hay `session['usuario_id']`, devuelve `{"error": "no autenticado"}` con 401.
2. Guardá el usuario en `g.usuario_id` para que las rutas lo usen al registrar el historial.
3. Avisale a A cómo importarlo: `from rutas_auth import requiere_login`.

## Herramientas
Python (decoradores), Flask

## Cumplido cuando
- [ ] Una ruta protegida da 401 sin login y 200 con login.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
