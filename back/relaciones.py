from historial import registrar


def _foto(origen, destino, tipo):
    return {"sourceId": str(origen), "targetId": str(destino), "type": tipo}


def insertar_relacion(conn, origen, destino, tipo, usuario_id):
    """Sin commit: la importación guarda todas sus relaciones en una sola transacción."""
    relacion_id = conn.execute(
        "INSERT INTO relaciones (origen_id, destino_id, tipo) VALUES (?, ?, ?)", (origen, destino, tipo)
    ).lastrowid
    foto = _foto(origen, destino, tipo)
    # una relación cambia dos nodos: se anota en el historial de cada uno
    registrar(conn, origen, usuario_id, "relacionar", None, foto)
    registrar(conn, destino, usuario_id, "relacionar", None, foto)
    return relacion_id


def relacionar(conn, origen, destino, tipo, usuario_id):
    with conn:
        return insertar_relacion(conn, origen, destino, tipo, usuario_id)


def desrelacionar(conn, origen, destino, tipo, usuario_id):
    with conn:
        cur = conn.execute(
            "DELETE FROM relaciones WHERE origen_id = ? AND destino_id = ? AND tipo = ?",
            (origen, destino, tipo),
        )
        if cur.rowcount == 0:
            return False
        foto = _foto(origen, destino, tipo)
        registrar(conn, origen, usuario_id, "desrelacionar", foto, None)
        registrar(conn, destino, usuario_id, "desrelacionar", foto, None)
    return True


def vecinos(conn, nodo_id):
    return conn.execute(
        """
        SELECT r.destino_id AS vecino_id, v.titulo, r.tipo
        FROM relaciones r JOIN nodos v ON v.id = r.destino_id
        WHERE r.origen_id = ? AND v.borrado = 0
        UNION
        SELECT r.origen_id, v.titulo, r.tipo
        FROM relaciones r JOIN nodos v ON v.id = r.origen_id
        WHERE r.destino_id = ? AND v.borrado = 0
        ORDER BY vecino_id
        """,
        (nodo_id, nodo_id),
    ).fetchall()

