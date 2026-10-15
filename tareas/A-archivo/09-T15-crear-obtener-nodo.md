# T15 — crear_nodo y obtener_nodo

**Estado:** [x] completado · **Día 3** · **Archivo:** `back/nodos.py` · **Depende de:** T13

## Qué
Las primeras funciones del repositorio de nodos.

## Cómo
1. `crear_nodo(conn, tipo, nombre, fuente, data)`: `json.dumps(data)` y un INSERT con parámetros `?` (nunca f-strings en SQL).
2. Devolvé el id nuevo (`cursor.lastrowid`).
3. `obtener_nodo(conn, id)`: SELECT que ignore los borrados; devuelve la fila o `None`.

## Herramientas
Python (`sqlite3`, `json`)

## Cumplido cuando
- [x] Prueba manual: creás un nodo y `obtener_nodo` lo devuelve igual.
- [x] Un id inexistente devuelve `None`.
- [x] Corriste `./respaldar.sh` e hiciste commit.
