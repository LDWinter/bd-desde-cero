"""T25 - Base de la aplicacion Flask (patron factory).

Aca se enchufan todas las rutas. Cada archivo de rutas (rutas_nodos.py,
rutas_fuentes.py, rutas_auth.py) tiene que exponer un Blueprint llamado `bp`.

Levantar:      flask --app app run          (desde la carpeta back/)
En los tests:  app = crear_app(":memory:")
"""
import os
from importlib import import_module

from flask import Flask, g, jsonify
from werkzeug.exceptions import HTTPException

from db import conectar, crear_esquema

# Archivos de rutas que se enchufan (cada uno expone `bp`)
MODULOS_DE_RUTAS = ("rutas_nodos", "rutas_fuentes", "rutas_auth")

# Mensajes por defecto en espanol; si una ruta hace abort(409, "texto"), se usa ese texto
MENSAJES = {
    400: "Solicitud invalida",
    401: "Hace falta iniciar sesion",
    403: "No tenes permiso para hacer esto",
    404: "No encontrado",
    405: "Metodo no permitido",
    409: "Conflicto con los datos existentes",
    415: "Formato no soportado",
    500: "Error interno del servidor",
}


def _registrar_rutas(app):
    for nombre in MODULOS_DE_RUTAS:
        try:
            modulo = import_module(nombre)
        except ModuleNotFoundError as e:
            if e.name != nombre:
                raise  # falla un import DENTRO del modulo: no hay que taparlo
            # Todavia no existe (T26, T28 y T29). Cuando esten las tres, conviene
            # sacar este try/except para que un archivo mal nombrado de error.
            app.logger.warning("Todavia no existe %s.py: sus rutas no se registran", nombre)
            continue
        app.register_blueprint(modulo.bp)


def crear_app(ruta_db="base.db"):
    app = Flask(__name__)
    # Solo para desarrollo: en cualquier otro lado se define SECRET_KEY como variable de entorno
    app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY", "dev-solo-para-desarrollo")
    app.config["RUTA_DB"] = ruta_db

    # Una base en memoria desaparece al cerrar su conexion, asi que en ese caso
    # (los tests) todos los requests comparten una sola conexion, que queda en
    # app.config["CONN"] para que el test pueda cargarle datos.
    if ruta_db == ":memory:":
        app.config["CONN"] = conectar(ruta_db)
        crear_esquema(app.config["CONN"])
    else:
        conn = conectar(ruta_db)
        crear_esquema(conn)  # si la base es nueva, crea las tablas
        conn.close()

    @app.before_request
    def abrir_conexion():
        g.conn = app.config.get("CONN") or conectar(app.config["RUTA_DB"])

    @app.teardown_appcontext
    def cerrar_conexion(error):
        conn = g.pop("conn", None)
        if conn is not None and conn is not app.config.get("CONN"):
            conn.close()

    @app.errorhandler(HTTPException)
    def error_http(e):
        mensaje = MENSAJES.get(e.code, e.name) if e.description == type(e).description else e.description
        return jsonify({"error": mensaje}), e.code

    _registrar_rutas(app)
    return app


# Para que `flask --app app run` encuentre la fabrica (Flask busca este nombre)
create_app = crear_app
