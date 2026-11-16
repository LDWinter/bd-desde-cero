"""Nodos (ids enteros de la base). Cada cambio y su historial van en una misma transacción (`with conn`)."""
import json

from historial import registrar

SELECT_NODO = """
    SELECT n.id, t.nombre AS tipo, f.nombre AS fuente, n.titulo, n.contenido
    FROM nodos n
    JOIN tipos_nodo t ON t.id = n.tipo_id
    JOIN fuentes f ON f.id = n.fuente_id
"""


def _tipo_id(conn, tipo):
    fila = conn.execute("SELECT id FROM tipos_nodo WHERE nombre = ?", (tipo,)).fetchone()
    if fila is not None:
        return fila["id"]
    cur = conn.execute("INSERT INTO tipos_nodo (nombre) VALUES (?)", (tipo,))
    return cur.lastrowid


def _fuente_id(conn, fuente):
    fila = conn.execute("SELECT id FROM fuentes WHERE nombre = ?", (fuente,)).fetchone()
    if fila is not None:
        return fila["id"]
    cur = conn.execute(
        "INSERT INTO fuentes (nombre, tipo, estado) VALUES (?, 'Manual', 'ok')", (fuente,)
    )
    return cur.lastrowid


def _foto(fila):
    return {
        "name": fila["titulo"],
        "type": fila["tipo"],
        "source": fila["fuente"],
        "data": json.loads(fila["contenido"]),
    }


def crear_nodo(conn, tipo, nombre, fuente, data, usuario_id):
    with conn:
        cur = conn.execute(
            "INSERT INTO nodos (tipo_id, fuente_id, creado_por, titulo, contenido) VALUES (?, ?, ?, ?, ?)",
            (_tipo_id(conn, tipo), _fuente_id(conn, fuente), usuario_id, nombre,
             json.dumps(data, ensure_ascii=False)),
        )
        nodo_id = cur.lastrowid
        registrar(conn, nodo_id, usuario_id, "crear", None, _foto(obtener_nodo(conn, nodo_id)))
    return nodo_id


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
            "UPDATE nodos SET titulo = ?, contenido = ?, tipo_id = ?, actualizado_en = datetime('now')"
            " WHERE id = ?",
            (
                antes["titulo"] if nombre is None else nombre,
                antes["contenido"] if data is None else json.dumps(data, ensure_ascii=False),
                _tipo_id(conn, antes["tipo"] if tipo is None else tipo),
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
        conn.execute(
            "UPDATE nodos SET borrado = 1, actualizado_en = datetime('now') WHERE id = ?", (nodo_id,)
        )
        registrar(conn, nodo_id, usuario_id, "borrar", _foto(antes), None)
    return True
