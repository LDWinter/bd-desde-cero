# T29 (B) — POST /api/auth/login, POST /api/auth/logout, GET /api/auth/me
# T30 (B) — decorador @requiere_login
# PROVISIONAL: lo escribió A (14/10) siguiendo tareas/B/13 y 14, para poder probar T31 y T32.
# B: revisalo y reemplazalo por tu versión si querés; mantené el nombre requiere_login.
from functools import wraps

from flask import Blueprint, g, jsonify, request, session

from usuarios import verificar_clave

bp = Blueprint("auth", __name__)


def requiere_login(vista):
    """401 si no hay sesión; si hay, deja el usuario en g.usuario_id."""
    @wraps(vista)
    def envuelta(*args, **kwargs):
        if "usuario_id" not in session:
            return jsonify({"error": "no autenticado"}), 401
        g.usuario_id = session["usuario_id"]
        return vista(*args, **kwargs)
    return envuelta


@bp.post("/api/auth/login")
def login():
    datos = request.get_json(silent=True) or {}
    usuario = verificar_clave(g.conn, datos.get("email", ""), datos.get("password", ""))
    if usuario is None:
        return jsonify({"error": "email o clave incorrectos"}), 401
    session["usuario_id"] = usuario["id"]
    return jsonify(usuario)


@bp.post("/api/auth/logout")
def logout():
    session.clear()
    return "", 204


@bp.get("/api/auth/me")
@requiere_login
def me():
    fila = g.conn.execute(
        "SELECT id, email, nombre, rol FROM usuarios WHERE id = ?", (g.usuario_id,)
    ).fetchone()
    if fila is None:
        return jsonify({"error": "no autenticado"}), 401
    return jsonify(dict(fila))
