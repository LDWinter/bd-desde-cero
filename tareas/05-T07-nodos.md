# T07 — CREATE TABLE nodos

**Estado:** [ ] pendiente · **Día 2** · **Archivo:** `back/esquema.sql` · **Depende de:** T06

## Qué
La tabla central: cada Entity del front es una fila de `nodos`.

## Cómo
1. FK a `tipos_nodo`, a `fuentes` y a `usuarios` (quién lo creó).
2. `contenido TEXT CHECK(json_valid(contenido))` para guardar el `data`.
3. `borrado INTEGER NOT NULL DEFAULT 0` (borrado lógico).
4. Acordate: en SQLite las FK solo se aplican con `PRAGMA foreign_keys = ON;`.

## Herramientas
SQL, sqlite3

## Cumplido cuando
- [ ] Un INSERT con JSON inválido falla.
- [ ] Un INSERT con un tipo que no existe falla.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
