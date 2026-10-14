# T16 — listar_nodos, editar_nodo y borrar_nodo

**Estado:** [x] completado · **Día 3** · **Archivo:** `back/nodos.py` · **Depende de:** T15

## Qué
Completar el CRUD de nodos.

## Cómo
1. `listar_nodos(conn, tipo=None)`: si viene `tipo`, filtrá con WHERE; si no, todos (menos los borrados).
2. `editar_nodo`: UPDATE de nombre y/o data; devolvé si encontró el nodo.
3. `borrar_nodo`: `UPDATE ... SET borrado = 1` (no DELETE).

## Herramientas
Python (`sqlite3`)

## Cumplido cuando
- [x] Prueba manual OK de las 3.
- [x] Un nodo borrado no aparece en `listar_nodos` ni en `obtener_nodo`.
- [x] Corriste `./respaldar.sh` e hiciste commit.
