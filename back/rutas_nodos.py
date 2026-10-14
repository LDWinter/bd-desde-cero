# T26 — GET /api/entities y GET /api/entities/<id>   (igual a getEntities() del mock)
# T27 — GET /api/relationships   (igual a getRelationships())
# T31 — POST /api/entities (valida tipo, name, data; 201 con la Entity)
# T32 — PUT y DELETE /api/entities/<id> (404 si no existe)
# T33 — POST y DELETE /api/relationships (409 si duplicado o lazo)
# (B agrega T34: GET /api/entities/<id>/history)
from flask import Blueprint, g, jsonify, request

try:
    from formato import a_entity, a_relationship  # T19 (B)
except ImportError:  # mientras B no suba formato.py, se usa la copia provisional
    from formato_provisional import a_entity, a_relationship
from nodos import listar_nodos, obtener_nodo

bp = Blueprint("nodos", __name__)


def _error(mensaje, codigo):
    return jsonify({"error": mensaje}), codigo


def _id_valido(entity_id):
    """Los ids llegan como texto ('3'); devuelve el número o None si no es un id posible."""
    return int(entity_id) if entity_id.isdigit() else None


# ---- T26 ----
@bp.get("/api/entities")
def get_entities():
    tipo = request.args.get("type")  # opcional: /api/entities?type=Cliente
    return jsonify([a_entity(fila) for fila in listar_nodos(g.conn, tipo)])


@bp.get("/api/entities/<entity_id>")
def get_entity(entity_id):
    nodo_id = _id_valido(entity_id)
    fila = obtener_nodo(g.conn, nodo_id) if nodo_id is not None else None
    if fila is None:
        return _error("entidad no encontrada", 404)
    return jsonify(a_entity(fila))
