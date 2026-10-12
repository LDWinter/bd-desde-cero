# T21 — Purga del historial (tope de 5 por nodo)

**Estado:** [ ] pendiente · **Prioridad 10** · **Día 4** · **Archivo:** `back/historial.py` · **Depende de:** T20

## Qué
Que cada nodo guarde solo sus últimos 5 cambios, sin tocar los de otros nodos.

## Cómo
1. Al final de `registrar`, borrá los registros de **ese** `nodo_id` que no estén entre los 5 más nuevos:
2. `DELETE FROM historial WHERE nodo_id = ? AND id NOT IN (SELECT id FROM historial WHERE nodo_id = ? ORDER BY fecha DESC, id DESC LIMIT ?)`
3. Probalo: 8 cambios en el nodo 1 y 3 en el nodo 2.

## Herramientas
SQL (subconsulta con LIMIT), Python

## Cumplido cuando
- [ ] Con 8 cambios en el nodo 1 y 3 en el nodo 2, quedan 5 y 3.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
