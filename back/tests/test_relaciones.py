# T18 - Tests de las funciones de relaciones (codigo de A: T17).
# Usa la fixture `conn`: nodos 1 ("Nodo uno") y 2 ("Nodo dos"), usuario 1.
import sqlite3

import pytest

from nodos import borrar_nodo, crear_nodo
from relaciones import desrelacionar, relacionar, vecinos

USUARIO = 1


def _contar(conn):
    return conn.execute("SELECT COUNT(*) FROM relaciones").fetchone()[0]


# ----------------------------------------------------------------- relacionar
def test_relacionar_funciona(conn):
    relacion_id = relacionar(conn, 1, 2, "conoce a", USUARIO)

    fila = conn.execute("SELECT * FROM relaciones WHERE id = ?", (relacion_id,)).fetchone()
    assert (fila["origen_id"], fila["destino_id"], fila["tipo"]) == (1, 2, "conoce a")


def test_relacionar_un_duplicado_falla(conn):
    relacionar(conn, 1, 2, "conoce a", USUARIO)
    with pytest.raises(sqlite3.IntegrityError):
        relacionar(conn, 1, 2, "conoce a", USUARIO)
    assert _contar(conn) == 1


def test_relacionar_los_mismos_nodos_con_otro_tipo_se_permite(conn):
    relacionar(conn, 1, 2, "conoce a", USUARIO)
    relacionar(conn, 1, 2, "trabaja con", USUARIO)
    assert _contar(conn) == 2


def test_relacionar_un_nodo_consigo_mismo_falla(conn):
    with pytest.raises(sqlite3.IntegrityError):
        relacionar(conn, 1, 1, "conoce a", USUARIO)
    assert _contar(conn) == 0


def test_relacionar_con_un_nodo_inexistente_falla(conn):
    with pytest.raises(sqlite3.IntegrityError):
        relacionar(conn, 1, 999, "conoce a", USUARIO)
    assert _contar(conn) == 0


# --------------------------------------------------------------- desrelacionar
def test_desrelacionar_funciona(conn):
    relacionar(conn, 1, 2, "conoce a", USUARIO)
    assert desrelacionar(conn, 1, 2, "conoce a", USUARIO) is True
    assert _contar(conn) == 0  # aca el borrado es real


def test_desrelacionar_algo_que_no_existe_devuelve_false(conn):
    assert desrelacionar(conn, 1, 2, "conoce a", USUARIO) is False


# --------------------------------------------------------------------- vecinos
def test_vecinos_funciona_de_los_dos_lados(conn):
    relacionar(conn, 1, 2, "conoce a", USUARIO)

    de_uno = vecinos(conn, 1)
    de_dos = vecinos(conn, 2)
    assert [(f["vecino_id"], f["titulo"], f["tipo"]) for f in de_uno] == [(2, "Nodo dos", "conoce a")]
    assert [(f["vecino_id"], f["titulo"], f["tipo"]) for f in de_dos] == [(1, "Nodo uno", "conoce a")]


def test_vecinos_de_un_nodo_sin_relaciones_devuelve_vacio(conn):
    assert vecinos(conn, 1) == []


def test_vecinos_no_incluye_nodos_borrados(conn):
    tercero = crear_nodo(conn, "Cliente", "Nodo tres", "fuente de prueba", {}, USUARIO)
    relacionar(conn, 1, 2, "conoce a", USUARIO)
    relacionar(conn, 1, tercero, "conoce a", USUARIO)

    borrar_nodo(conn, 2, USUARIO)

    assert [f["vecino_id"] for f in vecinos(conn, 1)] == [tercero]
