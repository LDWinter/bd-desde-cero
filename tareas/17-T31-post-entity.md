# T31 — POST /api/entities

**Estado:** [x] completado · **Día 6 · Mié 14** · **Archivo:** `back/rutas_nodos.py` · **Depende de:** T22, T30 (B)

## Qué
Crear nodos desde el front.

## Cómo
1. Protegé la ruta con `@requiere_login` de B.
2. Validá `request.get_json()`: `type` en Cliente/Producto/Pedido, `name` no vacío, `data` es un objeto. Si no: 400.
3. Llamá a `crear_nodo` y devolvé la Entity con código **201**.

## Herramientas
Flask, curl

## Cumplido cuando
- [x] Crea un nodo y aparece en el historial.
- [x] Datos inválidos → 400; sin login → 401.
- [x] Corriste `./respaldar.sh` e hiciste commit.
