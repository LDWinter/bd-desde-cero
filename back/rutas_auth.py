"""T29 y T30 - Sesion con cookie y proteccion de rutas.

POST /api/auth/login    {email, password}  -> el usuario, o 401
POST /api/auth/logout                      -> cierra la sesion
GET  /api/auth/me                          -> el usuario logueado, o 401

El usuario siempre sale como {id, email, nombre, rol}: nunca la clave ni su hash.

Para proteger una ruta (el decorador va DEBAJO de @bp.route):

    from rutas_auth import requiere_login

    @bp.route("/api/entities", methods=["POST"])
    @requiere_login
    def crear():
        ...  # g.usuario_id es el id del usuario logueado
"""
from functools import wraps

from flask import Blueprint, g, jsonify, request, session

from usuarios import obtener_usuario, verificar_clave

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

MENSAJE_NO_AUTENTICADO = "no autenticado"


def _usuario_de_la_sesion():
    """El usuario logueado ({id, email, nombre, rol}) o None.

    Si la cookie apunta a un usuario que ya no existe, se limpia la sesion.
    """
    usuario_id = session.get("usuario_id")
    usuario = obtener_usuario(g.conn, usuario_id) if usuario_id is not None else None
    if usuario is None:
        session.clear()
    return usuario


def requiere_login(vista):
    """Decorador: sin sesion valida responde 401; con sesion, deja el usuario en
    g.usuario_id (su id, para anotar el historial) y g.usuario (el diccionario completo)."""

    @wraps(vista)
    def envoltura(*args, **kwargs):
        usuario = _usuario_de_la_sesion()
        if usuario is None:
            return jsonify({"error": MENSAJE_NO_AUTENTICADO}), 401
        g.usuario_id = usuario["id"]
        g.usuario = usuario
        return vista(*args, **kwargs)

    return envoltura


@bp.route("/login", methods=["POST"])
def login():
    datos = request.get_json(silent=True)
    if not isinstance(datos, dict):
        return jsonify({"error": "Hay que enviar un JSON con email y password"}), 400
    email = datos.get("email")
    password = datos.get("password")
    if not isinstance(email, str) or not isinstance(password, str) or not email or not password:
        return jsonify({"error": "Faltan email y password"}), 400

    usuario = verificar_clave(g.conn, email, password)
    if usuario is None:
        # Mismo mensaje si falla el email o la clave: no se revela cual fue
        return jsonify({"error": "Email o clave incorrectos"}), 401

    session.clear()  # sesion nueva, por si quedaba una vieja
    session["usuario_id"] = usuario["id"]
    return jsonify(usuario)


@bp.route("/logout", methods=["POST"])
def logout():
    session.clear()
    return "", 204


@bp.route("/me", methods=["GET"])
def me():
    usuario = _usuario_de_la_sesion()
    if usuario is None:
        return jsonify({"error": MENSAJE_NO_AUTENTICADO}), 401
    return jsonify(usuario)
