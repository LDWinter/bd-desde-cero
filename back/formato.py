"""Filas de la base -> JSON del front. La regla de ids ('cli-1' <-> 1) vive solo aca."""
import json

PREFIJOS = {"Cliente": "cli", "Producto": "pro", "Pedido": "ped"}

SELECT_RELACION = """
    SELECT r.origen_id, t1.nombre AS origen_tipo,
           r.destino_id, t2.nombre AS destino_tipo,
           r.tipo
    FROM relaciones r
    JOIN nodos n1 ON n1.id = r.origen_id
    JOIN tipos_nodo t1 ON t1.id = n1.tipo_id
    JOIN nodos n2 ON n2.id = r.destino_id
    JOIN tipos_nodo t2 ON t2.id = n2.tipo_id
    WHERE n1.borrado = 0 AND n2.borrado = 0
    ORDER BY r.id
"""


def _prefijo(tipo):
    # Tipo nuevo: sus 3 primeras letras o numeros. Los signos se saltean: el tipo "A/B"
    # daba el id "a/b-1", que no se puede pedir por URL (la entidad quedaba inalcanzable).
    return PREFIJOS.get(tipo) or "".join(c for c in tipo if c.isalnum())[:3].lower() or "nod"


def id_front(tipo, nodo_id):
    """(Cliente, 1) -> 'cli-1'"""
    return f"{_prefijo(tipo)}-{nodo_id}"


def id_base(texto):
    """'cli-1' -> 1. Levanta ValueError si el id no tiene el formato esperado."""
    _, sep, numero = str(texto).rpartition("-")
    if not sep:
        raise ValueError(f"id con formato invalido: {texto!r}")
    numero = int(numero)
    if numero >= 2**63:  # SQLite no guarda enteros mas grandes: sin esto la consulta daba 500
        raise ValueError(f"id con formato invalido: {texto!r}")
    return numero


def a_entity(fila):
    return {
        "id": id_front(fila["tipo"], fila["id"]),
        "type": fila["tipo"],
        "name": fila["titulo"],
        "source": fila["fuente"],
        "data": json.loads(fila["contenido"]),
    }


def a_relationship(fila):
    return {
        "sourceId": id_front(fila["origen_tipo"], fila["origen_id"]),
        "targetId": id_front(fila["destino_tipo"], fila["destino_id"]),
        "type": fila["tipo"],
    }
