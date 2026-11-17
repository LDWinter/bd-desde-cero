from datetime import datetime

import pytest

from test_api_importar import cliente  # noqa: F401  (fixture: app con la semilla y sesión iniciada)

NUEVA = {"type": "Producto", "name": "Vino rosado", "source": "Base ventas", "data": {"precio": 5000}}
REL = {"sourceId": "cli-1", "targetId": "pro-5", "type": "compró"}


def test_listar_y_obtener(cliente):
    entidades = cliente.get("/api/entities").get_json()
    assert len(entidades) == 14
    assert entidades[0] == {"id": "cli-1", "type": "Cliente", "name": "Acme S.A.", "source": "clientes_2025.xlsx",
                            "data": {"email": "contacto@acme.com", "ciudad": "Córdoba"}}
    assert len(cliente.get("/api/entities?type=Cliente").get_json()) == 4
    assert cliente.get("/api/entities/cli-1").get_json() == entidades[0]


@pytest.mark.parametrize("entity_id", ["pro-1", "cli-999", "999", "abc"])
def test_obtener_id_equivocado_da_404(cliente, entity_id):
    res = cliente.get(f"/api/entities/{entity_id}")
    assert res.status_code == 404 and "error" in res.get_json()


def test_crear_editar_y_borrar(cliente):
    creada = cliente.post("/api/entities", json=NUEVA)
    assert creada.status_code == 201
    id_nuevo = creada.get_json()["id"]
    assert creada.get_json() == {**NUEVA, "id": id_nuevo}

    editada = cliente.put(f"/api/entities/{id_nuevo}", json={"type": "Producto", "name": "Vino rosado 750 ml"})
    assert editada.status_code == 200
    assert editada.get_json()["name"] == "Vino rosado 750 ml"
    assert editada.get_json()["data"] == NUEVA["data"]  # PUT sin data conserva los datos

    assert cliente.delete(f"/api/entities/{id_nuevo}").status_code == 204
    assert cliente.get(f"/api/entities/{id_nuevo}").status_code == 404
    assert cliente.delete(f"/api/entities/{id_nuevo}").status_code == 404


def test_put_que_cambia_el_tipo_cambia_el_id(cliente):
    res = cliente.put("/api/entities/cli-1", json={"type": "Producto", "name": "Acme"})
    assert res.get_json()["id"] == "pro-1"
    assert cliente.get("/api/entities/cli-1").status_code == 404


@pytest.mark.parametrize("cuerpo", [
    {"type": " ", "name": "x"},
    {"type": "Cliente", "name": " "},
    {"type": "Cliente", "name": "x", "data": [1]},
    {"type": "Cliente", "name": "x", "data": {"a": True}},
    {"type": "Cliente", "name": "x", "source": ""},
    [],
])
def test_datos_invalidos_dan_400(cliente, cuerpo):
    assert cliente.post("/api/entities", json=cuerpo).status_code == 400
    assert cliente.put("/api/entities/cli-1", json=cuerpo).status_code == 400


def test_editar_o_borrar_inexistente_da_404(cliente):
    assert cliente.put("/api/entities/cli-999", json=NUEVA).status_code == 404
    assert cliente.delete("/api/entities/cli-999").status_code == 404


def test_relacion_crear_duplicar_y_borrar(cliente):
    antes = len(cliente.get("/api/relationships").get_json())
    creada = cliente.post("/api/relationships", json=REL)
    assert creada.status_code == 201 and creada.get_json() == REL
    assert len(cliente.get("/api/relationships").get_json()) == antes + 1
    assert cliente.post("/api/relationships", json=REL).status_code == 409
    assert cliente.post("/api/relationships", json={**REL, "targetId": "cli-1"}).status_code == 409  # lazo
    assert cliente.post("/api/relationships", json={**REL, "targetId": "pro-999"}).status_code == 404
    assert cliente.delete("/api/relationships", json=REL).status_code == 204
    assert cliente.delete("/api/relationships", json=REL).status_code == 404


def test_borrar_entidad_oculta_sus_relaciones(cliente):
    assert cliente.delete("/api/entities/cli-1").status_code == 204
    relaciones = cliente.get("/api/relationships").get_json()
    assert all("cli-1" not in (r["sourceId"], r["targetId"]) for r in relaciones)


def test_escribir_sin_login_da_401(cliente):
    cliente.post("/api/auth/logout")
    assert cliente.post("/api/entities", json=NUEVA).status_code == 401
    assert cliente.put("/api/entities/cli-1", json=NUEVA).status_code == 401
    assert cliente.delete("/api/entities/cli-1").status_code == 401
    assert cliente.post("/api/relationships", json=REL).status_code == 401
    assert cliente.delete("/api/relationships", json=REL).status_code == 401


def test_historial_global(cliente):
    assert cliente.get("/api/history").get_json() == []  # la semilla no deja historial
    id_nuevo = cliente.post("/api/entities", json=NUEVA).get_json()["id"]
    cliente.post("/api/relationships", json=REL)

    cambios = cliente.get("/api/history").get_json()
    assert [c["accion"] for c in cambios] == ["relacionar", "crear"]  # la relación, una sola vez (nodo de origen)
    assert cambios[0]["entityId"] == "cli-1"
    assert cambios[1]["entityId"] == id_nuevo and cambios[1]["entityName"] == "Vino rosado"
    assert set(cambios[0]) == {"accion", "usuario", "antes", "despues", "fecha", "entityId", "entityName"}

    assert len(cliente.get("/api/history?limit=1").get_json()) == 1
    assert len(cliente.get("/api/history?limit=0").get_json()) == 1
    assert len(cliente.get("/api/history?limit=abc").get_json()) == 2
    cliente.post("/api/auth/logout")
    assert cliente.get("/api/history").status_code == 401


def test_fechas_del_nodo_en_la_misma_hora_que_el_historial(cliente):
    cliente.put("/api/entities/cli-1", json={"type": "Cliente", "name": "Acme"})
    fila = cliente.application.config["CONN"].execute("SELECT actualizado_en FROM nodos WHERE id = 1").fetchone()
    fecha = cliente.get("/api/entities/cli-1/history").get_json()[0]["fecha"]
    # antes el nodo quedaba en UTC y el historial en hora local
    assert abs(datetime.fromisoformat(fila["actualizado_en"]) - datetime.fromisoformat(fecha)).total_seconds() < 5
