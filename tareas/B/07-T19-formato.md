# T19 — a_entity y a_relationship

**Estado:** [ ] pendiente · **Prioridad 7** · **Día 3** · **Archivo:** `back/formato.py` · **Depende de:** T15 (de A)

## Qué
Funciones que pasan una fila de la base al JSON exacto que espera el front. Las usa A en T26, así que tienen prioridad.

## Cómo
1. `a_entity(fila)` → `{id, type, name, source, data}`; `data` viene de `json.loads(fila['contenido'])`; `type` es el nombre del tipo (no el id).
2. `a_relationship(fila)` → `{sourceId, targetId, type}`.
3. Compará con el mock `cli-1` campo por campo.

## Herramientas
Python 3, `json`

## Cumplido cuando
- [ ] El JSON de `cli-1` es idéntico al del mock.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
