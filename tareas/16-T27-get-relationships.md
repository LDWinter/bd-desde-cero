# T27 — GET /api/relationships

**Estado:** [x] completado · **Día 5** · **Archivo:** `back/rutas_nodos.py` · **Depende de:** T26

## Qué
El front recibe las aristas del grafo.

## Cómo
1. SELECT de todas las relaciones (de nodos no borrados) → `a_relationship` → `jsonify`.

## Herramientas
Flask, curl

## Cumplido cuando
- [x] La respuesta es igual a `getRelationships()` del mock.
- [x] Corriste `./respaldar.sh` e hiciste commit.
