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
from nodos import borrar_nodo, crear_nodo, editar_nodo, listar_nodos, obtener_nodo
from relaciones import listar_relaciones
try:
    from rutas_auth import requiere_login  # T30 (B)
except ImportError:  # mientras B no suba rutas_auth.py, se usa la copia provisional
    from rutas_auth_provisional import requiere_login

bp = Blueprint("nodos", __name__)

TIPOS = ("Cliente", "Producto", "Pedido")
FUENTE_POR_DEFECTO = "Manual"  # si el front no manda "source"


def _error(mensaje, codigo):
    return jsonify({"error": mensaje}), codigo


def _validar_entity(datos):
    """Devuelve un mensaje de error, o None si el JSON es una Entity válida."""
    if not isinstance(datos, dict):
        return "se esperaba un objeto JSON"
    if datos.get("type") not in TIPOS:
        return f"type tiene que ser uno de {', '.join(TIPOS)}"
    if not isinstance(datos.get("name"), str) or not datos["name"].strip():
        return "name no puede estar vacío"
    data = datos.get("data", {})
    if not isinstance(data, dict):
        return "data tiene que ser un objeto"
    for clave, valor in data.items():
        # {clave: texto | número}; bool es un int en Python, por eso se excluye aparte
        if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
            return f"data.{clave} tiene que ser texto o número"
    source = datos.get("source", FUENTE_POR_DEFECTO)
    if not isinstance(source, str) or not source.strip():
        return "source tiene que ser un texto"
    return None


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


# ---- T27 ----
@bp.get("/api/relationships")
def get_relationships():
    return jsonify([a_relationship(fila) for fila in listar_relaciones(g.conn)])


# ---- T31 ----
@bp.post("/api/entities")
@requiere_login
def post_entity():
    datos = request.get_json(silent=True)
    problema = _validar_entity(datos)
    if problema:
        return _error(problema, 400)
    nodo_id = crear_nodo(
        g.conn, datos["type"], datos["name"].strip(), datos.get("source", FUENTE_POR_DEFECTO),
        datos.get("data", {}), g.usuario_id,
    )
    return jsonify(a_entity(obtener_nodo(g.conn, nodo_id))), 201


# ---- T32 ----
@bp.put("/api/entities/<entity_id>")
@requiere_login
def put_entity(entity_id):
    nodo_id = _id_valido(entity_id)
    if nodo_id is None or obtener_nodo(g.conn, nodo_id) is None:
        return _error("entidad no encontrada", 404)
    datos = request.get_json(silent=True)
    problema = _validar_entity(datos)
    if problema:
        return _error(problema, 400)
    editar_nodo(g.conn, nodo_id, g.usuario_id,
                nombre=datos["name"].strip(), data=datos.get("data", {}), tipo=datos["type"])
    return jsonify(a_entity(obtener_nodo(g.conn, nodo_id)))


@bp.delete("/api/entities/<entity_id>")
@requiere_login
def delete_entity(entity_id):
    nodo_id = _id_valido(entity_id)
    if nodo_id is None or not borrar_nodo(g.conn, nodo_id, g.usuario_id):
        return _error("entidad no encontrada", 404)
    return "", 204
