# T36 — tests de API de las rutas de Oziel (T28 a T30, T34) con app.test_client()
# Listo cuando: verde
# Mientras Oziel no suba sus archivos, prueban las copias provisionales (rutas_*_provisional.py)
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

import semilla  # noqa: E402
from app import crear_app  # noqa: E402


@pytest.fixture
def cliente():
    """App con base en memoria cargada con la semilla (datos del mock del front)."""
    app = crear_app(":memory:")
    semilla.cargar(app.config["CONN"])
    return app.test_client()


def test_login_correcto(cliente):
    response = cliente.post("/api/auth/login", json={
        "email": semilla.USUARIO_PRUEBA["email"],
        "password": semilla.USUARIO_PRUEBA["clave"]
    })
    assert response.status_code == 200
    data = response.get_json()
    assert data["email"] == semilla.USUARIO_PRUEBA["email"]


def test_login_clave_mala(cliente):
    response = cliente.post("/api/auth/login", json={
        "email": semilla.USUARIO_PRUEBA["email"],
        "password": "clave_mala"
    })
    assert response.status_code == 401


def test_auth_me_flow(cliente):
    # No login
    res1 = cliente.get("/api/auth/me")
    assert res1.status_code == 401

    # Login
    res2 = cliente.post("/api/auth/login", json={
        "email": semilla.USUARIO_PRUEBA["email"],
        "password": semilla.USUARIO_PRUEBA["clave"]
    })
    assert res2.status_code == 200

    # GET /api/auth/me
    res3 = cliente.get("/api/auth/me")
    assert res3.status_code == 200
    data = res3.get_json()
    assert data["email"] == semilla.USUARIO_PRUEBA["email"]

    # Logout
    res4 = cliente.post("/api/auth/logout")
    assert res4.status_code == 204

    # GET /api/auth/me again
    res5 = cliente.get("/api/auth/me")
    assert res5.status_code == 401


def test_post_entities_no_login(cliente):
    response = cliente.post("/api/entities", json={
        "type": "Cliente",
        "name": "X",
        "data": {},
        "source": "Manual"
    })
    assert response.status_code == 401


def test_get_sources(cliente):
    response = cliente.get("/api/sources")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 3

    expected_counts = {
        "clientes_2025.xlsx": 3,
        "Base ventas": 11,
        "Tablero Proyectos": 0
    }

    # Verify each source has the correct keys and recordCount
    source_map = {s["name"]: s for s in data}
    for name, count in expected_counts.items():
        assert name in source_map
        assert source_map[name]["recordCount"] == count
        assert set(source_map[name].keys()) == {"id", "name", "type", "status", "lastSync", "recordCount"}
        assert source_map[name]["status"] in ("ok", "error")
    # El contrato HTTP usa ISO; el front se ocupa de la presentación local.
    assert source_map["clientes_2025.xlsx"]["lastSync"] == "2026-10-05T10:32:00"


def test_fuente_sin_sincronizar_devuelve_null(cliente):
    with cliente.application.config["CONN"] as conn:
        conn.execute("UPDATE fuentes SET ultima_sync = NULL WHERE id = 1")
    fuente = next(f for f in cliente.get("/api/sources").get_json() if f["id"] == 1)
    assert fuente["lastSync"] is None


def test_historial_usa_ruta_definitiva_e_ids_del_front(cliente):
    rutas = [r for r in cliente.application.url_map.iter_rules() if r.rule.endswith("/history")]
    assert len(rutas) == 1
    _login(cliente)
    relacion = {"sourceId": "cli-1", "targetId": "pro-5", "type": "compró"}
    assert cliente.post("/api/relationships", json=relacion).status_code == 201
    cambio = cliente.get("/api/entities/cli-1/history").get_json()[0]
    assert cambio["accion"] == "relacionar"
    assert cambio["despues"] == relacion


def test_historial_flow(cliente):
    # Login
    cliente.post("/api/auth/login", json={
        "email": semilla.USUARIO_PRUEBA["email"],
        "password": semilla.USUARIO_PRUEBA["clave"]
    })

    # 6 PUTs
    for n in range(1, 7):
        response = cliente.put("/api/entities/cli-1", json={
            "type": "Cliente",
            "name": f"Nombre {n}",
            "data": {}
        })
        assert response.status_code == 200

    # GET history
    response = cliente.get("/api/entities/cli-1/history")
    assert response.status_code == 200
    data = response.get_json()
    assert len(data) == 5

    for item in data:
        assert set(item.keys()) == {"accion", "usuario", "antes", "despues", "fecha"}

    assert data[0]["despues"]["name"] == "Nombre 6"  # el más nuevo primero
    fechas = [item["fecha"] for item in data]
    assert fechas == sorted(fechas, reverse=True)


def test_get_history_not_found(cliente):
    response = cliente.get("/api/entities/cli-99/history")
    assert response.status_code == 404


# ---- Regresiones de rutas_nodos.py encontradas en el análisis del 15/10 (los tests completos son T35) ----

def _login(cliente):
    cliente.post("/api/auth/login", json={
        "email": semilla.USUARIO_PRUEBA["email"],
        "password": semilla.USUARIO_PRUEBA["clave"]
    })


@pytest.mark.parametrize("valor", ["NaN", "Infinity", "-Infinity"])
def test_post_entity_con_numero_no_finito_da_400(cliente, valor):
    # Python acepta NaN en JSON, pero la base no: antes daba 500
    _login(cliente)
    cuerpo = '{"type": "Cliente", "name": "X", "data": {"x": %s}}' % valor
    response = cliente.post("/api/entities", data=cuerpo, content_type="application/json")
    assert response.status_code == 400
    assert "data.x" in response.get_json()["error"]


@pytest.mark.parametrize("cuerpo", [
    {"targetId": "pro-5", "type": "x"},
    {"sourceId": "cli-1", "type": "x"},
    {"sourceId": 1, "targetId": "pro-5", "type": "x"},
])
def test_relacion_sin_ids_da_400(cliente, cuerpo):
    # antes daba 404 "no existe", que confunde al que integra
    _login(cliente)
    for metodo in (cliente.post, cliente.delete):
        response = metodo("/api/relationships", json=cuerpo)
        assert response.status_code == 400
        assert "obligatorios" in response.get_json()["error"]
