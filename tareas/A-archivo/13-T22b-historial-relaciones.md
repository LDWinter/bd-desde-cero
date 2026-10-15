# T22b — Historial en relacionar/desrelacionar

**Estado:** [x] completado · **Día 4** · **Archivo:** `back/relaciones.py` · **Depende de:** T17, T20 (Oziel)

## Qué
Una relación cambia dos nodos: se anota en el historial de los dos.

## Cómo
1. Llamá a `registrar` dos veces: una para el origen y otra para el destino.
2. Todo dentro del mismo `with conn:`.

## Herramientas
Python (`sqlite3`, transacciones)

## Cumplido cuando
- [x] Al unir el nodo 1 con el 2, el cambio aparece en el historial de ambos.
- [x] Corriste `./respaldar.sh` e hiciste commit.
