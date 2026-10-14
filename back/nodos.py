# T15 — crear_nodo, obtener_nodo
# T16 — listar_nodos(tipo=None), editar_nodo, borrar_nodo (borrado lógico)
# T22 — crear/editar/borrar registran en el historial en la misma transacción
# Listo cuando: prueba manual OK; editar deja su 'antes' y 'después'
import json


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


def crear_nodo(conn, tipo, nombre, fuente, data):
    """Crea el nodo y devuelve su id nuevo."""
    with conn:  # una transacción: commit si todo sale bien, rollback si algo falla
        cur = conn.execute(
            "INSERT INTO nodos (tipo_id, fuente_id, titulo, contenido) VALUES (?, ?, ?, ?)",
            (_tipo_id(conn, tipo), _fuente_id(conn, fuente), nombre, json.dumps(data, ensure_ascii=False)),
        )
    return cur.lastrowid


def obtener_nodo(conn, nodo_id):
    """La fila del nodo, o None si no existe o está borrado."""
    return conn.execute(SELECT_NODO + " WHERE n.id = ? AND n.borrado = 0", (nodo_id,)).fetchone()

