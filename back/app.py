# T25 (B) — app.py: Flask, conexión por request, errores en JSON y SECRET_KEY
# PROVISIONAL: lo escribió A (14/10) siguiendo tareas/B/12, para poder probar T26 a T32.
# B: revisalo y reemplazalo por tu versión si querés (falta registrar rutas_fuentes cuando exista).
# Levantar (desde back/):  flask --app app run   → http://localhost:5000
import os

from flask import Flask, g, jsonify

from db import conectar


def crear_app(ruta_db="base.db"):
    app = Flask(__name__)
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "solo-para-desarrollo")
    app.config["RUTA_DB"] = ruta_db

    @app.before_request
    def abrir_conexion():
        g.conn = conectar(app.config["RUTA_DB"])

    @app.teardown_appcontext
    def cerrar_conexion(_error):
        conn = g.pop("conn", None)
        if conn is not None:
            conn.close()

    for codigo, mensaje in [(400, "pedido inválido"), (401, "no autenticado"),
                            (404, "no encontrado"), (405, "método no permitido"), (409, "conflicto")]:
        app.register_error_handler(codigo, lambda e, m=mensaje, c=codigo: (jsonify({"error": m}), c))

    from rutas_auth import bp as bp_auth
    from rutas_nodos import bp as bp_nodos
    app.register_blueprint(bp_auth)
    app.register_blueprint(bp_nodos)
    return app


# para "flask --app app run"; la base se elige con la variable DB (por defecto base.db)
app = crear_app(os.environ.get("DB", "base.db"))
