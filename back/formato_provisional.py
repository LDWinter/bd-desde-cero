# T19 (B) — a_entity(fila) y a_relationship(fila): de una fila de la base al formato del front
# COPIA PROVISIONAL de `formato.py` (tarea de B), escrita por A (14/10) siguiendo la ficha de B para poder probar
# las tareas de A. NO es el archivo de B: cuando B suba `formato.py`, el código de A usa el de B solo
# (import con respaldo) y esta copia se puede borrar. Mismos nombres de funciones que pide la ficha.
import json


def a_entity(fila):
    """Fila de nodos.SELECT_NODO → Entity {id, type, name, source, data}."""
    return {
        "id": str(fila["id"]),  # el front usa ids en texto
        "type": fila["tipo"],
        "name": fila["titulo"],
        "source": fila["fuente"],
        "data": json.loads(fila["contenido"]),
    }


def a_relationship(fila):
    """Fila de relaciones → Relationship {sourceId, targetId, type}."""
    return {
        "sourceId": str(fila["origen_id"]),
        "targetId": str(fila["destino_id"]),
        "type": fila["tipo"],
    }
