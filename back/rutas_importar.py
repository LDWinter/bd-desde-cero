"""POST /api/import y DELETE /api/data

POST /api/import (login) carga entidades y relaciones desde un JSON:
    {"replace": false,
     "entities": [{"id": "ana", "type": "Persona", "name": "Ana", "source": "Importado", "data": {...}}],
     "relationships": [{"sourceId": "ana", "targetId": "pro-3", "type": "trabaja en"}]}
- entities[].id es una referencia LOCAL del archivo (única dentro del archivo).
- sourceId/targetId: primero se buscan entre los ids locales; si no, se toman como id del front de un nodo existente.
- replace: true vacía los datos antes de importar.
- Todo o nada: ante cualquier error responde 400 {"error": ...} y no guarda nada.
- Respuesta 201: {"entities": n, "relationships": n, "ids": {id_local: id_front}}

DELETE /api/data (login) vacía historial, relaciones, nodos y fuentes (no toca usuarios ni tipos). 204.
"""
import json
import sqlite3

from flask import Blueprint, g, jsonify, request

from formato import id_front
from historial import registrar
from nodos import _foto as _foto_nodo, _fuente_id, _tipo_id, obtener_nodo
from relaciones import _foto as _foto_relacion
from rutas_auth import requiere_login
from rutas_nodos import _buscar, _validar_entity

bp = Blueprint("importar", __name__)

FUENTE_IMPORTADA = "Importado"
TABLAS_DE_DATOS = ("historial", "relaciones", "nodos", "fuentes")  # en este orden por las FK


def _vaciar(conn):
    for tabla in TABLAS_DE_DATOS:
        conn.execute(f"DELETE FROM {tabla}")


def _validar(datos):
    """Revisa el archivo entero antes de tocar la base. Devuelve un mensaje de error o None."""
    if not isinstance(datos, dict):
        return "se esperaba un objeto JSON"
    entidades = datos.get("entities", [])
    relaciones = datos.get("relationships", [])
    if not isinstance(entidades, list) or not isinstance(relaciones, list):
        return "entities y relationships tienen que ser listas"
    if not entidades and not relaciones:
        return "el archivo no trae entidades ni relaciones"
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
            if ref not in vistos and (not isinstance(ref, str) or _buscar(ref) is None):
                return f"relationships[{i}]: {clave} {ref!r} no existe ni en el archivo ni en la base"
    return None


@bp.post("/api/import")
@requiere_login
def importar():
    datos = request.get_json(silent=True)
    reemplazar = isinstance(datos, dict) and datos.get("replace") is True
    # Con replace, las referencias a nodos existentes desaparecen: solo valen los ids del archivo.
    problema = _validar(datos)
    if problema:
        return jsonify({"error": problema}), 400
    if reemplazar:
        locales = {e["id"] for e in datos.get("entities", [])}
        for i, r in enumerate(datos.get("relationships", [])):
            if r["sourceId"] not in locales or r["targetId"] not in locales:
                return jsonify({"error": f"relationships[{i}]: con replace solo se puede unir entidades del archivo"}), 400

    conn = g.conn
    ids = {}  # id local -> id de la base
    try:
        # Una sola transacción (no se usan crear_nodo/relacionar porque cada una hace su propio commit).
        with conn:
            if reemplazar:
                _vaciar(conn)
            for e in datos.get("entities", []):
                cur = conn.execute(
                    "INSERT INTO nodos (tipo_id, fuente_id, creado_por, titulo, contenido) VALUES (?, ?, ?, ?, ?)",
                    (_tipo_id(conn, e["type"].strip()), _fuente_id(conn, e.get("source", FUENTE_IMPORTADA)),
                     g.usuario_id, e["name"].strip(), json.dumps(e.get("data", {}), ensure_ascii=False)),
                )
                ids[e["id"]] = cur.lastrowid
                registrar(conn, cur.lastrowid, g.usuario_id, "crear", None, _foto_nodo(obtener_nodo(conn, cur.lastrowid)))
            for i, r in enumerate(datos.get("relationships", [])):
                origen, destino = (ids.get(ref) or _buscar(ref)["id"] for ref in (r["sourceId"], r["targetId"]))
                tipo = r["type"].strip()
                try:
                    conn.execute("INSERT INTO relaciones (origen_id, destino_id, tipo) VALUES (?, ?, ?)",
                                 (origen, destino, tipo))
                except sqlite3.IntegrityError:  # UNIQUE(origen, destino, tipo) o CHECK(origen <> destino)
                    raise ValueError(f"relationships[{i}]: la relación ya existe o une un nodo consigo mismo")
                foto = _foto_relacion(origen, destino, tipo)
                registrar(conn, origen, g.usuario_id, "relacionar", None, foto)
                registrar(conn, destino, g.usuario_id, "relacionar", None, foto)
    except ValueError as e:  # `with conn` ya hizo rollback
        return jsonify({"error": str(e)}), 400

    return jsonify({
        "entities": len(ids),
        "relationships": len(datos.get("relationships", [])),
        "ids": {local: id_front(obtener_nodo(conn, nodo)["tipo"], nodo) for local, nodo in ids.items()},
    }), 201


@bp.delete("/api/data")
@requiere_login
def vaciar_datos():
    with g.conn:
        _vaciar(g.conn)
    return "", 204
