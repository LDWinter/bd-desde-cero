import json
from datetime import datetime

HISTORIAL_MAX = 5

ACCIONES = ("crear", "editar", "borrar", "relacionar", "desrelacionar")


def _a_json(valor):
    return None if valor is None else json.dumps(valor, ensure_ascii=False)


def _purgar(conn, nodo_id):
    conn.execute(
        "DELETE FROM historial WHERE nodo_id = ? AND id NOT IN ("
        " SELECT id FROM historial WHERE nodo_id = ?"
        " ORDER BY fecha DESC, id DESC LIMIT ?)",
        (nodo_id, nodo_id, HISTORIAL_MAX),
    )


def registrar(conn, nodo_id, usuario_id, accion, antes, despues):
    """No hace commit: lo hace quien llama, asi el cambio, su historial y la purga van en una transaccion."""
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
    _purgar(conn, nodo_id)
    return cur.lastrowid  # sin commit a proposito


def historial_de(conn, nodo_id):
    return conn.execute(
        "SELECT id, usuario_id, accion, antes, despues, fecha"
        " FROM historial WHERE nodo_id = ?"
        " ORDER BY fecha DESC, id DESC",
        (nodo_id,),
    ).fetchall()
