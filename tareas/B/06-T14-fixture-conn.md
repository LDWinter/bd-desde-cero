# T14 — Fixture conn para los tests

**Estado:** [ ] pendiente · **Prioridad 6** · **Día 3 · Dom 11** · **Archivo:** `back/tests/conftest.py` · **Depende de:** T13 (de A)

## Qué
Una fixture de pytest que da una base en memoria lista para usar en todos los tests.

## Cómo
1. Usá `conectar(':memory:')` y `crear_esquema(conn)` de `db.py` (los hace A en T13).
2. Insertá datos mínimos: 1 tipo, 1 fuente, 1 usuario y 2 nodos.
3. `yield conn` y después `conn.close()`.
4. Escribí `test_vacio(conn)` que solo haga `assert conn`.

## Herramientas
pytest (fixtures)

## Cumplido cuando
- [ ] El test vacío que usa `conn` pasa con `pytest`.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
