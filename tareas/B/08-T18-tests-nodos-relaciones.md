# T18 — Tests de nodos y relaciones (código de A)

**Estado:** [ ] pendiente · **Prioridad 8** · **Día 3** · **Archivo:** `back/tests/test_nodos.py`, `back/tests/test_relaciones.py` · **Depende de:** T14, T17 (de A)

## Qué
Testing cruzado: probás las funciones de A.

## Cómo
1. Por cada función de T15 a T17 (`crear_nodo`, `obtener_nodo`, `listar_nodos`, `editar_nodo`, `borrar_nodo`, `relacionar`, `desrelacionar`, `vecinos`): un caso que funciona y uno que falla.
2. Casos que fallan: tipo inexistente, JSON inválido, relación duplicada, lazo (origen = destino) → `pytest.raises(sqlite3.IntegrityError)`.
3. Usá la fixture `conn` de T14.

## Herramientas
pytest

## Cumplido cuando
- [ ] `pytest` en verde.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
