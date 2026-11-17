"""La clave nunca se guarda ni se devuelve en texto plano: solo el hash de werkzeug."""
from werkzeug.security import check_password_hash, generate_password_hash

from db import ahora

# Roles que permite el esquema (CHECK de la tabla usuarios)
ROLES = ("admin", "editor", "lector")


def _normalizar(email):
    """Sin espacios y en minusculas, asi 'Ana@X.com' y 'ana@x.com' son el mismo usuario."""
    return email.strip().lower()


def _publico(fila):
    return {clave: fila[clave] for clave in ("id", "email", "nombre", "rol")}


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
                ahora(),
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
    return _publico(fila)


def obtener_usuario(conn, usuario_id):
    fila = conn.execute(
        "SELECT id, email, nombre, rol FROM usuarios WHERE id = ?", (usuario_id,)
    ).fetchone()
    return fila and _publico(fila)
