"""
Este módulo gestiona la información de los nodos en la base de datos.
Los IDs aquí son ENTEROS de la base de datos; la traducción a 'cli-1'
la realiza el módulo formato.py.
Cada cambio se anota en el historial dentro de la misma transacción
con 'with conn:' para que si algo falla no quede nada a medias.

Tareas: T15 (crear_nodo, obtener_nodo), T16 (listar_nodos, editar_nodo, borrar_nodo con borrado lógico)
y T22 (crear/editar/borrar registran en el historial en la misma transacción).
"""
import json

from historial import registrar

# Nodo con el nombre de su tipo y de su fuente (lo que necesita a_entity)
SELECT_NODO = """
    SELECT n.id, t.nombre AS tipo, f.nombre AS fuente, n.titulo, n.contenido
    FROM nodos n
    JOIN tipos_nodo t ON t.id = n.tipo_id
    JOIN fuentes f ON f.id = n.fuente_id
"""


def _tipo_id(conn, tipo):
    """
    Obtiene el ID de un tipo por su nombre.

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        tipo (str): Nombre del tipo a buscar.

    Returns:
        int: El ID del tipo.

    Raises:
        ValueError: Si el tipo no existe en la base de datos.
    """
    fila = conn.execute("SELECT id FROM tipos_nodo WHERE nombre = ?", (tipo,)).fetchone()
    if fila is None:
        raise ValueError(f"tipo inexistente: {tipo}")
    return fila["id"]


def _fuente_id(conn, fuente):
    """
    Obtiene el ID de la fuente por su nombre; si no existe la crea.

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        fuente (str): Nombre de la fuente.

    Returns:
        int: El ID de la fuente.
    """
    fila = conn.execute("SELECT id FROM fuentes WHERE nombre = ?", (fuente,)).fetchone()
    if fila is not None:
        return fila["id"]
    cur = conn.execute(
        "INSERT INTO fuentes (nombre, tipo, estado) VALUES (?, 'Manual', 'ok')", (fuente,)
    )
    return cur.lastrowid


def _foto(fila):
    """
    Convierte una fila de base de datos en un diccionario para el historial.

    Args:
        fila (tuple): Fila de la consulta SQL.

    Returns:
        dict: Diccionario con la estructura necesaria para el historial.
    """
    return {
        "name": fila["titulo"],
        "type": fila["tipo"],
        "source": fila["fuente"],
        "data": json.loads(fila["contenido"]),
    }


def crear_nodo(conn, tipo, nombre, fuente, data, usuario_id):
    """
    Crea un nuevo nodo y lo registra en el historial.

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        tipo (str): Nombre del tipo del nodo.
        nombre (str): Título del nodo.
        fuente (str): Nombre de la fuente.
        data (dict): Datos del contenido del nodo.
        usuario_id (int): ID del usuario que crea el nodo.

    Returns:
        int: El ID del nuevo nodo creado.

    Raises:
        ValueError: Si el tipo no existe.
        sqlite3.IntegrityError: Si hay un error de integridad en la base de datos.
    """
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
    """
    Obtiene los datos de un nodo por su ID.

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        nodo_id (int): ID del nodo.

    Returns:
        tuple: La fila del nodo si existe y no está borrado, o None.
    """
    return conn.execute(SELECT_NODO + " WHERE n.id = ? AND n.borrado = 0", (nodo_id,)).fetchone()


def listar_nodos(conn, tipo=None):
    """
    Lista todos los nodos no borrados.

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        tipo (str, optional): Nombre del tipo a filtrar. Por defecto None (devuelve todos).

    Returns:
        list: Lista de tuplas con los nodos.
    """
    if tipo is None:
        return conn.execute(SELECT_NODO + " WHERE n.borrado = 0 ORDER BY n.id").fetchall()
    return conn.execute(
        SELECT_NODO + " WHERE n.borrado = 0 AND t.nombre = ? ORDER BY n.id", (tipo,)
    ).fetchall()


def editar_nodo(conn, nodo_id, usuario_id, nombre=None, data=None, tipo=None):
    """
    Edita el contenido, título o tipo de un nodo existente.

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        nodo_id (int): ID del nodo a editar.
        usuario_id (int): ID del usuario que realiza la edición.
        nombre (str, optional): Nuevo título.
        data (dict, optional): Nuevos datos de contenido.
        tipo (str, optional): Nuevo nombre del tipo.

    Returns:
        bool: True si la edición fue exitosa, False si el nodo no existe.

    Raises:
        ValueError: Si el nuevo tipo no existe.
        sqlite3.IntegrityError: Si hay un error de integridad en la base de datos.
    """
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
    """
    Realiza un borrado lógico de un nodo (marca borrado = 1).

    Args:
        conn (sqlite3.Connection): Conexión a la base de datos.
        nodo_id (int): ID del nodo a borrar.
        usuario_id (int): ID del usuario que realiza el borrado.

    Returns:
        bool: True si el borrado fue exitoso, False si el nodo no existe.

    Raises:
        sqlite3.IntegrityError: Si hay un error de integridad en la base de datos.
    """
    with conn:
        antes = obtener_nodo(conn, nodo_id)
        if antes is None:
            return False
        conn.execute(
            "UPDATE nodos SET borrado = 1, actualizado_en = datetime('now') WHERE id = ?", (nodo_id,)
        )
        registrar(conn, nodo_id, usuario_id, "borrar", _foto(antes), None)
    return True
