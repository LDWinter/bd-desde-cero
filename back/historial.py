"""T20 - Historial de cambios de cada nodo.

registrar(...)   anota un cambio y deja solo los ultimos HISTORIAL_MAX de ese nodo
                 (NO hace commit: lo hace quien la llama, para que el cambio, su
                 historial y la purga vayan en la misma transaccion).
historial_de(..) devuelve los cambios de un nodo, del mas nuevo al mas viejo.
"""
import json
from datetime import datetime

# Cuantos cambios se guardan por nodo (la purga que lo aplica es T21)
HISTORIAL_MAX = 5

# Los 5 tipos de cambio que se registran
ACCIONES = ("crear", "editar", "borrar", "relacionar", "desrelacionar")


def _a_json(valor):
    """None queda como NULL; cualquier otra cosa se guarda como texto JSON."""
    return None if valor is None else json.dumps(valor, ensure_ascii=False)


def _purgar(conn, nodo_id):
    """Borra los cambios de ESTE nodo que no esten entre los HISTORIAL_MAX mas nuevos."""
    conn.execute(
        "DELETE FROM historial WHERE nodo_id = ? AND id NOT IN ("
        " SELECT id FROM historial WHERE nodo_id = ?"
        " ORDER BY fecha DESC, id DESC LIMIT ?)",
        (nodo_id, nodo_id, HISTORIAL_MAX),
    )


def registrar(conn, nodo_id, usuario_id, accion, antes, despues):
    """Anota un cambio en el historial del nodo y aplica el tope. Devuelve el id de la fila nueva.

    antes / despues: diccionarios (o None). Un crear no tiene 'antes' y un
    borrar no tiene 'despues'.
    """
    if accion not in ACCIONES:
        raise ValueError(f"accion invalida: {accion!r} (debe ser una de {ACCIONES})")
    cur = conn.execute(
        "INSERT INTO historial (usuario_id, nodo_id, accion, antes, despues, fecha)"
        " VALUES (?, ?, ?, ?, ?, ?)",
        (
            usuario_id,
            nodo_id,
            accion,
            _a_json(antes),
            _a_json(despues),
            datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
        ),
    )
    _purgar(conn, nodo_id)  # el tope de 5 se aplica de a un nodo
    return cur.lastrowid  # sin commit a proposito


def historial_de(conn, nodo_id):
    """Cambios del nodo, del mas nuevo al mas viejo.

    Cada fila trae: id, usuario_id, accion, antes, despues, fecha
    (antes y despues son texto JSON o None: quien los use hace json.loads).
    """
    return conn.execute(
        "SELECT id, usuario_id, accion, antes, despues, fecha"
        " FROM historial WHERE nodo_id = ?"
        " ORDER BY fecha DESC, id DESC",
        (nodo_id,),
    ).fetchall()
