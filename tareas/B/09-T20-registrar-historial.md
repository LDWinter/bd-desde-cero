# T20 — registrar() e historial_de()

**Estado:** [ ] pendiente · **Prioridad 9** · **Día 4 · Lun 12** · **Archivo:** `back/historial.py` · **Depende de:** T10, T13 (de A)

## Qué
Funciones para anotar un cambio y leer el historial de un nodo. A las necesita para T22 y T22b: prioridad alta.

## Cómo
1. `registrar(conn, nodo_id, usuario_id, accion, antes, despues)`: hace el INSERT con `json.dumps` en antes/después. **No** hace `commit` (lo hace quien la llama, para que todo vaya en la misma transacción).
2. `historial_de(conn, nodo_id)`: devuelve los cambios del nodo del más nuevo al más viejo (`ORDER BY fecha DESC, id DESC`).
3. Constante `HISTORIAL_MAX = 5` al principio del archivo.

## Herramientas
Python 3, `sqlite3`, `json`

## Cumplido cuando
- [ ] Prueba manual OK: registrar 2 cambios y verlos con `historial_de`.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
