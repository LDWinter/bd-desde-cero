# POST /api/import, DELETE /api/data y tipos libres
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent.parent))

import pytest  # noqa: E402

import semilla  # noqa: E402
from app import crear_app  # noqa: E402

EJEMPLO = json.loads((pathlib.Path(__file__).resolve().parents[2] / "docs" / "ejemplo-import.json").read_text())


@pytest.fixture
def cliente():
    app = crear_app(":memory:")
    semilla.cargar(app.config["CONN"])
    app.config["CONN"].commit()  # cargar() no hace commit: sin esto, un rollback del import también borra la semilla
    c = app.test_client()
    c.post("/api/auth/login", json={"email": semilla.USUARIO_PRUEBA["email"],
                                    "password": semilla.USUARIO_PRUEBA["clave"]})
    return c


def test_importar_ejemplo_reemplaza_todo(cliente):
    res = cliente.post("/api/import", json=EJEMPLO)
    assert res.status_code == 201, res.get_json()
    cuerpo = res.get_json()
    assert (cuerpo["entities"], cuerpo["relationships"]) == (7, 7)
    entidades = cliente.get("/api/entities").get_json()
    assert sorted(e["name"] for e in entidades) == sorted(e["name"] for e in EJEMPLO["entities"])
    assert len(cliente.get("/api/relationships").get_json()) == 7
    assert cuerpo["ids"]["ana"] in {e["id"] for e in entidades}


def test_importar_sin_replace_suma_y_usa_ids_existentes(cliente):
    antes = len(cliente.get("/api/entities").get_json())
    res = cliente.post("/api/import", json={
        "entities": [{"id": "x", "type": "Persona", "name": "Xime"}],
        "relationships": [{"sourceId": "x", "targetId": "cli-1", "type": "conoce a"}],
    })
    assert res.status_code == 201, res.get_json()
    assert len(cliente.get("/api/entities").get_json()) == antes + 1
    historial = cliente.get("/api/entities/cli-1/history").get_json()
    assert historial[0]["accion"] == "relacionar"


def test_referencia_inexistente_no_guarda_nada(cliente):
    antes = cliente.get("/api/entities").get_json()
    res = cliente.post("/api/import", json={
        "replace": True,
        "entities": [{"id": "a", "type": "Persona", "name": "A"}],
        "relationships": [{"sourceId": "a", "targetId": "nadie", "type": "x"}],
    })
    assert res.status_code == 400
    assert "nadie" in res.get_json()["error"]
    assert cliente.get("/api/entities").get_json() == antes


def test_relacion_duplicada_hace_rollback(cliente):
    antes = cliente.get("/api/entities").get_json()
    rel = {"sourceId": "a", "targetId": "b", "type": "x"}
    res = cliente.post("/api/import", json={
        "entities": [{"id": "a", "type": "T", "name": "A"}, {"id": "b", "type": "T", "name": "B"}],
        "relationships": [rel, rel],
    })
    assert res.status_code == 400
    assert cliente.get("/api/entities").get_json() == antes


def test_importar_sin_login_da_401():
    app = crear_app(":memory:")
    assert app.test_client().post("/api/import", json=EJEMPLO).status_code == 401


def test_vaciar_datos(cliente):
    assert cliente.delete("/api/data").status_code == 204
    assert cliente.get("/api/entities").get_json() == []
    assert cliente.get("/api/relationships").get_json() == []
    assert cliente.get("/api/sources").get_json() == []
    assert cliente.get("/api/auth/me").status_code == 200  # los usuarios no se borran


def test_tipo_nuevo_por_post(cliente):
    res = cliente.post("/api/entities", json={"type": " Persona ", "name": "Ana"})
    assert res.status_code == 201
    assert res.get_json()["type"] == "Persona"
    assert cliente.post("/api/entities", json={"type": "x" * 41, "name": "A"}).status_code == 400


def test_borrar_fuente_con_sus_nodos_y_conexiones(cliente):
    fuentes = {f["name"]: f for f in cliente.get("/api/sources").get_json()}
    fuente = fuentes["clientes_2025.xlsx"]
    assert cliente.delete(f"/api/sources/{fuente['id']}").status_code == 204
    entidades = cliente.get("/api/entities").get_json()
    assert all(e["source"] != "clientes_2025.xlsx" for e in entidades)
    ids = {e["id"] for e in entidades}
    assert all(r["sourceId"] in ids and r["targetId"] in ids for r in cliente.get("/api/relationships").get_json())
    assert "clientes_2025.xlsx" not in {f["name"] for f in cliente.get("/api/sources").get_json()}
    assert cliente.delete(f"/api/sources/{fuente['id']}").status_code == 404


def test_ejemplo_obras_importa(cliente):
    obras = json.loads((pathlib.Path(__file__).resolve().parents[2] / "docs" / "ejemplo-obras.json").read_text())
    res = cliente.post("/api/import", json=obras)
    assert res.status_code == 201, res.get_json()
    assert (res.get_json()["entities"], res.get_json()["relationships"]) == (34, 41)
