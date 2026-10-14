# T17 — relacionar, desrelacionar, vecinos(nodo_id)
# T22b — relacionar/desrelacionar registran en el historial de los dos nodos (misma transacción)
# Listo cuando: prueba manual OK; al unir 1 con 2 aparece en el historial de ambos
try:
    from historial import registrar  # T20 (B)
except ImportError:  # mientras B no suba historial.py, se usa la copia provisional
    from historial_provisional import registrar


def _foto(origen, destino, tipo):
    return {"sourceId": str(origen), "targetId": str(destino), "type": tipo}


def relacionar(conn, origen, destino, tipo, usuario_id):
    """Une dos nodos. Un duplicado o un lazo lanza sqlite3.IntegrityError (lo controla el esquema)."""
    with conn:
        cur = conn.execute(
            "INSERT INTO relaciones (origen_id, destino_id, tipo) VALUES (?, ?, ?)", (origen, destino, tipo)
        )
        foto = _foto(origen, destino, tipo)
        # una relación cambia dos nodos: se anota en el historial de cada uno
        registrar(conn, origen, usuario_id, "relacionar", None, foto)
        registrar(conn, destino, usuario_id, "relacionar", None, foto)
    return cur.lastrowid


def desrelacionar(conn, origen, destino, tipo, usuario_id):
    """Borra la relación (acá el borrado es real). Devuelve False si no existía."""
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
    """Nodos unidos a nodo_id, de los dos lados de la relación (la consulta 2 de T12)."""
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


def listar_relaciones(conn):
    """Todas las relaciones entre nodos no borrados (para GET /api/relationships)."""
    return conn.execute(
        """
        SELECT r.id, r.origen_id, r.destino_id, r.tipo
        FROM relaciones r
        JOIN nodos o ON o.id = r.origen_id
        JOIN nodos d ON d.id = r.destino_id
        WHERE o.borrado = 0 AND d.borrado = 0
        ORDER BY r.id
        """
    ).fetchall()
