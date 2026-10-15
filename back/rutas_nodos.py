"""
Este módulo define las rutas de la API para la gestión de nodos (entidades) y relaciones en el sistema.

Los IDs utilizados por el front-end siguen el formato '<prefijo>-<id_de_la_base>', donde:
- 'cli' corresponde a Clientes.
- 'pro' corresponde a Productos.
- 'ped' corresponde a Pedidos.

La conversión entre el ID del front y el ID de la base de datos se realiza mediante
las funciones `formato.id_base()` y `formato.id_front()`.

Todas las respuestas de error devuelven un objeto JSON con la estructura:
{"error": "mensaje del error"}
"""
# T26 — GET /api/entities y GET /api/entities/<id>   (igual a getEntities() del mock)
# T27 — GET /api/relationships   (igual a getRelationships())
# T31 — POST /api/entities (valida tipo, name, data; 201 con la Entity)
# T32 — PUT y DELETE /api/entities/<id> (404 si no existe)
# T33 — POST y DELETE /api/relationships (409 si duplicado o lazo)
# Ids: el front usa "cli-1"; se traducen solo con formato.id_base()/id_front() (de Oziel).
# (Oziel agrega T34: GET /api/entities/<id>/history)
import json
import math
import sqlite3

from flask import Blueprint, g, jsonify, request

from formato import SELECT_RELACION, a_entity, a_relationship, id_base, id_front
from nodos import borrar_nodo, crear_nodo, editar_nodo, listar_nodos, obtener_nodo
from historial import historial_de
from relaciones import desrelacionar, relacionar
try:
    from rutas_auth import requiere_login  # T30 (Oziel)
except ImportError:  # mientras Oziel no suba rutas_auth.py, se usa la copia provisional
    from back.Revisar.rutas_auth_provisional import requiere_login

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
        # Python acepta NaN/Infinity en JSON, pero el CHECK(json_valid) de la base no: sin esto daba 500
        if isinstance(valor, float) and not math.isfinite(valor):
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
    """
    Obtiene la lista de entidades.
    - Método: GET
    - URL: /api/entities
    - Login: No requerido.
    - Parámetros:
        - type (query, opcional): Tipo de entidad (ej: "Cliente").
    - Respuesta: JSON con lista de entidades.
    - Ejemplo de respuesta:
        [
            {"id": "cli-1", "type": "Cliente", "name": "Acme S.A.", "source": "clientes_2025.xlsx",
             "data": {"email": "contacto@acme.com", "ciudad": "Córdoba"}},
            ...
        ]
    """
    tipo = request.args.get("type")  # opcional: /api/entities?type=Cliente
    return jsonify([a_entity(fila) for fila in listar_nodos(g.conn, tipo)])


@bp.get("/api/entities/<entity_id>")
def get_entity(entity_id):
    """
    Obtiene una entidad por su ID.
    - Método: GET
    - URL: /api/entities/<entity_id>
    - Login: No requerido.
    - Parámetros:
        - entity_id (path): ID de la entidad (ej: "cli-1").
    - Respuesta: JSON con la entidad.
    - Ejemplo de respuesta:
        {"id": "cli-1", "type": "Cliente", "name": "Acme S.A.", "source": "clientes_2025.xlsx",
         "data": {"email": "contacto@acme.com", "ciudad": "Córdoba"}}
    - Errores:
        - 404: Si la entidad no existe o el ID es inválido.
    """
    fila = _buscar(entity_id)
    if fila is None:
        return _error("entidad no encontrada", 404)
    return jsonify(a_entity(fila))


# ---- T34 (Oziel) — PROVISIONAL escrita por A (15/10) siguiendo la ficha de Oziel; Oziel la puede reemplazar ----
@bp.get("/api/entities/<entity_id>/history")
def get_history(entity_id):
    """Últimos cambios (máximo 5) de una entidad, del más nuevo al más viejo.
    - Respuesta: [{"accion", "usuario", "antes", "despues", "fecha"}] (fecha ISO; antes/despues objeto o null).
    - Errores: 404 si la entidad no existe.
    """
    fila = _buscar(entity_id)
    if fila is None:
        return _error("entidad no encontrada", 404)
    nombres = dict(g.conn.execute("SELECT id, nombre FROM usuarios").fetchall())
    return jsonify([
        {
            "accion": c["accion"],
            "usuario": nombres.get(c["usuario_id"]),
            "antes": json.loads(c["antes"]) if c["antes"] else None,
            "despues": json.loads(c["despues"]) if c["despues"] else None,
            "fecha": c["fecha"],
        }
        for c in historial_de(g.conn, fila["id"])
    ])


# ---- T27 ----
@bp.get("/api/relationships")
def get_relationships():
    """
    Obtiene todas las relaciones existentes.
    - Método: GET
    - URL: /api/relationships
    - Login: No requerido.
    - Respuesta: JSON con lista de relaciones.
    - Ejemplo de respuesta:
        [
            {"sourceId": "cli-1", "targetId": "pro-5", "type": "compró"}
        ]
    """
    return jsonify([a_relationship(fila) for fila in g.conn.execute(SELECT_RELACION)])


