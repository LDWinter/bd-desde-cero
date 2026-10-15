# T33 — POST y DELETE /api/relationships

**Estado:** [x] completado · **Día 6** · **Archivo:** `back/rutas_nodos.py` · **Depende de:** T17, T30 (B)

## Qué
Crear y quitar relaciones desde el front.

## Cómo
1. POST con `{sourceId, targetId, type}` → `relacionar` → 201.
2. Atrapá `sqlite3.IntegrityError` y devolvé **409**.
3. DELETE: `desrelacionar`; 404 si no existía.

## Herramientas
Flask, curl

## Cumplido cuando
- [x] 409 si es un duplicado o un lazo.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
