# T36 — Tests de API de las rutas de B

**Estado:** [ ] pendiente · **Día 6** · **Archivo:** `back/tests/test_api_auth.py` · **Depende de:** T34

## Qué
Testing cruzado: probás login, fuentes e historial por HTTP.

## Cómo
1. Fixture con `app.test_client()` y base en memoria.
2. login → me → logout; ruta protegida sin login da 401; `GET /api/sources` con `recordCount` correcto; historial con máximo 5 y del más nuevo al más viejo.

## Herramientas
pytest, Flask test_client

## Cumplido cuando
- [ ] `pytest` en verde.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
