"""T29 - Rutas de sesion con cookie.

POST /api/auth/login    {email, password}  -> el usuario, o 401
POST /api/auth/logout                      -> cierra la sesion
GET  /api/auth/me                          -> el usuario logueado, o 401

El usuario siempre sale como {id, email, nombre, rol}: nunca la clave ni su hash.
"""
from flask import Blueprint, g, jsonify, request, session

from usuarios import obtener_usuario, verificar_clave

bp = Blueprint("auth", __name__, url_prefix="/api/auth")


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
    return jsonify({"ok": True})


@bp.route("/me", methods=["GET"])
def me():
    usuario_id = session.get("usuario_id")
    usuario = obtener_usuario(g.conn, usuario_id) if usuario_id is not None else None
    if usuario is None:
        session.clear()  # sin sesion, o el usuario ya no existe
        return jsonify({"error": "Hace falta iniciar sesion"}), 401
    return jsonify(usuario)
