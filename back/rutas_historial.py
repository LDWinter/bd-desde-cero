"""T34 - GET /api/entities/<id>/history

Los ultimos cambios de un nodo (maximo HISTORIAL_MAX), del mas nuevo al mas viejo:
    [{accion, usuario, antes, despues, fecha}, ...]

Va en su propio archivo (y no en rutas_nodos.py) para no pisar el trabajo de A.
"""
import json

from flask import Blueprint, abort, g, jsonify

from formato import id_base, id_front
from historial import HISTORIAL_MAX, historial_de
from nodos import obtener_nodo

bp = Blueprint("historial", __name__)


def _nombres_de_usuarios(conn, ids):
    """{id: nombre} (o el email si no tiene nombre) para los usuarios de esos cambios."""
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

    cambios = historial_de(g.conn, nodo_id)[:HISTORIAL_MAX]
    usuarios = _nombres_de_usuarios(g.conn, [c["usuario_id"] for c in cambios])
    return jsonify(
        [
            {
                "accion": c["accion"],
                "usuario": usuarios.get(c["usuario_id"]),
                "antes": _con_ids_del_front(g.conn, _desde_json(c["antes"])),
                "despues": _con_ids_del_front(g.conn, _desde_json(c["despues"])),
                "fecha": c["fecha"],
            }
            for c in cambios
        ]
    )
