"""Levanta todo con un comando: el back (Flask) sirve también el front compilado (web/). La base queda en datos/base.db."""
import os
import secrets
import socket
import sys
import threading
import webbrowser
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "back"))

from flask import abort, send_from_directory  # noqa: E402

import semilla  # noqa: E402
from app import crear_app  # noqa: E402
from db import conectar  # noqa: E402
from usuarios import registrar_usuario  # noqa: E402

PUERTO = int(os.environ.get("PUERTO", "5001"))
WEB = AQUI / "web"
BASE = AQUI / "datos" / "base.db"
CLAVE = BASE.parent / "clave-sesion.txt"

BASE.parent.mkdir(exist_ok=True)
# Clave de sesión propia de esta copia: la de desarrollo de app.py es pública (está en el código)
if not CLAVE.exists():
    CLAVE.write_text(secrets.token_hex(32))
os.environ.setdefault("SECRET_KEY", CLAVE.read_text().strip())
app = crear_app(str(BASE))

conn = conectar(str(BASE))
if conn.execute("SELECT COUNT(*) FROM usuarios").fetchone()[0] == 0:
    # Solo el usuario de prueba: los datos se cargan desde Fuentes → Importar JSON
    u = semilla.USUARIO_PRUEBA
    registrar_usuario(conn, u["email"], u["nombre"], u["clave"], u["rol"])
conn.close()


@app.get("/")
@app.get("/<path:ruta>")
def front(ruta=""):
    if ruta.startswith("api/"):
        abort(404)  # una ruta de API que no existe da el error en JSON, no la página del front
    # Archivos del front; cualquier otra ruta (/grafo, /entidad/...) es de la app de una página
    if ruta and (WEB / ruta).is_file():
        return send_from_directory(WEB, ruta)
    if not (WEB / "index.html").is_file():
        abort(404, "Falta el front compilado en web/: correr paquete/armar.sh <carpeta del front>")
    return send_from_directory(WEB, "index.html")


if __name__ == "__main__":
    url = f"http://127.0.0.1:{PUERTO}"
    with socket.socket() as prueba:
        if prueba.connect_ex(("127.0.0.1", PUERTO)) == 0:
            sys.exit(f"\n  El puerto {PUERTO} ya está en uso: Knowledge System ya está abierto en {url},\n"
                     "  o lo usa otro programa (en ese caso, elegir otro con la variable PUERTO).\n")
    print(f"\n  Knowledge System en {url}  (usuario prueba@local / clave prueba123)")
    print("  Para cerrarlo: cerrar esta ventana o Ctrl+C\n")
    if os.environ.get("SIN_NAVEGADOR") != "1":
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=PUERTO)
