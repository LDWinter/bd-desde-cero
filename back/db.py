# T13 — conectar(ruta) con foreign_keys=ON y row_factory; crear_esquema(conn)
# Listo cuando: abre la base y crea las tablas
import sqlite3
from pathlib import Path

# esquema.sql está al lado de este archivo; así funciona desde cualquier carpeta
ESQUEMA = Path(__file__).with_name("esquema.sql")


def conectar(ruta):
    """Abre la base (un archivo o ':memory:') lista para usar."""
    # check_same_thread=False: Flask puede atender un request en otro hilo que el que abrió la conexión
    conn = sqlite3.connect(ruta, check_same_thread=False)
    conn.execute("PRAGMA foreign_keys = ON")  # SQLite no controla las FK si no se lo pedís en cada conexión
    conn.row_factory = sqlite3.Row  # filas que se leen por nombre: fila["titulo"]
    return conn


def crear_esquema(conn):
    """Crea las 6 tablas (se puede correr varias veces: usa IF NOT EXISTS)."""
    conn.executescript(ESQUEMA.read_text(encoding="utf-8"))
