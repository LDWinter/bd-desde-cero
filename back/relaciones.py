"""
Este módulo gestiona las relaciones entre los nodos en la base de datos.
Los IDs aquí son ENTEROS de la base de datos; la traducción a 'cli-1'
la realiza el módulo formato.py.
Cada cambio se anota en el historial dentro de la misma transacción
con 'with conn:' para que si algo falla no quede nada a medias.

Tareas: T17 (relacionar, desrelacionar, vecinos) y T22b (relacionar/desrelacionar
registran en el historial de los dos nodos, en la misma transacción).
"""
from historial import registrar


def _foto(origen, destino, tipo):
    """
    Convierte los datos de una relación en un diccionario para el historial.

    Args:
        origen (int): ID del nodo de origen.
        destino (int): ID del nodo de destino.
        tipo (str): Tipo de relación.

    Returns:
        dict: Diccionario con la estructura necesaria para el historial.
    """
    return {"sourceId": str(origen), "targetId": str(destino), "type": tipo}


def relacionar(conn, origen, destino, tipo, usuario_id):
    """
    Une dos nodos mediante una relación.

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        origen (int): ID del nodo de origen.
        destino (int): ID del nodo de destino.
        tipo (str): Tipo de relación.
        usuario_id (int): ID del usuario que crea la relación.

    Returns:
        int: El ID de la nueva relación.

    Raises:
        sqlite3.IntegrityError: Si se intenta crear un duplicado o un lazo (controlado por el esquema).
    """
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
    """
    Borra una relación existente (el borrado en la tabla relaciones es real).

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        origen (int): ID del nodo de origen.
        destino (int): ID del nodo de destino.
        tipo (str): Tipo de relación a borrar.
        usuario_id (int): ID del usuario que realiza la eliminación.

    Returns:
        bool: True si la relación existía y fue borrada, False de lo contrario.

    Raises:
        sqlite3.IntegrityError: Si hay un error de integridad en la base de datos.
    """
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
    """
    Obtiene los nodos unidos a un nodo_id, tanto como origen como destino.

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        nodo_id (int): ID del nodo para buscar sus vecinos.

    Returns:
        list: Lista de tuplas con los vecinos (vecino_id, título, tipo).
    """
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

