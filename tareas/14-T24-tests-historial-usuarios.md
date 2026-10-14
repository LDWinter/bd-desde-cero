# T24 — Tests de historial y usuarios (código de B)

**Estado:** [x] completado · **Día 4** · **Archivo:** `back/tests/test_historial.py`, `back/tests/test_usuarios.py` · **Depende de:** T21, T22, T22b, T23

## Qué
Testing cruzado: probás las funciones de B.

## Cómo
1. Usá la fixture `conn` de B (`conftest.py`).
2. Historial: 8 cambios en el nodo 1 y 3 en el nodo 2 → quedan 5 y 3; los 5 tipos de acción; rollback ante error.
3. Usuarios: la clave no se guarda en texto plano; `verificar_clave` acepta la buena y rechaza la mala.
4. Un test que funciona y uno que falla por función (`pytest.raises`).

## Herramientas
pytest

## Cumplido cuando
- [x] `pytest` en verde.
- [x] Corriste `./respaldar.sh` e hiciste commit.
