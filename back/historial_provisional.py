# T20 (B) — registrar() e historial_de()   ·   T21 (B) — purga: últimos HISTORIAL_MAX por nodo
# COPIA PROVISIONAL de `historial.py` (tarea de B), escrita por A (14/10) siguiendo la ficha de B para poder probar
# las tareas de A. NO es el archivo de B: cuando B suba `historial.py`, el código de A usa el de B solo
# (import con respaldo) y esta copia se puede borrar. Mismos nombres de funciones que pide la ficha.
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
