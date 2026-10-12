# T22 — Historial en crear/editar/borrar nodo

**Estado:** [ ] pendiente · **Día 4 · Lun 12** · **Archivo:** `back/nodos.py` · **Depende de:** T16, T20 (B)

## Qué
Cada cambio de un nodo queda registrado, todo o nada.

## Cómo
1. Dentro de cada función, llamá a `registrar(...)` de B (`historial.py`) con `antes` y `despues` en JSON.
2. Usá `with conn:` para que el cambio y el registro estén en la **misma transacción** (commit o rollback juntos).
3. Para editar: leé el nodo antes del UPDATE para tener el "antes".

## Herramientas
Python (`sqlite3`, transacciones)

## Cumplido cuando
- [ ] Editar un nodo deja una fila de historial con su antes y después.
- [ ] Si `registrar` falla, el cambio del nodo tampoco queda.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
