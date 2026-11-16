-- Cómo probarlas (desde la raíz del proyecto):
--   python3 back/semilla.py prueba.db
--   sqlite3 prueba.db ".headers on" ".mode column" ".read back/consultas.sql"

-- 1) Nodos con el nombre de su tipo.
-- Esperado: 14 filas, de "1 | Acme S.A. | Cliente" a "14 | Pedido #1006 | Pedido".
SELECT n.id, n.titulo, t.nombre AS tipo
FROM nodos n
JOIN tipos_nodo t ON t.id = n.tipo_id
WHERE n.borrado = 0
ORDER BY n.id;

-- 2) Vecinos del nodo 2 (Bodega Los Andes).
-- Esperado: 10 | Pedido #1002 y 11 | Pedido #1003, los dos con "pertenece a".
SELECT r.destino_id AS vecino_id, v.titulo, r.tipo
FROM relaciones r
JOIN nodos v ON v.id = r.destino_id
WHERE r.origen_id = 2 AND v.borrado = 0
UNION
SELECT r.origen_id, v.titulo, r.tipo
FROM relaciones r
JOIN nodos v ON v.id = r.origen_id
WHERE r.destino_id = 2 AND v.borrado = 0
ORDER BY vecino_id;

-- 3) Cantidad de nodos por tipo (sin contar los borrados).
-- Esperado: Cliente 4, Pedido 6, Producto 4.
SELECT t.nombre AS tipo, COUNT(*) AS cantidad
FROM nodos n
JOIN tipos_nodo t ON t.id = n.tipo_id
WHERE n.borrado = 0
GROUP BY t.nombre
ORDER BY t.nombre;
