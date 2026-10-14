# T15 — crear_nodo, obtener_nodo
# T16 — listar_nodos(tipo=None), editar_nodo, borrar_nodo (borrado lógico)
# T22 — crear/editar/borrar registran en el historial en la misma transacción
# Listo cuando: prueba manual OK; editar deja su 'antes' y 'después'
import json

try:
    from historial import registrar  # T20 (B)
except ImportError:  # mientras B no suba historial.py, se usa la copia provisional
    from historial_provisional import registrar

# Nodo con el nombre de su tipo y de su fuente (lo que necesita a_entity)
SELECT_NODO = """
    SELECT n.id, t.nombre AS tipo, f.nombre AS fuente, n.titulo, n.contenido
    FROM nodos n
    JOIN tipos_nodo t ON t.id = n.tipo_id
    JOIN fuentes f ON f.id = n.fuente_id
"""


def _tipo_id(conn, tipo):
    fila = conn.execute("SELECT id FROM tipos_nodo WHERE nombre = ?", (tipo,)).fetchone()
    if fila is None:
        raise ValueError(f"tipo inexistente: {tipo}")
    return fila["id"]


def _fuente_id(conn, fuente):
    """Id de la fuente por nombre; si no existe la crea (nodos cargados a mano desde el front)."""
    fila = conn.execute("SELECT id FROM fuentes WHERE nombre = ?", (fuente,)).fetchone()
    if fila is not None:
        return fila["id"]
    cur = conn.execute(
        "INSERT INTO fuentes (nombre, tipo, estado) VALUES (?, 'Manual', 'ok')", (fuente,)
    )
    return cur.lastrowid


def _foto(fila):
    """Cómo se guarda un nodo en el historial (antes / después)."""
    return {
        "name": fila["titulo"],
        "type": fila["tipo"],
        "source": fila["fuente"],
        "data": json.loads(fila["contenido"]),
    }


def crear_nodo(conn, tipo, nombre, fuente, data, usuario_id):
    """Crea el nodo y lo anota en el historial. Devuelve el id nuevo."""
    with conn:  # una transacción: el nodo y su historial se guardan juntos o no se guarda nada
        cur = conn.execute(
            "INSERT INTO nodos (tipo_id, fuente_id, creado_por, titulo, contenido) VALUES (?, ?, ?, ?, ?)",
            (_tipo_id(conn, tipo), _fuente_id(conn, fuente), usuario_id, nombre,
             json.dumps(data, ensure_ascii=False)),
        )
        nodo_id = cur.lastrowid
        registrar(conn, nodo_id, usuario_id, "crear", None, _foto(obtener_nodo(conn, nodo_id)))
    return nodo_id


def obtener_nodo(conn, nodo_id):
    """La fila del nodo, o None si no existe o está borrado."""
    return conn.execute(SELECT_NODO + " WHERE n.id = ? AND n.borrado = 0", (nodo_id,)).fetchone()


def listar_nodos(conn, tipo=None):
    """Todos los nodos no borrados; si viene tipo ('Cliente', ...), solo los de ese tipo."""
    if tipo is None:
        return conn.execute(SELECT_NODO + " WHERE n.borrado = 0 ORDER BY n.id").fetchall()
    return conn.execute(
        SELECT_NODO + " WHERE n.borrado = 0 AND t.nombre = ? ORDER BY n.id", (tipo,)
    ).fetchall()


def editar_nodo(conn, nodo_id, usuario_id, nombre=None, data=None, tipo=None):
    """Cambia lo que venga (nombre, data y/o tipo). Devuelve False si el nodo no existe."""
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
    """Borrado lógico: se marca borrado = 1 (la fila y su historial quedan). False si no existe."""
    with conn:
        antes = obtener_nodo(conn, nodo_id)
        if antes is None:
            return False
        conn.execute(
            "UPDATE nodos SET borrado = 1, actualizado_en = datetime('now') WHERE id = ?", (nodo_id,)
        )
        registrar(conn, nodo_id, usuario_id, "borrar", _foto(antes), None)
    return True
