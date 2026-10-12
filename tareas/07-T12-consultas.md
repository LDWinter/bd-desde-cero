# T12 — Consultas de práctica

**Estado:** [ ] pendiente · **Día 2** · **Archivo:** `back/consultas.sql` · **Depende de:** T11 (semilla de B)

## Qué
Practicar SELECT con JOIN y GROUP BY sobre los datos reales.

## Cómo
1. Nodos con el **nombre** de su tipo: `JOIN tipos_nodo`.
2. Vecinos de un nodo: los que están en `relaciones` como destino si él es origen, y al revés (pista: `UNION`).
3. Cantidad por tipo: `GROUP BY` + `COUNT(*)`, sin contar los borrados.

## Herramientas
SQL, DB Browser o sqlite3

## Cumplido cuando
- [ ] Las 3 consultas dan el resultado esperado sobre la semilla (4 clientes, 4 productos, 6 pedidos).
- [ ] Corriste `./respaldar.sh` e hiciste commit.
