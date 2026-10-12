# T09 — CREATE TABLE usuarios

**Estado:** [ ] pendiente · **Prioridad 3** · **Día 2 · Sáb 10** · **Archivo:** `back/esquema.sql` (avisar a A antes de tocarlo) · **Depende de:** T06

## Qué
Crear la tabla de usuarios del sistema.

## Cómo
1. Columnas: `id INTEGER PRIMARY KEY`, `email TEXT NOT NULL UNIQUE`, `nombre TEXT`, `hash_clave TEXT NOT NULL`, `rol TEXT NOT NULL CHECK(rol IN ('admin','editor','lector'))`, `creado TEXT DEFAULT (datetime('now'))`.
2. Usá `CREATE TABLE IF NOT EXISTS` para que el script se pueda correr dos veces.
3. Probá en `sqlite3 :memory:`: insertá dos usuarios con el mismo email y verificá que el segundo falla.

## Herramientas
SQLite (`sqlite3` o DB Browser for SQLite), SQL

## Cumplido cuando
- [ ] Rechaza un email repetido.
- [ ] Rechaza un rol que no está en la lista.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
