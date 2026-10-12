# T10 — CREATE TABLE historial

**Estado:** [ ] pendiente · **Prioridad 4** · **Día 2** · **Archivo:** `back/esquema.sql` (avisar a A) · **Depende de:** T07, T09

## Qué
Crear la tabla donde se guarda cada cambio de un nodo.

## Cómo
1. Columnas: `id`, `nodo_id` (FK a nodos), `usuario_id` (FK a usuarios), `accion` con `CHECK(accion IN ('crear','editar','borrar','relacionar','desrelacionar'))`, `antes TEXT`, `despues TEXT` (JSON, pueden ser NULL), `fecha TEXT NOT NULL DEFAULT (datetime('now'))`.
2. `CHECK(antes IS NULL OR json_valid(antes))` y lo mismo para `despues`.
3. Índice: `CREATE INDEX IF NOT EXISTS idx_historial_nodo_fecha ON historial(nodo_id, fecha);`

## Herramientas
SQLite, SQL

## Cumplido cuando
- [ ] Se crea sin error.
- [ ] Rechaza una acción que no está en la lista.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
