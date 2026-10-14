"""T11 - Semilla con los mismos datos de los mocks del front.

Uso:
    python semilla.py base.db

Borra los datos de la base y los vuelve a cargar, asi se puede correr
las veces que haga falta. Si las tablas no existen, las crea con
esquema.sql (que tiene que estar en la misma carpeta).
"""
import sqlite3
import sys
from datetime import datetime
from pathlib import Path

from werkzeug.security import generate_password_hash

# ---------------------------------------------------------------------
# DATOS: copiados de src/mocks/data.ts del front
# 3 fuentes, 14 nodos (4 clientes + 4 productos + 6 pedidos), 15 relaciones
# ---------------------------------------------------------------------
TIPOS = ["Cliente", "Producto", "Pedido"]

# (nombre, tipo, estado, ultima_sync)  -- fechas pasadas a ISO
FUENTES = [
    ("clientes_2025.xlsx", "Excel", "ok", "2026-10-05T10:32:00"),
    ("Base ventas", "SQL", "ok", "2026-10-06T18:10:00"),
    ("Tablero Proyectos", "Trello", "error", "2026-10-01T09:00:00"),
]

# (id_mock, tipo, name, nombre_de_la_fuente, data)
NODOS = [
    ("cli-1", "Cliente", "Acme S.A.", "clientes_2025.xlsx",
     {"email": "contacto@acme.com", "ciudad": "Córdoba"}),
    ("cli-2", "Cliente", "Bodega Los Andes", "clientes_2025.xlsx",
     {"email": "ventas@losandes.com", "ciudad": "Rosario"}),
    ("cli-3", "Cliente", "Distribuidora Cuyo", "clientes_2025.xlsx",
     {"email": "info@dcuyo.com", "ciudad": "Buenos Aires"}),
    ("cli-4", "Cliente", "ACME SA", "Base ventas",
     {"email": "contacto@acme.com", "ciudad": "Córdoba"}),
    ("pro-1", "Producto", "Malbec 750 ml", "Base ventas", {"precio": 4500}),
    ("pro-2", "Producto", "Aceite de oliva 1 L", "Base ventas", {"precio": 6200}),
    ("pro-3", "Producto", "Caja de cartón x12", "Base ventas", {"precio": 1800}),
    ("pro-4", "Producto", "Etiquetas adhesivas", "Base ventas", {"precio": 950}),
    ("ped-1", "Pedido", "Pedido #1001", "Base ventas", {"fecha": "28/09/2026", "total": 54000}),
    ("ped-2", "Pedido", "Pedido #1002", "Base ventas", {"fecha": "30/09/2026", "total": 31500}),
    ("ped-3", "Pedido", "Pedido #1003", "Base ventas", {"fecha": "01/10/2026", "total": 18600}),
    ("ped-4", "Pedido", "Pedido #1004", "Base ventas", {"fecha": "03/10/2026", "total": 24800}),
    ("ped-5", "Pedido", "Pedido #1005", "Base ventas", {"fecha": "04/10/2026", "total": 9500}),
    ("ped-6", "Pedido", "Pedido #1006", "Base ventas", {"fecha": "05/10/2026", "total": 12000}),
]

# (id_mock_origen, id_mock_destino, type)
RELACIONES = [
    ("ped-1", "cli-1", "pertenece a"),
    ("ped-1", "pro-1", "contiene"),
    ("ped-1", "pro-3", "contiene"),
    ("ped-2", "cli-2", "pertenece a"),
    ("ped-2", "pro-1", "contiene"),
    ("ped-2", "pro-4", "contiene"),
    ("ped-3", "cli-2", "pertenece a"),
    ("ped-3", "pro-2", "contiene"),
    ("ped-4", "cli-3", "pertenece a"),
    ("ped-4", "pro-2", "contiene"),
    ("ped-4", "pro-3", "contiene"),
    ("ped-5", "cli-1", "pertenece a"),
    ("ped-5", "pro-4", "contiene"),
    ("ped-6", "cli-4", "pertenece a"),
    ("ped-6", "pro-1", "contiene"),
]

