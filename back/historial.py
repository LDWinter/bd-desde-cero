import json

from db import ahora

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
            ahora(),
        ),
    )
    _purgar(conn, nodo_id)
    return cur.lastrowid


def historial_de(conn, nodo_id):
    return conn.execute(
        "SELECT id, usuario_id, accion, antes, despues, fecha"
        " FROM historial WHERE nodo_id = ?"
        " ORDER BY fecha DESC, id DESC",
        (nodo_id,),
    ).fetchall()


def historial_reciente(conn, limite):
    """Los últimos cambios de todos los nodos, con el título y el tipo del nodo de cada uno."""
    return conn.execute(
        "SELECT h.usuario_id, h.accion, h.antes, h.despues, h.fecha, h.nodo_id, n.titulo, t.nombre AS tipo"
        " FROM historial h JOIN nodos n ON n.id = h.nodo_id JOIN tipos_nodo t ON t.id = n.tipo_id"
        # una relación se anota en sus dos nodos: acá cuenta una vez, la del nodo de origen
        " WHERE h.accion NOT IN ('relacionar', 'desrelacionar')"
        "    OR h.nodo_id = CAST(json_extract(COALESCE(h.despues, h.antes), '$.sourceId') AS INTEGER)"
        " ORDER BY h.fecha DESC, h.id DESC LIMIT ?",
        (limite,),
    ).fetchall()
