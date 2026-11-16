# Comprueba la fixture `conn`; va aparte porque pytest no busca tests dentro de conftest.py
def test_vacio(conn):
    assert conn
