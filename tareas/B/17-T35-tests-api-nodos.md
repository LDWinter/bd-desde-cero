# T35 — Tests de API de las rutas de A

**Estado:** [ ] pendiente · **Prioridad 17** · **Día 6** · **Archivo:** `back/tests/test_api_nodos.py` · **Depende de:** T33 (de A)

## Qué
Testing cruzado: probás las rutas de A con el cliente de pruebas de Flask.

## Cómo
1. Fixture `cliente` con `crear_app(':memory:')` + semilla, y `app.test_client()`.
2. Rutas: T26, T27, T31, T32 y T33. Un caso bien y uno con error por ruta (404, 400, 401 sin login, 409 duplicado).
3. Para las rutas protegidas, hacer login primero con el cliente.

## Herramientas
pytest, `app.test_client()`

## Cumplido cuando
- [ ] `pytest` en verde.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
