# T24 — tests de registrar_usuario y verificar_clave (de Oziel)
# Listo cuando: pytest en verde
import sqlite3

import pytest


from usuarios import registrar_usuario, verificar_clave


def test_la_clave_no_se_guarda_en_texto_plano(conn):
    registrar_usuario(conn, "ana@local", "Ana", "secreta123")
    hash_clave = conn.execute("SELECT hash_clave FROM usuarios WHERE email = 'ana@local'").fetchone()[0]
    assert "secreta123" not in hash_clave


def test_email_repetido_falla(conn):
    registrar_usuario(conn, "ana@local", "Ana", "secreta123")
    with pytest.raises(sqlite3.IntegrityError):
        registrar_usuario(conn, "ana@local", "Otra Ana", "otra")


def test_verificar_clave_buena(conn):
    registrar_usuario(conn, "ana@local", "Ana", "secreta123")
    usuario = verificar_clave(conn, "ana@local", "secreta123")
    assert usuario["email"] == "ana@local"
    assert "hash_clave" not in usuario  # nunca se devuelve el hash


def test_verificar_clave_mala_o_email_inexistente(conn):
    registrar_usuario(conn, "ana@local", "Ana", "secreta123")
    assert verificar_clave(conn, "ana@local", "otra") is None
    assert verificar_clave(conn, "nadie@local", "secreta123") is None
