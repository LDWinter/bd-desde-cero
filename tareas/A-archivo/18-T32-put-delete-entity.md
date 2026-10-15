# T32 — PUT y DELETE /api/entities/<id>

**Estado:** [x] completado · **Día 6** · **Archivo:** `back/rutas_nodos.py` · **Depende de:** T31

## Qué
Editar y borrar nodos desde el front.

## Cómo
1. PUT: misma validación que POST → `editar_nodo` → 200 con la Entity.
2. DELETE: `borrar_nodo` → 204 (sin cuerpo).
3. Si el nodo no existe: **404**.

## Herramientas
Flask, curl

## Cumplido cuando
- [x] 404 si no existe.
- [x] Los dos cambios quedan en el historial.
- [x] Corriste `./respaldar.sh` e hiciste commit.
