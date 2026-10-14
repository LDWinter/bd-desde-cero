# T14 - Fixture `conn`: una base en memoria, con el esquema y datos minimos.
import sys
from pathlib import Path

import pytest

# Para poder hacer `from db import ...` desde back/tests/ sin tocar nada mas
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from db import conectar, crear_esquema  # noqa: E402

AHORA = "2026-10-11T10:00:00"


@pytest.fixture
def conn():
    """Base en memoria nueva para cada test.

    Datos minimos, con ids fijos para que los tests sean predecibles:
      tipos_nodo: 1 = Cliente
      fuentes:    1 = fuente de prueba
      usuarios:   1 = prueba@local
      nodos:      1 y 2 (los dos de tipo Cliente, fuente 1, creados por el usuario 1)
    """
    conn = conectar(":memory:")
    crear_esquema(conn)

    with conn:  # confirma todo junto (commit) al salir
        conn.execute("INSERT INTO tipos_nodo (id, nombre) VALUES (1, 'Cliente')")
        conn.execute(
            "INSERT INTO fuentes (id, nombre, tipo, estado, ultima_sync)"
            " VALUES (1, 'fuente de prueba', 'Excel', 'ok', ?)",
            (AHORA,),
        )
        conn.execute(
            "INSERT INTO usuarios (id, email, nombre, hash_clave, rol, creado)"
            " VALUES (1, 'prueba@local', 'Usuario de prueba', 'hash-de-prueba', 'admin', ?)",
            (AHORA,),
        )
        for id_nodo, titulo in ((1, "Nodo uno"), (2, "Nodo dos")):
            conn.execute(
                "INSERT INTO nodos (id, tipo_id, fuente_id, creado_por, titulo, contenido, creado_en)"
                " VALUES (?, 1, 1, 1, ?, '{}', ?)",
                (id_nodo, titulo, AHORA),
            )

    yield conn
    conn.close()
