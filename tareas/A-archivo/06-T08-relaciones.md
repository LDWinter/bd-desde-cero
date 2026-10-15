# T08 — CREATE TABLE relaciones

**Estado:** [x] completado · **Día 2** · **Archivo:** `back/esquema.sql` · **Depende de:** T07

## Qué
Las aristas del grafo: une un nodo origen con un nodo destino.

## Cómo
1. Dos FK a `nodos`: `origen_id` y `destino_id`, más `tipo` (texto).
2. `UNIQUE(origen_id, destino_id, tipo)` evita duplicados.
3. `CHECK(origen_id <> destino_id)` evita lazos (un nodo unido consigo mismo).

## Herramientas
SQL, sqlite3

## Cumplido cuando
- [x] Insertar la misma relación 2 veces falla.
- [x] Relacionar un nodo consigo mismo falla.
- [x] Corriste `./respaldar.sh` e hiciste commit.
