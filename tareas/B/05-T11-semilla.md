# T11 — Semilla con los datos de los mocks

**Estado:** [x] completado · **Prioridad 5** · **Día 2** · **Archivo:** `back/semilla.py` · **Depende de:** T08, T10

## Qué
Cargar en la base los mismos datos que usa el front en sus mocks, para comparar respuestas después.

## Cómo
1. Copiá los datos de `src/mocks/data.ts`: 3 fuentes, 4 clientes, 4 productos, 6 pedidos y 15 relaciones.
2. Agregá 1 usuario de prueba (`prueba@local`, clave hasheada con `generate_password_hash`).
3. Respetá los ids del mock (`cli-1`, etc.) para que el JSON coincida.
4. Hacé que se pueda correr así: `python semilla.py base.db` (borra los datos y los vuelve a cargar).

## Herramientas
Python 3, `sqlite3`, `json`

## Cumplido cuando
- [x] `SELECT COUNT(*)` da 3 fuentes, 14 nodos y 15 relaciones (verificado 2026-10-14, también corriéndola 2 veces).
- [ ] Corriste `./respaldar.sh` e hiciste commit.
