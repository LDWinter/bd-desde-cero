# T17 — relacionar, desrelacionar y vecinos

**Estado:** [ ] pendiente · **Día 3** · **Archivo:** `back/relaciones.py` · **Depende de:** T15

## Qué
Manejar las aristas del grafo desde Python.

## Cómo
1. `relacionar(conn, origen, destino, tipo)`: INSERT; dejá que `sqlite3.IntegrityError` avise duplicados/lazos.
2. `desrelacionar`: DELETE de esa relación (acá sí es borrado real).
3. `vecinos(conn, nodo_id)`: reutilizá la consulta de T12.

## Herramientas
Python (`sqlite3`)

## Cumplido cuando
- [ ] Prueba manual OK.
- [ ] Una relación duplicada o un lazo lanza `IntegrityError`.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
