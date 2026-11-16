"""Prueba de punta a punta sobre una base temporal con la semilla. Uso: python3 back/probar_a.py"""
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
from pathlib import Path

AQUI = Path(__file__).resolve().parent
sys.path.insert(0, str(AQUI))

from db import conectar, crear_esquema  # noqa: E402
from formato import id_base  # noqa: E402

fallas = 0


def ver(nombre, condicion):
    global fallas
    print(("OK    " if condicion else "FALLA ") + nombre)
    if not condicion:
        fallas += 1


def lanza(funcion, error=sqlite3.IntegrityError):
    try:
        funcion()
    except error:
        return True
    return False


tmp = tempfile.mkdtemp()
ruta = os.path.join(tmp, "prueba.db")

c = conectar(":memory:")
crear_esquema(c)
crear_esquema(c)  # dos veces sin error
tablas = {f[0] for f in c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
ver("crear_esquema crea las 6 tablas",
    {"tipos_nodo", "fuentes", "usuarios", "nodos", "relaciones", "historial"} <= tablas)
ver("FK activas (un tipo inexistente falla)",
    lanza(lambda: c.execute("INSERT INTO nodos (tipo_id, fuente_id, titulo) VALUES (99, 99, 'x')")))

subprocess.run([sys.executable, str(AQUI / "semilla.py"), ruta], check=True, stdout=subprocess.DEVNULL)
conn = conectar(ruta)

from historial import historial_de  # noqa: E402
from nodos import borrar_nodo, crear_nodo, editar_nodo, listar_nodos, obtener_nodo  # noqa: E402
from relaciones import desrelacionar, relacionar, vecinos  # noqa: E402

nuevo = crear_nodo(conn, "Cliente", "Prueba SRL", "clientes_2025.xlsx", {"ciudad": "Salta"}, 1)
fila = obtener_nodo(conn, nuevo)
ver("crear_nodo + obtener_nodo devuelve lo mismo",
    fila["titulo"] == "Prueba SRL" and fila["tipo"] == "Cliente" and '"Salta"' in fila["contenido"])
ver("id inexistente → None", obtener_nodo(conn, 9999) is None)

ver("listar_nodos() = 15 (14 de la semilla + 1)", len(listar_nodos(conn)) == 15)
ver("listar_nodos('Cliente') = 5", len(listar_nodos(conn, "Cliente")) == 5)
ver("editar_nodo cambia el nombre",
    editar_nodo(conn, nuevo, 1, nombre="Prueba SA") and obtener_nodo(conn, nuevo)["titulo"] == "Prueba SA")
ver("editar un id inexistente → False", editar_nodo(conn, 9999, 1, nombre="x") is False)
borrar_nodo(conn, nuevo, 1)
ver("borrado: no aparece en obtener ni en listar",
    obtener_nodo(conn, nuevo) is None and len(listar_nodos(conn)) == 14)
ver("borrado lógico: la fila sigue con borrado = 1",
    conn.execute("SELECT borrado FROM nodos WHERE id = ?", (nuevo,)).fetchone()[0] == 1)

ver("vecinos(2) = pedidos 10 y 11", [f["vecino_id"] for f in vecinos(conn, 2)] == [10, 11])
relacionar(conn, 1, 2, "conoce a", 1)
ver("relacionar agrega el vecino", 2 in [f["vecino_id"] for f in vecinos(conn, 1)])
ver("relación duplicada → IntegrityError", lanza(lambda: relacionar(conn, 1, 2, "conoce a", 1)))
ver("lazo → IntegrityError", lanza(lambda: relacionar(conn, 1, 1, "conoce a", 1)))

editar_nodo(conn, 3, 1, data={"email": "info@dcuyo.com", "ciudad": "Mendoza"})
h = historial_de(conn, 3)[0]
ver("editar deja 'antes' y 'después'",
    h["accion"] == "editar" and "Buenos Aires" in h["antes"] and "Mendoza" in h["despues"])
ver("si registrar falla, el nodo no cambia",
    lanza(lambda: editar_nodo(conn, 3, 999, nombre="No")) and obtener_nodo(conn, 3)["titulo"] == "Distribuidora Cuyo")
ver("relacionar 1 con 2 queda en el historial de ambos",
    historial_de(conn, 1)[0]["accion"] == "relacionar" and historial_de(conn, 2)[0]["accion"] == "relacionar")
desrelacionar(conn, 1, 2, "conoce a", 1)
ver("desrelacionar también queda en ambos",
    historial_de(conn, 1)[0]["accion"] == "desrelacionar" and historial_de(conn, 2)[0]["accion"] == "desrelacionar")
conn.close()

from app import crear_app  # noqa: E402

api = crear_app(ruta).test_client()

r = api.get("/api/entities")
ver("GET /api/entities = 14 entidades", r.status_code == 200 and len(r.get_json()) == 14)
ver("forma de cli-1 igual al mock",
    r.get_json()[0] == {"id": "cli-1", "type": "Cliente", "name": "Acme S.A.", "source": "clientes_2025.xlsx",
                        "data": {"email": "contacto@acme.com", "ciudad": "Córdoba"}})
ver("GET /api/entities/cli-1 → 200", api.get("/api/entities/cli-1").status_code == 200)
ver("prefijo equivocado (pro-1) → 404", api.get("/api/entities/pro-1").status_code == 404)
ver("GET /api/entities/999 → 404 con {error}",
    api.get("/api/entities/999").status_code == 404 and "error" in api.get("/api/entities/999").get_json())

r = api.get("/api/relationships")
ver("GET /api/relationships = 15", r.status_code == 200 and len(r.get_json()) == 15)
ver("relación con forma igual al mock", r.get_json()[0] == {"sourceId": "ped-9", "targetId": "cli-1", "type": "pertenece a"})

nueva = {"type": "Producto", "name": "Vino rosado", "source": "Base ventas", "data": {"precio": 5000}}
ver("POST /api/entities sin login → 401", api.post("/api/entities", json=nueva).status_code == 401)
ver("Login con prueba@local", api.post("/api/auth/login",
                                      json={"email": "prueba@local", "password": "prueba123"}).status_code == 200)
r = api.post("/api/entities", json=nueva)
ver("POST /api/entities válido → 201 con la Entity", r.status_code == 201 and r.get_json()["name"] == "Vino rosado")
id_nuevo = r.get_json()["id"]
ver("POST /api/entities con datos inválidos → 400",
    api.post("/api/entities", json={"type": " ", "name": "x", "data": {}}).status_code == 400
    and api.post("/api/entities", json={"type": "Cliente", "name": " ", "data": {}}).status_code == 400
    and api.post("/api/entities", json={"type": "Cliente", "name": "x", "data": [1]}).status_code == 400)

nueva["name"] = "Vino rosado 750 ml"
r = api.put(f"/api/entities/{id_nuevo}", json=nueva)
ver("PUT → 200 con el cambio", r.status_code == 200 and r.get_json()["name"] == "Vino rosado 750 ml")
r = api.put(f"/api/entities/{id_nuevo}", json={"type": "Producto", "name": "Vino rosado 750 ml"})
ver("PUT sin data no borra los datos", r.status_code == 200 and r.get_json()["data"] == {"precio": 5000})
ver("PUT inexistente → 404", api.put("/api/entities/cli-999", json=nueva).status_code == 404)
ver("DELETE entidad → 204", api.delete(f"/api/entities/{id_nuevo}").status_code == 204)
ver("DELETE entidad otra vez → 404", api.delete(f"/api/entities/{id_nuevo}").status_code == 404)

rel = {"sourceId": "cli-1", "targetId": "pro-5", "type": "compró"}
ver("POST relación → 201", api.post("/api/relationships", json=rel).status_code == 201)
ver("relación duplicada por API → 409", api.post("/api/relationships", json=rel).status_code == 409)
ver("lazo por API → 409", api.post("/api/relationships",
                              json={"sourceId": "cli-1", "targetId": "cli-1", "type": "x"}).status_code == 409)
ver("relación con nodo inexistente → 404", api.post("/api/relationships", json={**rel, "targetId": "pro-999"}).status_code == 404)
ver("DELETE relación → 204", api.delete("/api/relationships", json=rel).status_code == 204)
ver("DELETE relación otra vez → 404", api.delete("/api/relationships", json=rel).status_code == 404)

conn = conectar(ruta)
acciones = [f["accion"] for f in historial_de(conn, id_base(id_nuevo))]
ver("crear, editar y borrar por API quedan en el historial", acciones == ["borrar", "editar", "editar", "crear"])
conn.close()
shutil.rmtree(tmp)

print()
print("TODO OK" if fallas == 0 else f"{fallas} FALLA(S)")
sys.exit(1 if fallas else 0)