# ---- T31 ----
@bp.post("/api/entities")
@requiere_login
def post_entity():
    """
    Crea una nueva entidad.
    - Método: POST
    - URL: /api/entities
    - Login: Requerido.
    - Parámetros (JSON):
        - type (str): Tipo de entidad ("Cliente", "Producto" o "Pedido").
        - name (str): Nombre de la entidad.
        - source (str, opcional): Origen de la entidad. Por defecto "Manual".
        - data (dict, opcional): Diccionario de atributos (texto, números).
    - Respuesta: 201 Created, JSON con la entidad creada.
    - Ejemplo de entrada:
        {"type": "Cliente", "name": "Juan Pérez", "source": "Manual", "data": {"edad": 30}}
    - Ejemplo de respuesta:
        {"id": "cli-15", "type": "Cliente", "name": "Juan Pérez", "source": "Manual", "data": {"edad": 30}}
    - Errores:
        - 400: Si el JSON es inválido, el tipo no es válido, el nombre está vacío, data no es objeto, o los valores de data no son válidos (texto o número finito).
        - 401: Sin sesión iniciada.
    """
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
    """
    Actualiza una entidad existente.
    - Método: PUT
    - URL: /api/entities/<entity_id>
    - Login: Requerido.
    - Parámetros (JSON):
        - type (str): Tipo de la entidad.
        - name (str): Nuevo nombre.
        - data (dict, opcional): Nuevos atributos. Si NO se manda, los datos actuales no se tocan
          (el front, en updateEntity, solo manda name y type).
    - Ojo: si cambia el type, cambia el prefijo del id (cli-15 -> pro-15). Usar el id de la respuesta.
    - Respuesta: JSON con la entidad actualizada.
    - Ejemplo de entrada:
        {"type": "Cliente", "name": "Juan Pérez", "data": {"edad": 31}}
    - Ejemplo de respuesta:
        {"id": "cli-15", "type": "Cliente", "name": "Juan Pérez", "source": "Manual", "data": {"edad": 31}}
    - Errores:
        - 401: Sin sesión iniciada.
        - 404: Si la entidad no existe (o el prefijo del id no coincide con su tipo).
        - 400: Si el JSON es inválido, el tipo no es válido, el nombre está vacío, o los valores de data no son válidos (texto o número finito).
    """
    fila = _buscar(entity_id)
    if fila is None:
        return _error("entidad no encontrada", 404)
    nodo_id = fila["id"]
    datos = request.get_json(silent=True)
    problema = _validar_entity(datos)
    if problema:
        return _error(problema, 400)
    editar_nodo(g.conn, nodo_id, g.usuario_id,
                nombre=datos["name"].strip(), data=datos.get("data"), tipo=datos["type"])  # sin data: no se toca
    return jsonify(a_entity(obtener_nodo(g.conn, nodo_id)))


@bp.delete("/api/entities/<entity_id>")
@requiere_login
def delete_entity(entity_id):
    """
    Elimina una entidad.
    - Método: DELETE
    - URL: /api/entities/<entity_id>
    - Login: Requerido.
    - Parámetros:
        - entity_id (path): ID de la entidad a borrar.
    - Respuesta: 204 No Content.
    - Errores:
        - 401: Sin sesión iniciada.
        - 404: Si la entidad no existe o ya estaba borrada.
    - Nota: el borrado es lógico; sus relaciones dejan de aparecer en GET /api/relationships.
    """
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
    if not all(isinstance(datos.get(k), str) and datos[k] for k in ("sourceId", "targetId")):
        return None, None, None, ("sourceId y targetId son obligatorios", 400)
    origen, destino = _buscar(datos["sourceId"]), _buscar(datos["targetId"])
    if origen is None or destino is None:
        return None, None, None, ("sourceId o targetId no existe", 404)
    return origen, destino, tipo.strip(), None


@bp.post("/api/relationships")
@requiere_login
def post_relationship():
    """
    Crea una nueva relación entre dos entidades.
    - Método: POST
    - URL: /api/relationships
    - Login: Requerido.
    - Parámetros (JSON):
        - sourceId (str): ID de la entidad origen (ej: "cli-1").
        - targetId (str): ID de la entidad destino (ej: "pro-5").
        - type (str): Tipo de relación (ej: "compra").
    - Respuesta: 201 Created, JSON con la relación creada.
    - Ejemplo de entrada:
        {"sourceId": "cli-1", "targetId": "pro-5", "type": "compra"}
    - Ejemplo de respuesta:
        {"sourceId": "cli-1", "targetId": "pro-5", "type": "compra"}
    - Errores:
        - 400: Si el JSON es inválido, el tipo está vacío o falta sourceId/targetId.
        - 401: Sin sesión iniciada.
        - 404: Si sourceId o targetId no existe.
        - 409: Si la relación ya existe o el nodo intenta relacionarse consigo mismo.
    """
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
    """
    Elimina una relación existente.
    - Método: DELETE
    - URL: /api/relationships
    - Login: Requerido.
    - Parámetros (JSON):
        - sourceId (str): ID de la entidad origen.
        - targetId (str): ID de la entidad destino.
        - type (str): Tipo de relación.
    - Respuesta: 204 No Content.
    - Ejemplo de entrada:
        {"sourceId": "cli-1", "targetId": "pro-5", "type": "compra"}
    - Errores:
        - 400: Si el JSON es inválido, el tipo está vacío o falta sourceId/targetId.
        - 401: Sin sesión iniciada.
        - 404: Si sourceId o targetId no existe.
        - 404: Si la relación no existe.
    """
    origen, destino, tipo, problema = _leer_relacion()
    if problema:
        return _error(*problema)
    if not desrelacionar(g.conn, origen["id"], destino["id"], tipo, g.usuario_id):
        return _error("relación no encontrada", 404)
    return "", 204
