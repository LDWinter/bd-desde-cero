# T24 — tope de 5 por nodo, los 5 tipos de cambio y rollback
# Listo cuando: pytest en verde
import sqlite3

import pytest


from historial import HISTORIAL_MAX, historial_de, registrar
from nodos import borrar_nodo, crear_nodo, editar_nodo, obtener_nodo
from relaciones import desrelacionar, relacionar


def cantidad(conn, nodo_id):
    return conn.execute("SELECT COUNT(*) FROM historial WHERE nodo_id = ?", (nodo_id,)).fetchone()[0]


# ---- registrar / historial_de ----
def test_registrar_y_leer(conn):
    with conn:
        registrar(conn, 1, 1, "editar", {"name": "viejo"}, {"name": "nuevo"})
    cambios = historial_de(conn, 1)
    assert len(cambios) == 1
    assert cambios[0]["accion"] == "editar"
    assert '"nuevo"' in cambios[0]["despues"]


def test_registrar_accion_invalida_falla(conn):
    with pytest.raises(ValueError):  # historial.py valida la acción antes de tocar la base
        registrar(conn, 1, 1, "inventada", None, None)


def test_historial_del_mas_nuevo_al_mas_viejo(conn):
    with conn:
        for i in range(3):
            registrar(conn, 1, 1, "editar", None, {"vuelta": i})
    assert [c["despues"] for c in historial_de(conn, 1)] == ['{"vuelta": 2}', '{"vuelta": 1}', '{"vuelta": 0}']


# ---- purga: tope de 5 por nodo ----
def test_tope_de_5_por_nodo_sin_tocar_otros(conn):
    with conn:
        for i in range(8):
            registrar(conn, 1, 1, "editar", None, {"vuelta": i})
        for i in range(3):
            registrar(conn, 2, 1, "editar", None, {"vuelta": i})
    assert HISTORIAL_MAX == 5
    assert cantidad(conn, 1) == 5
    assert cantidad(conn, 2) == 3
    # quedan los 5 más nuevos (vueltas 7 a 3)
    assert historial_de(conn, 1)[0]["despues"] == '{"vuelta": 7}'
    assert historial_de(conn, 1)[-1]["despues"] == '{"vuelta": 3}'


# ---- los 5 tipos de cambio (T22 y T22b) ----
def test_crear_editar_borrar_quedan_en_el_historial(conn):
    nodo = crear_nodo(conn, "Cliente", "Nuevo", "Base ventas", {"ciudad": "Rosario"}, 1)
    editar_nodo(conn, nodo, 1, nombre="Nuevo SRL")
    borrar_nodo(conn, nodo, 1)
    acciones = [c["accion"] for c in historial_de(conn, nodo)]
    assert acciones == ["borrar", "editar", "crear"]
    editar = historial_de(conn, nodo)[1]
    assert '"Nuevo"' in editar["antes"] and '"Nuevo SRL"' in editar["despues"]


def test_relacionar_y_desrelacionar_en_los_dos_nodos(conn):
    relacionar(conn, 1, 2, "compró", 1)
    desrelacionar(conn, 1, 2, "compró", 1)
    for nodo in (1, 2):
        assert [c["accion"] for c in historial_de(conn, nodo)] == ["desrelacionar", "relacionar"]


# ---- rollback: si algo falla a mitad, no queda nada ----
def test_rollback_si_falla_registrar_al_crear(conn, monkeypatch):
    import nodos

    def registrar_que_falla(*args):
        raise sqlite3.OperationalError("falla simulada")

    monkeypatch.setattr(nodos, "registrar", registrar_que_falla)  # el INSERT del nodo sí anda; falla después
    antes = conn.execute("SELECT COUNT(*) FROM nodos").fetchone()[0]
    with pytest.raises(sqlite3.OperationalError):
        crear_nodo(conn, "Cliente", "Fantasma", "Base ventas", {}, 1)
    assert conn.execute("SELECT COUNT(*) FROM nodos").fetchone()[0] == antes


def test_rollback_si_falla_registrar_al_editar(conn):
    with pytest.raises(sqlite3.IntegrityError):
        editar_nodo(conn, 1, 999, nombre="No tiene que quedar")
    assert obtener_nodo(conn, 1)["titulo"] == "Nodo uno"
    assert cantidad(conn, 1) == 0


def test_rollback_si_falla_registrar_al_relacionar(conn):
    with pytest.raises(sqlite3.IntegrityError):
        relacionar(conn, 1, 2, "compró", 999)
    assert conn.execute("SELECT COUNT(*) FROM relaciones").fetchone()[0] == 0
