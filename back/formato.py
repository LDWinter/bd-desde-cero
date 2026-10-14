"""T19 - Pasa filas de la base al formato JSON que espera el front.

a_entity(fila)       -> {id, type, name, source, data}
a_relationship(fila) -> {sourceId, targetId, type}

La base usa ids enteros y el front usa ids de texto ("cli-1"). La regla
para pasar de uno a otro vive solo en id_front() / id_base(), asi si el
equipo decide otra cosa (por ejemplo una columna id_externo) se cambia aca.
"""
import json

# Prefijo del id del front segun el tipo de nodo
PREFIJOS = {"Cliente": "cli", "Producto": "pro", "Pedido": "ped"}

# Consulta que arma las filas que espera a_relationship (para usar en T27).
# Igual que listar_relaciones de relaciones.py, pero agregando el tipo de cada extremo.
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
    # Si aparece un tipo nuevo, se usan sus 3 primeras letras
    return PREFIJOS.get(tipo, tipo[:3].lower())


def id_front(tipo, nodo_id):
    """(Cliente, 1) -> 'cli-1'"""
    return f"{_prefijo(tipo)}-{nodo_id}"


def id_base(texto):
    """'cli-1' -> 1. Levanta ValueError si el id no tiene el formato esperado."""
    _, sep, numero = str(texto).rpartition("-")
    if not sep:
        raise ValueError(f"id con formato invalido: {texto!r}")
    return int(numero)


def a_entity(fila):
    """Fila de nodo (id, tipo, fuente, titulo, contenido) -> Entity del front."""
    return {
        "id": id_front(fila["tipo"], fila["id"]),
        "type": fila["tipo"],  # el nombre del tipo, no su id
        "name": fila["titulo"],
        "source": fila["fuente"],
        "data": json.loads(fila["contenido"]),
    }


def a_relationship(fila):
    """Fila con origen_id, origen_tipo, destino_id, destino_tipo, tipo -> Relationship."""
    return {
        "sourceId": id_front(fila["origen_tipo"], fila["origen_id"]),
        "targetId": id_front(fila["destino_tipo"], fila["destino_id"]),
        "type": fila["tipo"],
    }
