# T06 — CREATE TABLE tipos_nodo y fuentes

**Estado:** [x] completado · **Día 2 · Sáb 10** · **Archivo:** `back/esquema.sql` · **Depende de:** T02

## Qué
Escribir en SQL las dos tablas más simples (no dependen de ninguna otra).

## Cómo
1. `tipos_nodo`: id y nombre único (Cliente, Producto, Pedido).
2. `fuentes`: id, nombre, tipo, estado (con `CHECK(estado IN ('ok','error'))`) y última sincronización (texto ISO).
3. Usá `CREATE TABLE IF NOT EXISTS` para que se pueda correr más de una vez.
4. Probalo: `sqlite3 prueba.db < back/esquema.sql`.

## Herramientas
SQL, sqlite3 / DB Browser

## Cumplido cuando
- [x] El script se ejecuta 2 veces seguidas sin error.
- [x] Un estado distinto de ok/error es rechazado.
- [x] Corriste `./respaldar.sh` e hiciste commit.
