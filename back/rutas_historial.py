import json

from flask import Blueprint, abort, g, jsonify, request

from formato import id_base, id_front
from historial import HISTORIAL_MAX, historial_de, historial_reciente
from nodos import obtener_nodo
from rutas_auth import requiere_login

bp = Blueprint("historial", __name__)

LIMITE_MAXIMO = 50


def _nombres_de_usuarios(conn, ids):
    ids = sorted(set(ids))
    if not ids:
        return {}
    marcas = ",".join("?" * len(ids))
    filas = conn.execute(
        f"SELECT id, nombre, email FROM usuarios WHERE id IN ({marcas})", ids
    ).fetchall()
    return {f["id"]: (f["nombre"] or f["email"]) for f in filas}


def _desde_json(texto):
    return None if texto is None else json.loads(texto)


def _con_ids_del_front(conn, foto):
    """Las relaciones se anotan con ids de la base ("1"); el front usa "cli-1"."""
    if not isinstance(foto, dict) or "sourceId" not in foto:
        return foto
    resultado = dict(foto)
    for clave in ("sourceId", "targetId"):
        try:
            nodo_id = int(foto[clave])
        except (KeyError, TypeError, ValueError):
            continue
        fila = conn.execute(
            "SELECT t.nombre AS tipo FROM nodos n JOIN tipos_nodo t ON t.id = n.tipo_id WHERE n.id = ?",
            (nodo_id,),
        ).fetchone()
        if fila is not None:
            resultado[clave] = id_front(fila["tipo"], nodo_id)
    return resultado


def _cambios(conn, filas):
    usuarios = _nombres_de_usuarios(conn, [f["usuario_id"] for f in filas])
    return [
        {
            "accion": f["accion"],
            "usuario": usuarios.get(f["usuario_id"]),
            "antes": _con_ids_del_front(conn, _desde_json(f["antes"])),
            "despues": _con_ids_del_front(conn, _desde_json(f["despues"])),
            "fecha": f["fecha"],
        }
        for f in filas
    ]


@bp.route("/api/entities/<entity_id>/history", methods=["GET"])
def historial_de_entidad(entity_id):
    try:
        nodo_id = id_base(entity_id)
    except ValueError:
        abort(404, "La entidad no existe")
    nodo = obtener_nodo(g.conn, nodo_id)
    # El id tiene que coincidir entero: "ped-1" no es el cliente 1
    if nodo is None or id_front(nodo["tipo"], nodo["id"]) != entity_id:
        abort(404, "La entidad no existe")

    return jsonify(_cambios(g.conn, historial_de(g.conn, nodo_id)[:HISTORIAL_MAX]))


@bp.get("/api/history")
@requiere_login
def historial_global():
    limite = min(max(request.args.get("limit", 10, type=int), 1), LIMITE_MAXIMO)
    filas = historial_reciente(g.conn, limite)
    return jsonify([
        {**cambio, "entityId": id_front(f["tipo"], f["nodo_id"]), "entityName": f["titulo"]}
        for cambio, f in zip(_cambios(g.conn, filas), filas)
    ])
