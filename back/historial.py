# T20 (B) — registrar() e historial_de()   ·   T21 (B) — purga: últimos HISTORIAL_MAX por nodo
# PROVISIONAL: lo escribió A (14/10) siguiendo tareas/B/09 y 10, para poder probar T22, T22b y T24.
# B: revisalo y reemplazalo por tu versión si querés; mantené los mismos nombres y parámetros.
import json

HISTORIAL_MAX = 5


def registrar(conn, nodo_id, usuario_id, accion, antes, despues):
    """Anota un cambio y deja solo los últimos HISTORIAL_MAX de ese nodo.
    No hace commit: lo hace quien la llama, para que todo vaya en la misma transacción."""
    conn.execute(
        "INSERT INTO historial (nodo_id, usuario_id, accion, antes, despues) VALUES (?, ?, ?, ?, ?)",
        (
            nodo_id,
            usuario_id,
            accion,
            None if antes is None else json.dumps(antes, ensure_ascii=False),
            None if despues is None else json.dumps(despues, ensure_ascii=False),
        ),
    )
    conn.execute(
        """DELETE FROM historial WHERE nodo_id = ? AND id NOT IN (
               SELECT id FROM historial WHERE nodo_id = ? ORDER BY fecha DESC, id DESC LIMIT ?)""",
        (nodo_id, nodo_id, HISTORIAL_MAX),
    )


def historial_de(conn, nodo_id):
    """Los cambios del nodo, del más nuevo al más viejo."""
    return conn.execute(
        "SELECT * FROM historial WHERE nodo_id = ? ORDER BY fecha DESC, id DESC", (nodo_id,)
    ).fetchall()
