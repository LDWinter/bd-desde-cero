"""Knowledge System en una sola carpeta: el back (Flask) sirve también el front compilado (web/).

Uso: python iniciar.py   (lo llaman «Iniciar (Windows).bat» e «iniciar.sh»)
Abre http://127.0.0.1:5001 en el navegador. Usuario: prueba@local / clave: prueba123
La base queda en datos/base.db; para empezar de cero, borrar esa carpeta.
"""
import os
import sys
import threading
import webbrowser
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI / "back"))

from flask import send_from_directory  # noqa: E402

import semilla  # noqa: E402
from app import crear_app  # noqa: E402
from db import conectar  # noqa: E402

PUERTO = int(os.environ.get("PUERTO", "5001"))
WEB = AQUI / "web"
BASE = AQUI / "datos" / "base.db"

es_nueva = not BASE.exists()
BASE.parent.mkdir(exist_ok=True)
app = crear_app(str(BASE))  # crea las tablas si la base es nueva

if es_nueva:
    # Solo el usuario de prueba: los datos se cargan desde Fuentes → Importar JSON
    conn = conectar(str(BASE))
    with conn:
        semilla.cargar(conn)
        for tabla in ("historial", "relaciones", "nodos", "fuentes"):
            conn.execute(f"DELETE FROM {tabla}")
    conn.close()


@app.get("/")
@app.get("/<path:ruta>")
def front(ruta=""):
    # Archivos del front; cualquier otra ruta (/grafo, /entidad/...) es de la app de una página
    if ruta and (WEB / ruta).is_file():
        return send_from_directory(WEB, ruta)
    return send_from_directory(WEB, "index.html")


if __name__ == "__main__":
    url = f"http://127.0.0.1:{PUERTO}"
    print(f"\n  Knowledge System en {url}  (usuario prueba@local / clave prueba123)")
    print("  Para cerrarlo: cerrar esta ventana o Ctrl+C\n")
    if os.environ.get("SIN_NAVEGADOR") != "1":
        threading.Timer(1.5, lambda: webbrowser.open(url)).start()
    app.run(host="127.0.0.1", port=PUERTO)
