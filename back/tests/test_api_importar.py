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


def test_ids_y_referencias_invalidas_no_dan_500(cliente):
    enorme = "9" * 30  # no entra en un entero de SQLite
    assert cliente.get(f"/api/entities/cli-{enorme}").status_code == 404
    assert cliente.get(f"/api/entities/cli-{enorme}/history").status_code == 404
    assert cliente.delete(f"/api/sources/{enorme}").status_code == 404
    for ref in ([], {}, 5, None):
        res = cliente.post("/api/import", json={"relationships": [{"sourceId": ref, "targetId": "cli-1", "type": "t"}]})
        assert res.status_code == 400, res.get_json()


def test_borrar_fuente_no_reusa_ids(cliente):
    # si el id se reusara, el historial y el front apuntarían a otro nodo
    viejo = cliente.post("/api/entities", json={"type": "Cliente", "name": "x", "source": "temporal"}).get_json()["id"]
    fuente = {f["name"]: f["id"] for f in cliente.get("/api/sources").get_json()}["temporal"]
    assert cliente.delete(f"/api/sources/{fuente}").status_code == 204
    nuevo = cliente.post("/api/entities", json={"type": "Cliente", "name": "y"}).get_json()["id"]
    assert nuevo != viejo


def test_tipo_con_signos_se_puede_pedir_por_id(cliente):
    # "A/B" daba el id "a/b-1": imposible de pedir por URL
    entidad = cliente.post("/api/entities", json={"type": "A/B", "name": "x"}).get_json()
    assert entidad["id"].startswith("ab-")
    assert cliente.get(f"/api/entities/{entidad['id']}").get_json() == entidad


def test_source_sin_espacios_y_replace_solo_booleano(cliente):
    res = cliente.post("/api/entities", json={"type": "Cliente", "name": "x", "source": " Base ventas "})
    assert res.get_json()["source"] == "Base ventas"  # antes creaba otra fuente, " Base ventas "
    res = cliente.post("/api/import", json={"replace": "true", "entities": [{"id": "a", "type": "T", "name": "A"}]})
    assert res.status_code == 400


def test_base_sin_autoincrement_avisa_al_arrancar(tmp_path, caplog):
    from db import ESQUEMA, conectar
    ruta = str(tmp_path / "vieja.db")
    conn = conectar(ruta)
    conn.executescript(ESQUEMA.read_text(encoding="utf-8").replace("AUTOINCREMENT", ""))
    conn.close()
    crear_app(ruta)
    assert "AUTOINCREMENT" in caplog.text
    caplog.clear()
    crear_app(str(tmp_path / "nueva.db"))
    assert "AUTOINCREMENT" not in caplog.text
