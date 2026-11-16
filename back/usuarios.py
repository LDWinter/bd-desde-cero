"""La clave nunca se guarda ni se devuelve en texto plano: solo el hash de werkzeug."""
from datetime import datetime

from werkzeug.security import check_password_hash, generate_password_hash

# Roles que permite el esquema (CHECK de la tabla usuarios)
ROLES = ("admin", "editor", "lector")


def _normalizar(email):
    """Sin espacios y en minusculas, asi 'Ana@X.com' y 'ana@x.com' son el mismo usuario."""
    return email.strip().lower()


def registrar_usuario(conn, email, nombre, clave, rol="editor"):
    """Levanta ValueError (clave vacia o rol invalido) o sqlite3.IntegrityError (email repetido)."""
    if not clave:
        raise ValueError("la clave no puede estar vacia")
    if rol not in ROLES:
        raise ValueError(f"rol invalido: {rol!r} (debe ser uno de {ROLES})")
    with conn:
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
    """El usuario {id, email, nombre, rol} si la clave es correcta; si no, None."""
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
