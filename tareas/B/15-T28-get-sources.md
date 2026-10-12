# T28 — GET /api/sources

**Estado:** [ ] pendiente · **Prioridad 15** · **Día 5** · **Archivo:** `back/rutas_fuentes.py` · **Depende de:** T25

## Qué
Listar las fuentes de datos como las muestra el front.

## Cómo
1. Consulta con `LEFT JOIN nodos` y `COUNT(nodos.id)` para calcular `recordCount` (sin contar los borrados).
2. Devolver `{id, name, type, status, lastSync, recordCount}`.

## Herramientas
Flask, SQL (LEFT JOIN, GROUP BY), curl

## Cumplido cuando
- [ ] `curl localhost:5000/api/sources` da lo mismo que `getSources()` del mock.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
