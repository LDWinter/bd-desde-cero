import math
import sqlite3

from flask import Blueprint, g, jsonify, request

from formato import SELECT_RELACION, a_entity, a_relationship, id_base, id_front
from nodos import borrar_nodo, crear_nodo, editar_nodo, listar_nodos, obtener_nodo
from relaciones import desrelacionar, relacionar
from rutas_auth import requiere_login

bp = Blueprint("nodos", __name__)

FUENTE_POR_DEFECTO = "Manual"


def _error(mensaje, codigo):
    return jsonify({"error": mensaje}), codigo


def _validar_entity(datos):
    """Devuelve un mensaje de error, o None si el JSON es una Entity válida."""
    if not isinstance(datos, dict):
        return "se esperaba un objeto JSON"
    if not isinstance(datos.get("type"), str) or not datos["type"].strip() or len(datos["type"].strip()) > 40:
        return "type tiene que ser un texto de 1-40 caracteres"
    if not isinstance(datos.get("name"), str) or not datos["name"].strip():
        return "name no puede estar vacío"
    data = datos.get("data", {})
    if not isinstance(data, dict):
        return "data tiene que ser un objeto"
    for clave, valor in data.items():
        # {clave: texto | número}; bool es un int en Python, por eso se excluye aparte
        if isinstance(valor, bool) or not isinstance(valor, (str, int, float)):
            return f"data.{clave} tiene que ser texto o número"
        # Python acepta NaN/Infinity en JSON, pero el CHECK(json_valid) de la base no: sin esto daba 500
        if isinstance(valor, float) and not math.isfinite(valor):
            return f"data.{clave} tiene que ser texto o número"
    source = datos.get("source", FUENTE_POR_DEFECTO)
    if not isinstance(source, str) or not source.strip():
        return "source tiene que ser un texto"
    return None


def _buscar(entity_id):
    """Fila del nodo, o None si el id no es válido, no existe o su prefijo no coincide con el tipo."""
    try:
        fila = obtener_nodo(g.conn, id_base(entity_id))
    except ValueError:
        return None
    return fila if fila is not None and id_front(fila["tipo"], fila["id"]) == entity_id else None


@bp.get("/api/entities")
def get_entities():
    tipo = request.args.get("type")
    return jsonify([a_entity(fila) for fila in listar_nodos(g.conn, tipo)])


@bp.get("/api/entities/<entity_id>")
def get_entity(entity_id):
    fila = _buscar(entity_id)
    if fila is None:
        return _error("entidad no encontrada", 404)
    return jsonify(a_entity(fila))


@bp.get("/api/relationships")
def get_relationships():
    return jsonify([a_relationship(fila) for fila in g.conn.execute(SELECT_RELACION)])


@bp.post("/api/entities")
@requiere_login
def post_entity():
    datos = request.get_json(silent=True)
    problema = _validar_entity(datos)
    if problema:
        return _error(problema, 400)
    nodo_id = crear_nodo(
        g.conn, datos["type"].strip(), datos["name"].strip(), datos.get("source", FUENTE_POR_DEFECTO).strip(),
        datos.get("data", {}), g.usuario_id,
    )
    return jsonify(a_entity(obtener_nodo(g.conn, nodo_id))), 201


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
                nombre=datos["name"].strip(), data=datos.get("data"), tipo=datos["type"].strip())  # sin data: no se toca
    return jsonify(a_entity(obtener_nodo(g.conn, nodo_id)))


@bp.delete("/api/entities/<entity_id>")
@requiere_login
def delete_entity(entity_id):
    fila = _buscar(entity_id)
    if fila is None or not borrar_nodo(g.conn, fila["id"], g.usuario_id):
        return _error("entidad no encontrada", 404)
    return "", 204


def _leer_relacion():
    """Valida {sourceId, targetId, type}. Devuelve (origen, destino, tipo, None) o (.., (mensaje, código))."""
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return None, None, None, ("se esperaba un objeto JSON", 400)
    tipo = datos.get("type")
    if not isinstance(tipo, str) or not tipo.strip():
        return None, None, None, ("type no puede estar vacío", 400)
    if not all(isinstance(datos.get(k), str) and datos[k] for k in ("sourceId", "targetId")):
        return None, None, None, ("sourceId y targetId son obligatorios", 400)
    origen, destino = _buscar(datos["sourceId"]), _buscar(datos["targetId"])
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
    except sqlite3.IntegrityError:
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
