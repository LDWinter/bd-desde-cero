"""Exportar e importar un JSON (todo o nada; entities[].id es una referencia local del archivo), vaciar datos y borrar fuentes."""
import sqlite3

from flask import Blueprint, g, jsonify, request

from formato import SELECT_RELACION, a_entity, a_relationship, id_front
from nodos import insertar_nodo, listar_nodos, obtener_nodo
from relaciones import insertar_relacion
from rutas_auth import requiere_login
from rutas_fuentes import SELECT_FUENTES
from rutas_nodos import _buscar, _validar_entity

bp = Blueprint("importar", __name__)

FUENTE_IMPORTADA = "Importado"
TABLAS_DE_DATOS = ("historial", "relaciones", "nodos", "fuentes", "tipos_nodo")  # en este orden por las FK


def _vaciar(conn):
    for tabla in TABLAS_DE_DATOS:
        conn.execute(f"DELETE FROM {tabla}")


def _validar(datos):
    if not isinstance(datos, dict):
        return "se esperaba un objeto JSON"
    if not isinstance(datos.get("replace", False), bool):  # "true" (texto) se tomaba como false, sin avisar
        return "replace tiene que ser true o false"
    fuentes = datos.get("sources", [])
    entidades = datos.get("entities", [])
    relaciones = datos.get("relationships", [])
    if not all(isinstance(lista, list) for lista in (fuentes, entidades, relaciones)):
        return "sources, entities y relationships tienen que ser listas"
    if not entidades and not relaciones:
        return "el archivo no trae entidades ni relaciones"
    for i, f in enumerate(fuentes):
        if not (isinstance(f, dict) and all(isinstance(f.get(k), str) and f[k].strip() for k in ("name", "type"))
                and f.get("status") in ("ok", "error") and isinstance(f.get("lastSync"), (str, type(None)))):
            return f"sources[{i}]: se esperaba {{name, type, status: ok o error, lastSync: fecha ISO o null}}"
    vistos = set()
    for i, e in enumerate(entidades):
        problema = _validar_entity(e)
        if problema:
            return f"entities[{i}]: {problema}"
        if not isinstance(e.get("id"), str) or not e["id"].strip():
            return f"entities[{i}]: id no puede estar vacío"
        if e["id"] in vistos:
            return f"entities[{i}]: el id {e['id']!r} está repetido"
        vistos.add(e["id"])
    for i, r in enumerate(relaciones):
        if not isinstance(r, dict):
            return f"relationships[{i}]: se esperaba un objeto"
        if not isinstance(r.get("type"), str) or not r["type"].strip():
            return f"relationships[{i}]: type no puede estar vacío"
        for clave in ("sourceId", "targetId"):
            ref = r.get(clave)
            # primero el isinstance: una lista o un objeto no se puede buscar en un set (daba 500)
            if not isinstance(ref, str) or (ref not in vistos and _buscar(ref) is None):
                return f"relationships[{i}]: {clave} {ref!r} no existe ni en el archivo ni en la base"
    return None


@bp.post("/api/import")
@requiere_login
def importar():
    datos = request.get_json(silent=True)
    problema = _validar(datos)
    if problema:
        return jsonify({"error": problema}), 400
    reemplazar = datos.get("replace", False)
    if reemplazar:  # las referencias a nodos existentes desaparecen: solo valen los ids del archivo
        locales = {e["id"] for e in datos.get("entities", [])}
        for i, r in enumerate(datos.get("relationships", [])):
            if r["sourceId"] not in locales or r["targetId"] not in locales:
                return jsonify({"error": f"relationships[{i}]: con replace solo se puede unir entidades del archivo"}), 400

    conn = g.conn
    ids = {}
    try:
        with conn:  # una sola transacción: por eso no se usan crear_nodo / relacionar, que confirman cada una
            if reemplazar:
                _vaciar(conn)
            for i, f in enumerate(datos.get("sources", [])):
                try:
                    conn.execute(
                        "INSERT INTO fuentes (nombre, tipo, estado, ultima_sync) VALUES (?, ?, ?, ?)"
                        " ON CONFLICT (nombre) DO UPDATE SET tipo = excluded.tipo, estado = excluded.estado,"
                        " ultima_sync = excluded.ultima_sync",
                        (f["name"].strip(), f["type"].strip(), f["status"], f["lastSync"]),
                    )
                except sqlite3.IntegrityError:  # el CHECK de fuentes.ultima_sync
                    raise ValueError(f"sources[{i}]: lastSync no es una fecha válida")
            for e in datos.get("entities", []):
                ids[e["id"]] = insertar_nodo(conn, e["type"].strip(), e["name"].strip(),
                                             e.get("source", FUENTE_IMPORTADA).strip(), e.get("data", {}), g.usuario_id)
            for i, r in enumerate(datos.get("relationships", [])):
                origen, destino = (ids.get(ref) or _buscar(ref)["id"] for ref in (r["sourceId"], r["targetId"]))
                try:
                    insertar_relacion(conn, origen, destino, r["type"].strip(), g.usuario_id)
                except sqlite3.IntegrityError:
                    raise ValueError(f"relationships[{i}]: la relación ya existe o une un nodo consigo mismo")
    except ValueError as e:  # `with conn` ya hizo rollback
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "entities": len(ids),
        "relationships": len(datos.get("relationships", [])),
        "ids": {local: id_front(obtener_nodo(conn, nodo)["tipo"], nodo) for local, nodo in ids.items()},
    }), 201


@bp.get("/api/export")
@requiere_login
def exportar():
    """Mismo formato que recibe /api/import: reimportarlo restaura entidades, relaciones y fuentes."""
    return jsonify({
        "replace": True,
        "sources": [{"name": f["nombre"], "type": f["tipo"], "status": f["estado"], "lastSync": f["ultima_sync"]}
                    for f in g.conn.execute(SELECT_FUENTES)],
        "entities": [a_entity(f) for f in listar_nodos(g.conn)],
        "relationships": [a_relationship(f) for f in g.conn.execute(SELECT_RELACION)],
    })


@bp.delete("/api/data")
@requiere_login
def vaciar_datos():
    with g.conn:
        _vaciar(g.conn)
    return "", 204


@bp.delete("/api/sources/<int(max=9223372036854775807):fuente_id>")  # un id más grande no entra en SQLite (daba 500)
@requiere_login
def borrar_fuente(fuente_id):
    conn = g.conn
    if conn.execute("SELECT 1 FROM fuentes WHERE id = ?", (fuente_id,)).fetchone() is None:
        return jsonify({"error": "fuente no encontrada"}), 404
    nodos = "SELECT id FROM nodos WHERE fuente_id = ?"
    with conn:  # todo o nada, en el orden que piden las FK
        conn.execute(f"DELETE FROM historial WHERE nodo_id IN ({nodos})", (fuente_id,))
        conn.execute(f"DELETE FROM relaciones WHERE origen_id IN ({nodos}) OR destino_id IN ({nodos})",
                     (fuente_id, fuente_id))
        conn.execute("DELETE FROM nodos WHERE fuente_id = ?", (fuente_id,))
        conn.execute("DELETE FROM fuentes WHERE id = ?", (fuente_id,))
    return "", 204
