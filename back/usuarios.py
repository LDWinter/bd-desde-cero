"""T23 - Alta de usuarios y verificacion de clave.

La clave nunca se guarda ni se devuelve en texto plano: en la base queda
solo el hash que genera werkzeug (hash_clave).
"""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

# Roles que permite el esquema (CHECK de la tabla usuarios)
ROLES = ("admin", "editor", "lector")


def _normalizar(email):
    """Sin espacios y en minusculas, asi 'Ana@X.com' y 'ana@x.com' son el mismo usuario."""
    return email.strip().lower()


def registrar_usuario(conn, email, nombre, clave, rol="editor"):
    """Da de alta un usuario con la clave hasheada. Devuelve su id.

    Levanta ValueError si la clave esta vacia o el rol no existe, y
    sqlite3.IntegrityError si el email ya esta registrado (lo controla el esquema).
    """
    if not clave:
        raise ValueError("la clave no puede estar vacia")
    if rol not in ROLES:
        raise ValueError(f"rol invalido: {rol!r} (debe ser uno de {ROLES})")
    with conn:  # transaccion propia: se confirma sola al salir
        cur = conn.execute(
            "INSERT INTO usuarios (email, nombre, hash_clave, rol, creado) VALUES (?, ?, ?, ?, ?)",
            (
                _normalizar(email),
                nombre,
                generate_password_hash(clave),
                rol,
                datetime.now().strftime("%Y-%m-%dT%H:%M:%S"),
            ),
        )
    return cur.lastrowid


def verificar_clave(conn, email, clave):
    """Si el email existe y la clave es correcta, devuelve el usuario; si no, None.

    El usuario es un diccionario {id, email, nombre, rol}: nunca incluye la clave
    ni su hash.
    """
    fila = conn.execute(
        "SELECT id, email, nombre, rol, hash_clave FROM usuarios WHERE email = ?",
        (_normalizar(email),),
    ).fetchone()
    if fila is None or not check_password_hash(fila["hash_clave"], clave):
        return None
    return {
        "id": fila["id"],
        "email": fila["email"],
        "nombre": fila["nombre"],
        "rol": fila["rol"],
    }


def obtener_usuario(conn, usuario_id):
    """El usuario con ese id como {id, email, nombre, rol} (sin hash), o None si no existe."""
    fila = conn.execute(
        "SELECT id, email, nombre, rol FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    if fila is None:
        return None
    return {
        "id": fila["id"],
        "email": fila["email"],
        "nombre": fila["nombre"],
        "rol": fila["rol"],
    }
