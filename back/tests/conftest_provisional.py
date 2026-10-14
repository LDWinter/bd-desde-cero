# T14 (B) — fixture conn: base en memoria + esquema + datos mínimos
# COPIA PROVISIONAL de `tests/conftest.py` (tarea de B), escrita por A (14/10) siguiendo la ficha de B para poder probar
# las tareas de A. NO es el archivo de B: cuando B suba `tests/conftest.py`, el código de A usa el de B solo
# (import con respaldo) y esta copia se puede borrar. Mismos nombres de funciones que pide la ficha.
import sys
from pathlib import Path

import pytest

# para que los tests puedan hacer "from db import conectar" (los módulos están en back/)
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import conectar, crear_esquema  # noqa: E402


@pytest.fixture
def conn():
    c = conectar(":memory:")
    crear_esquema(c)
    with c:
        c.executemany("INSERT INTO tipos_nodo (id, nombre) VALUES (?, ?)",
                      [(1, "Cliente"), (2, "Producto"), (3, "Pedido")])
        c.execute("INSERT INTO fuentes (id, nombre, tipo, estado) VALUES (1, 'Base ventas', 'SQL', 'ok')")
        c.execute("INSERT INTO usuarios (id, email, nombre, hash_clave, rol)"
                  " VALUES (1, 'prueba@local', 'Prueba', 'x', 'admin')")
        c.executemany("INSERT INTO nodos (id, tipo_id, fuente_id, titulo, contenido) VALUES (?, ?, 1, ?, ?)",
                      [(1, 1, "Acme S.A.", '{"ciudad": "Córdoba"}'),
                       (2, 2, "Malbec 750 ml", '{"precio": 4500}')])
    yield c
    c.close()


def test_vacio_provisional(conn):
    assert conn
