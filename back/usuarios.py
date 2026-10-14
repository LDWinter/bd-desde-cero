# T23 (B) — registrar_usuario (con hash) y verificar_clave
# PROVISIONAL: lo escribió A (14/10) siguiendo tareas/B/11, para poder probar T24.
# B: revisalo y reemplazalo por tu versión si querés; mantené los mismos nombres y parámetros.
from werkzeug.security import check_password_hash, generate_password_hash


def registrar_usuario(conn, email, nombre, clave, rol="editor"):
    """Crea el usuario guardando solo el hash de la clave. Devuelve el id nuevo."""
    with conn:
        cur = conn.execute(
            "INSERT INTO usuarios (email, nombre, hash_clave, rol) VALUES (?, ?, ?, ?)",
            (email, nombre, generate_password_hash(clave), rol),
        )
    return cur.lastrowid


def verificar_clave(conn, email, clave):
    """El usuario (sin el hash) si email y clave coinciden; si no, None."""
    fila = conn.execute("SELECT * FROM usuarios WHERE email = ?", (email,)).fetchone()
    if fila is None or not check_password_hash(fila["hash_clave"], clave):
        return None
    return {"id": fila["id"], "email": fila["email"], "nombre": fila["nombre"], "rol": fila["rol"]}
