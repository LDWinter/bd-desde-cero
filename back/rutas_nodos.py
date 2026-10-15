# T26 — GET /api/entities y GET /api/entities/<id>   (igual a getEntities() del mock)
# T27 — GET /api/relationships   (igual a getRelationships())
# T31 — POST /api/entities (valida tipo, name, data; 201 con la Entity)
# T32 — PUT y DELETE /api/entities/<id> (404 si no existe)
# T33 — POST y DELETE /api/relationships (409 si duplicado o lazo)
# Ids: el front usa "cli-1"; se traducen solo con formato.id_base()/id_front() (de B).
# (B agrega T34: GET /api/entities/<id>/history)
import sqlite3

from flask import Blueprint, g, jsonify, request

from formato import SELECT_RELACION, a_entity, a_relationship, id_base, id_front
from nodos import borrar_nodo, crear_nodo, editar_nodo, listar_nodos, obtener_nodo
from relaciones import desrelacionar, relacionar
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


def _buscar(entity_id):
    """Id del front ('cli-1') -> fila del nodo, o None si el id no es válido, no existe o el prefijo
    no coincide con el tipo ('pro-1' no encuentra al Cliente 1)."""
    try:
        fila = obtener_nodo(g.conn, id_base(entity_id))
    except ValueError:
        return None
    return fila if fila is not None and id_front(fila["tipo"], fila["id"]) == entity_id else None


# ---- T26 ----
@bp.get("/api/entities")
def get_entities():
    tipo = request.args.get("type")  # opcional: /api/entities?type=Cliente
    return jsonify([a_entity(fila) for fila in listar_nodos(g.conn, tipo)])


@bp.get("/api/entities/<entity_id>")
def get_entity(entity_id):
    fila = _buscar(entity_id)
    if fila is None:
        return _error("entidad no encontrada", 404)
    return jsonify(a_entity(fila))


# ---- T27 ----
@bp.get("/api/relationships")
def get_relationships():
    return jsonify([a_relationship(fila) for fila in g.conn.execute(SELECT_RELACION)])


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
    fila = _buscar(entity_id)
    if fila is None:
        return _error("entidad no encontrada", 404)
    nodo_id = fila["id"]
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
    fila = _buscar(entity_id)
    if fila is None or not borrar_nodo(g.conn, fila["id"], g.usuario_id):
        return _error("entidad no encontrada", 404)
    return "", 204


# ---- T33 ----
def _leer_relacion():
    """Valida {sourceId, targetId, type}. Devuelve (origen, destino, tipo, None) o (.., (mensaje, código))."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return None, None, None, ("se esperaba un objeto JSON", 400)
    tipo = datos.get("type")
    if not isinstance(tipo, str) or not tipo.strip():
        return None, None, None, ("type no puede estar vacío", 400)
    origen, destino = _buscar(str(datos.get("sourceId"))), _buscar(str(datos.get("targetId")))
    if origen is None or destino is None:
        return None, None, None, ("sourceId o targetId no existe", 404)
    return origen, destino, tipo.strip(), None


@bp.post("/api/relationships")
@requiere_login
def post_relationship():
    origen, destino, tipo, problema = _leer_relacion()
    if problema:
        return _error(*problema)
    try:
        relacionar(g.conn, origen["id"], destino["id"], tipo, g.usuario_id)
    except sqlite3.IntegrityError:  # UNIQUE(origen, destino, tipo) o CHECK(origen <> destino)
        return _error("la relación ya existe o une un nodo consigo mismo", 409)
    return jsonify({"sourceId": id_front(origen["tipo"], origen["id"]),
                    "targetId": id_front(destino["tipo"], destino["id"]), "type": tipo}), 201


@bp.delete("/api/relationships")
@requiere_login
def delete_relationship():
    origen, destino, tipo, problema = _leer_relacion()
    if problema:
        return _error(*problema)
    if not desrelacionar(g.conn, origen["id"], destino["id"], tipo, g.usuario_id):
        return _error("relación no encontrada", 404)
    return "", 204
