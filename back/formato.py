# T19 (B) — a_entity(fila) y a_relationship(fila): de una fila de la base al formato del front
# PROVISIONAL: lo escribió A (14/10) siguiendo tareas/B/07, para poder probar T26 y T27.
# B: revisalo y reemplazalo por tu versión si querés; mantené los mismos nombres.
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
