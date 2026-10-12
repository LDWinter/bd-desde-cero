# T34 — GET /api/entities/<id>/history

**Estado:** [ ] pendiente · **Prioridad 16** · **Día 6 · Mié 14** · **Archivo:** `back/rutas_nodos.py` (avisar a A antes de tocarlo) · **Depende de:** T20, T26 (de A)

## Qué
Ruta para que el front muestre el panel de historial de un nodo.

## Cómo
1. Usá `historial_de(conn, id)`.
2. 404 si el nodo no existe.
3. Cada cambio: `{accion, usuario, antes, despues, fecha}` con fecha ISO.

## Herramientas
Flask, curl

## Cumplido cuando
- [ ] Devuelve como máximo 5 cambios de ese nodo, del más nuevo al más viejo.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
