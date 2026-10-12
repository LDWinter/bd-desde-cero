# T23 — registrar_usuario y verificar_clave

**Estado:** [ ] pendiente · **Prioridad 11** · **Día 4** · **Archivo:** `back/usuarios.py` · **Depende de:** T09, T13 (de A)

## Qué
Alta de usuarios con la clave hasheada y verificación al loguearse.

## Cómo
1. `registrar_usuario(conn, email, nombre, clave, rol='editor')` usa `generate_password_hash(clave)` de `werkzeug.security`.
2. `verificar_clave(conn, email, clave)` busca por email y usa `check_password_hash`; devuelve el usuario o `None`.
3. Nunca guardes ni devuelvas la clave en texto plano.

## Herramientas
Python 3, `werkzeug.security` (viene con Flask)

## Cumplido cuando
- [ ] En la base solo aparece el hash.
- [ ] `verificar_clave` acepta la buena y rechaza la mala.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
