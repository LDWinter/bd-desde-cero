# T18 - Tests de las funciones de nodos (codigo de A: T15 y T16).
# Usa la fixture `conn` de conftest.py: ya trae el tipo 1 (Cliente), la fuente
# "fuente de prueba", el usuario 1 y los nodos 1 ("Nodo uno") y 2 ("Nodo dos").
import json
import sqlite3

import pytest

from nodos import borrar_nodo, crear_nodo, editar_nodo, listar_nodos, obtener_nodo

USUARIO = 1
FUENTE = "fuente de prueba"


# ---------------------------------------------------------------- crear_nodo
def test_crear_nodo_funciona(conn):
    nodo_id = crear_nodo(conn, "Cliente", "Nuevo S.A.", FUENTE, {"ciudad": "Mendoza"}, USUARIO)

    fila = obtener_nodo(conn, nodo_id)
    assert nodo_id > 2  # la fixture ya trae los nodos 1 y 2
    assert fila["titulo"] == "Nuevo S.A."
    assert fila["tipo"] == "Cliente"
    assert fila["fuente"] == FUENTE
    assert json.loads(fila["contenido"]) == {"ciudad": "Mendoza"}


def test_crear_nodo_con_tipo_inexistente_falla(conn):
    with pytest.raises(ValueError):
        crear_nodo(conn, "Inventado", "X", FUENTE, {}, USUARIO)
    assert len(listar_nodos(conn)) == 2  # no quedo nada guardado


def test_crear_nodo_con_fuente_nueva_la_crea(conn):
    crear_nodo(conn, "Cliente", "X", "Fuente nueva", {}, USUARIO)
    fila = conn.execute("SELECT tipo, estado FROM fuentes WHERE nombre = 'Fuente nueva'").fetchone()
    assert fila is not None
    assert fila["tipo"] == "Manual"
    assert fila["estado"] == "ok"


# -------------------------------------------------- reglas que pone el esquema
def test_la_base_rechaza_un_json_invalido(conn):
    with pytest.raises(sqlite3.IntegrityError) as error:
        conn.execute(
            "INSERT INTO nodos (tipo_id, fuente_id, creado_por, titulo, contenido, creado_en)"
            " VALUES (1, 1, 1, 'Malo', 'esto no es json', '2026-10-11T10:00:00')"
        )
    assert "CHECK" in str(error.value)


def test_la_base_rechaza_un_tipo_inexistente(conn):
    with pytest.raises(sqlite3.IntegrityError) as error:
        conn.execute(
            "INSERT INTO nodos (tipo_id, fuente_id, creado_por, titulo, contenido, creado_en)"
            " VALUES (999, 1, 1, 'Malo', '{}', '2026-10-11T10:00:00')"
        )
    assert "FOREIGN KEY" in str(error.value)


# ------------------------------------------------------------- obtener_nodo
def test_obtener_nodo_funciona(conn):
    fila = obtener_nodo(conn, 1)
    assert fila["id"] == 1
    assert fila["titulo"] == "Nodo uno"


def test_obtener_nodo_inexistente_devuelve_none(conn):
    assert obtener_nodo(conn, 999) is None


# -------------------------------------------------------------- listar_nodos
def test_listar_nodos_funciona(conn):
    assert [f["id"] for f in listar_nodos(conn)] == [1, 2]
    assert [f["id"] for f in listar_nodos(conn, tipo="Cliente")] == [1, 2]


def test_listar_nodos_de_un_tipo_sin_nodos_devuelve_vacio(conn):
    assert listar_nodos(conn, tipo="Pedido") == []


# --------------------------------------------------------------- editar_nodo
def test_editar_nodo_funciona(conn):
    assert editar_nodo(conn, 1, USUARIO, nombre="Nombre nuevo", data={"a": 1}) is True

    fila = obtener_nodo(conn, 1)
    assert fila["titulo"] == "Nombre nuevo"
    assert json.loads(fila["contenido"]) == {"a": 1}
    actualizado = conn.execute("SELECT actualizado_en FROM nodos WHERE id = 1").fetchone()[0]
    assert actualizado is not None


def test_editar_nodo_sin_pasar_datos_no_cambia_el_resto(conn):
    editar_nodo(conn, 1, USUARIO, nombre="Solo el nombre")
    fila = obtener_nodo(conn, 1)
    assert fila["titulo"] == "Solo el nombre"
    assert fila["tipo"] == "Cliente"
    assert json.loads(fila["contenido"]) == {}


def test_editar_nodo_inexistente_devuelve_false(conn):
    assert editar_nodo(conn, 999, USUARIO, nombre="X") is False


def test_editar_nodo_con_tipo_inexistente_falla_y_no_cambia_nada(conn):
    with pytest.raises(ValueError):
        editar_nodo(conn, 1, USUARIO, nombre="Cambiado", tipo="Inventado")
    assert obtener_nodo(conn, 1)["titulo"] == "Nodo uno"


# -------------------------------------------------------------- borrar_nodo
def test_borrar_nodo_funciona_y_es_logico(conn):
    assert borrar_nodo(conn, 1, USUARIO) is True

    assert obtener_nodo(conn, 1) is None
    assert [f["id"] for f in listar_nodos(conn)] == [2]
    # la fila sigue en la tabla, marcada como borrada
    assert conn.execute("SELECT borrado FROM nodos WHERE id = 1").fetchone()[0] == 1


def test_borrar_nodo_inexistente_o_ya_borrado_devuelve_false(conn):
    assert borrar_nodo(conn, 999, USUARIO) is False
    borrar_nodo(conn, 1, USUARIO)
    assert borrar_nodo(conn, 1, USUARIO) is False
