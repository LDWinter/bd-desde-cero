import sqlite3
from datetime import datetime
from pathlib import Path

ESQUEMA = Path(__file__).with_name("esquema.sql")


def conectar(ruta):
    # check_same_thread=False: Flask puede atender un request en otro hilo que el que abrió la conexión
    conn = sqlite3.connect(ruta, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite no controla las FK si no se lo pedís en cada conexión
    conn.row_factory = sqlite3.Row
    return conn


def ahora():
    return datetime.now().strftime("%Y-%m-%dT%H:%M:%S")


def crear_esquema(conn):
    conn.executescript(ESQUEMA.read_text(encoding="utf-8"))
