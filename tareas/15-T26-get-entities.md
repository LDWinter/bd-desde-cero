# T26 — GET /api/entities y /api/entities/<id>

**Estado:** [x] completado · **Día 5 · Mar 13** · **Archivo:** `back/rutas_nodos.py` · **Depende de:** T19, T25 (B)

## Qué
Primeras rutas de la API: el front lee los nodos.

## Cómo
1. Creá un `Blueprint` y registralo en `app.py` de B (avisale).
2. Usá `listar_nodos` / `obtener_nodo` + `a_entity` de B y devolvé `jsonify(...)`.
3. 404 con `{"error": ...}` si el id no existe.

## Herramientas
Flask, curl

## Cumplido cuando
- [x] `curl localhost:5000/api/entities` devuelve lo mismo que `getEntities()` del mock.
- [x] Corriste `./respaldar.sh` e hiciste commit.
