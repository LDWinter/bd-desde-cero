"""Nodos (ids enteros de la base). Cada cambio y su historial van en una misma transacción (`with conn`)."""
import json

from db import ahora
from historial import registrar

SELECT_NODO = """
    SELECT n.id, t.nombre AS tipo, f.nombre AS fuente, n.titulo, n.contenido
    FROM nodos n
    JOIN tipos_nodo t ON t.id = n.tipo_id
    JOIN fuentes f ON f.id = n.fuente_id
"""


# OR IGNORE y después buscar: buscando primero, dos pedidos a la vez con un nombre nuevo chocaban con el UNIQUE
def _tipo_id(conn, tipo):
    conn.execute("INSERT OR IGNORE INTO tipos_nodo (nombre) VALUES (?)", (tipo,))
    return conn.execute("SELECT id FROM tipos_nodo WHERE nombre = ?", (tipo,)).fetchone()["id"]


def _fuente_id(conn, fuente):
    conn.execute("INSERT OR IGNORE INTO fuentes (nombre, tipo, estado) VALUES (?, 'Manual', 'ok')", (fuente,))
    return conn.execute("SELECT id FROM fuentes WHERE nombre = ?", (fuente,)).fetchone()["id"]


def _foto(fila):
    return {
        "name": fila["titulo"],
        "type": fila["tipo"],
        "source": fila["fuente"],
        "data": json.loads(fila["contenido"]),
    }


def insertar_nodo(conn, tipo, nombre, fuente, data, usuario_id):
    """Sin commit: la importación guarda todos sus nodos en una sola transacción."""
    nodo_id = conn.execute(
        "INSERT INTO nodos (tipo_id, fuente_id, creado_por, titulo, contenido, creado_en) VALUES (?, ?, ?, ?, ?, ?)",
        (_tipo_id(conn, tipo), _fuente_id(conn, fuente), usuario_id, nombre,
         json.dumps(data, ensure_ascii=False), ahora()),
    ).lastrowid
    registrar(conn, nodo_id, usuario_id, "crear", None, _foto(obtener_nodo(conn, nodo_id)))
    return nodo_id


def crear_nodo(conn, tipo, nombre, fuente, data, usuario_id):
    with conn:
        return insertar_nodo(conn, tipo, nombre, fuente, data, usuario_id)


def obtener_nodo(conn, nodo_id):
    return conn.execute(SELECT_NODO + " WHERE n.id = ? AND n.borrado = 0", (nodo_id,)).fetchone()


def listar_nodos(conn, tipo=None):
    if tipo is None:
        return conn.execute(SELECT_NODO + " WHERE n.borrado = 0 ORDER BY n.id").fetchall()
    return conn.execute(
        SELECT_NODO + " WHERE n.borrado = 0 AND t.nombre = ? ORDER BY n.id", (tipo,)
    ).fetchall()


def editar_nodo(conn, nodo_id, usuario_id, nombre=None, data=None, tipo=None):
    with conn:
        antes = obtener_nodo(conn, nodo_id)
        if antes is None:
            return False
        conn.execute(
            "UPDATE nodos SET titulo = ?, contenido = ?, tipo_id = ?, actualizado_en = ? WHERE id = ?",
            (
                antes["titulo"] if nombre is None else nombre,
                antes["contenido"] if data is None else json.dumps(data, ensure_ascii=False),
                _tipo_id(conn, antes["tipo"] if tipo is None else tipo),
                ahora(),
                nodo_id,
            ),
        )
        registrar(conn, nodo_id, usuario_id, "editar", _foto(antes), _foto(obtener_nodo(conn, nodo_id)))
    return True


def borrar_nodo(conn, nodo_id, usuario_id):
    with conn:
        antes = obtener_nodo(conn, nodo_id)
        if antes is None:
            return False
        conn.execute("UPDATE nodos SET borrado = 1, actualizado_en = ? WHERE id = ?", (ahora(), nodo_id))
        registrar(conn, nodo_id, usuario_id, "borrar", _foto(antes), None)
    return True