USUARIO_PRUEBA = {
    "email": "prueba@local",
    "nombre": "Usuario de prueba",
    "clave": "prueba123",  # solo para desarrollo
    "rol": "admin",
}

# Esperado segun el "Listo cuando" de T11
ESPERADO = {"fuentes": 3, "nodos": 14, "relaciones": 15}

# Hijas primero, para no chocar con las claves foraneas
TABLAS_A_VACIAR = ["historial", "relaciones", "nodos", "usuarios", "fuentes", "tipos_nodo"]


def ahora():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def vaciar(conn):
    for tabla in TABLAS_A_VACIAR:
        conn.execute(f"DELETE FROM {tabla}")
    # Para que los ids vuelvan a empezar en 1
    marcas = ",".join("?" * len(TABLAS_A_VACIAR))
    conn.execute(f"DELETE FROM sqlite_sequence WHERE name IN ({marcas})", TABLAS_A_VACIAR)


def cargar(conn):
    import json

    tipo_id = {}
    for nombre in TIPOS:
        cur = conn.execute("INSERT INTO tipos_nodo (nombre) VALUES (?)", (nombre,))
        tipo_id[nombre] = cur.lastrowid

    fuente_id = {}
    for nombre, tipo, estado, ultima_sync in FUENTES:
        cur = conn.execute(
            "INSERT INTO fuentes (nombre, tipo, estado, ultima_sync) VALUES (?, ?, ?, ?)",
            (nombre, tipo, estado, ultima_sync),
        )
        fuente_id[nombre] = cur.lastrowid

    u = USUARIO_PRUEBA
    cur = conn.execute(
        "INSERT INTO usuarios (email, nombre, hash_clave, rol, creado) VALUES (?, ?, ?, ?, ?)",
        (u["email"], u["nombre"], generate_password_hash(u["clave"]), u["rol"], ahora()),
    )
    usuario_id = cur.lastrowid

    nodo_id = {}  # id del mock -> id en la base
    for id_mock, tipo, name, fuente, data in NODOS:
        cur = conn.execute(
            "INSERT INTO nodos (tipo_id, fuente_id, creado_por, titulo, contenido, creado_en)"
            " VALUES (?, ?, ?, ?, ?, ?)",
            (
                tipo_id[tipo],
                fuente_id[fuente],
                usuario_id,
                name,
                json.dumps(data, ensure_ascii=False),
                ahora(),
            ),
        )
        nodo_id[id_mock] = cur.lastrowid

    for origen, destino, tipo in RELACIONES:
        conn.execute(
            "INSERT INTO relaciones (origen_id, destino_id, tipo) VALUES (?, ?, ?)",
            (nodo_id[origen], nodo_id[destino], tipo),
        )


def contar(conn):
    return {
        "fuentes": conn.execute("SELECT COUNT(*) FROM fuentes").fetchone()[0],
        "nodos": conn.execute("SELECT COUNT(*) FROM nodos").fetchone()[0],
        "relaciones": conn.execute("SELECT COUNT(*) FROM relaciones").fetchone()[0],
    }


def main():
    if len(sys.argv) != 2:
        print("Uso: python semilla.py base.db")
        sys.exit(1)

    conn = sqlite3.connect(sys.argv[1])
    conn.execute("PRAGMA foreign_keys = ON")

    esquema = Path(__file__).with_name("esquema.sql")
    if esquema.exists():
        conn.executescript(esquema.read_text(encoding="utf-8"))

    try:
        with conn:  # una sola transaccion: si algo falla, no queda nada a medias
            vaciar(conn)
            cargar(conn)
    except sqlite3.Error as e:
        print("ERROR al cargar la semilla:", e)
        sys.exit(1)

    conteos = contar(conn)
    print("Cargado:", conteos)
    if conteos != ESPERADO:
        print("OJO: se esperaba", ESPERADO, "- revisa los datos de arriba.")
    conn.close()


if __name__ == "__main__":
    main()
