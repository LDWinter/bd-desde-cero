# T14 - Test vacio: solo comprueba que la fixture `conn` funciona.
# (pytest no busca tests dentro de conftest.py, por eso va en su propio archivo)


def test_vacio(conn):
    assert conn
