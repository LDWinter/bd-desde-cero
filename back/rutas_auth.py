"""Sesion con cookie. Para proteger una ruta: @requiere_login DEBAJO de @bp.route."""
from functools import wraps

from flask import Blueprint, g, jsonify, request, session

from usuarios import obtener_usuario, verificar_clave

bp = Blueprint("auth", __name__, url_prefix="/api/auth")

MENSAJE_NO_AUTENTICADO = "no autenticado"


def _usuario_de_la_sesion():
    """Si la cookie apunta a un usuario que ya no existe, se limpia la sesion."""
    usuario_id = session.get("usuario_id")
    usuario = obtener_usuario(g.conn, usuario_id) if usuario_id is not None else None
    if usuario is None:
        session.clear()
    return usuario


def requiere_login(vista):
    """Sin sesion valida responde 401; con sesion deja g.usuario_id y g.usuario."""

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
