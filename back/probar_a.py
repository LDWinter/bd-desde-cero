"""Prueba manual de las tareas de A (T13 a T32) sobre una base nueva con la semilla.

Uso (desde la raíz del proyecto, con el entorno virtual activado):
    python3 back/probar_a.py

Crea una base temporal, carga la semilla, prueba las funciones y las rutas, y la borra al final.
Cada línea dice OK o FALLA; termina con un resumen.
"""
import os
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

# ---- T13 ----
c = conectar(":memory:")
crear_esquema(c)
crear_esquema(c)  # dos veces sin error
tablas = {f[0] for f in c.execute("SELECT name FROM sqlite_master WHERE type = 'table'")}
ver("T13 crear_esquema crea las 6 tablas",
    {"tipos_nodo", "fuentes", "usuarios", "nodos", "relaciones", "historial"} <= tablas)
ver("T13 FK activas (un tipo inexistente falla)",
    lanza(lambda: c.execute("INSERT INTO nodos (tipo_id, fuente_id, titulo) VALUES (99, 99, 'x')")))

# semilla en una base de archivo (3 fuentes, 14 nodos, 15 relaciones, usuario 1 = prueba@local)
subprocess.run([sys.executable, str(AQUI / "semilla.py"), ruta], check=True, stdout=subprocess.DEVNULL)
conn = conectar(ruta)

from historial import historial_de  # noqa: E402  (T20, Oziel)
from nodos import borrar_nodo, crear_nodo, editar_nodo, listar_nodos, obtener_nodo  # noqa: E402
from relaciones import desrelacionar, relacionar, vecinos  # noqa: E402

# ---- T15 ----
nuevo = crear_nodo(conn, "Cliente", "Prueba SRL", "clientes_2025.xlsx", {"ciudad": "Salta"}, 1)
fila = obtener_nodo(conn, nuevo)
ver("T15 crear_nodo + obtener_nodo devuelve lo mismo",
    fila["titulo"] == "Prueba SRL" and fila["tipo"] == "Cliente" and '"Salta"' in fila["contenido"])
ver("T15 id inexistente → None", obtener_nodo(conn, 9999) is None)

# ---- T16 ----
ver("T16 listar_nodos() = 15 (14 de la semilla + 1)", len(listar_nodos(conn)) == 15)
ver("T16 listar_nodos('Cliente') = 5", len(listar_nodos(conn, "Cliente")) == 5)
ver("T16 editar_nodo cambia el nombre",
    editar_nodo(conn, nuevo, 1, nombre="Prueba SA") and obtener_nodo(conn, nuevo)["titulo"] == "Prueba SA")
ver("T16 editar un id inexistente → False", editar_nodo(conn, 9999, 1, nombre="x") is False)
borrar_nodo(conn, nuevo, 1)
ver("T16 borrado: no aparece en obtener ni en listar",
    obtener_nodo(conn, nuevo) is None and len(listar_nodos(conn)) == 14)
ver("T16 borrado lógico: la fila sigue con borrado = 1",
    conn.execute("SELECT borrado FROM nodos WHERE id = ?", (nuevo,)).fetchone()[0] == 1)

# ---- T17 ----
ver("T17 vecinos(2) = pedidos 10 y 11", [f["vecino_id"] for f in vecinos(conn, 2)] == [10, 11])
relacionar(conn, 1, 2, "conoce a", 1)
ver("T17 relacionar agrega el vecino", 2 in [f["vecino_id"] for f in vecinos(conn, 1)])
ver("T17 relación duplicada → IntegrityError", lanza(lambda: relacionar(conn, 1, 2, "conoce a", 1)))
ver("T17 lazo → IntegrityError", lanza(lambda: relacionar(conn, 1, 1, "conoce a", 1)))

# ---- T22 / T22b ----
editar_nodo(conn, 3, 1, data={"email": "info@dcuyo.com", "ciudad": "Mendoza"})
h = historial_de(conn, 3)[0]
ver("T22 editar deja 'antes' y 'después'",
    h["accion"] == "editar" and "Buenos Aires" in h["antes"] and "Mendoza" in h["despues"])
ver("T22 si registrar falla, el nodo no cambia",
    lanza(lambda: editar_nodo(conn, 3, 999, nombre="No")) and obtener_nodo(conn, 3)["titulo"] == "Distribuidora Cuyo")
ver("T22b relacionar 1 con 2 queda en el historial de ambos",
    historial_de(conn, 1)[0]["accion"] == "relacionar" and historial_de(conn, 2)[0]["accion"] == "relacionar")
desrelacionar(conn, 1, 2, "conoce a", 1)
ver("T22b desrelacionar también queda en ambos",
    historial_de(conn, 1)[0]["accion"] == "desrelacionar" and historial_de(conn, 2)[0]["accion"] == "desrelacionar")
conn.close()

# ---- T26 a T32: la API con el cliente de prueba de Flask ----
os.environ["DB"] = ruta
from app import crear_app  # T25 (Oziel)

app = crear_app(ruta)
if "auth.login" not in app.view_functions:  # el login (T29/T30) lo hace otra compañera: mientras, la copia provisional
    from back.Revisar.rutas_auth_provisional import bp as bp_auth
    app.register_blueprint(bp_auth)
api = app.test_client()

r = api.get("/api/entities")
ver("T26 GET /api/entities = 14 entidades", r.status_code == 200 and len(r.get_json()) == 14)
ver("T26 forma de cli-1 igual al mock",
    r.get_json()[0] == {"id": "cli-1", "type": "Cliente", "name": "Acme S.A.", "source": "clientes_2025.xlsx",
                        "data": {"email": "contacto@acme.com", "ciudad": "Córdoba"}})
ver("T26 GET /api/entities/cli-1 → 200", api.get("/api/entities/cli-1").status_code == 200)
ver("T26 prefijo equivocado (pro-1) → 404", api.get("/api/entities/pro-1").status_code == 404)
ver("T26 GET /api/entities/999 → 404 con {error}",
    api.get("/api/entities/999").status_code == 404 and "error" in api.get("/api/entities/999").get_json())

r = api.get("/api/relationships")
ver("T27 GET /api/relationships = 15", r.status_code == 200 and len(r.get_json()) == 15)
ver("T27 forma igual al mock", r.get_json()[0] == {"sourceId": "ped-9", "targetId": "cli-1", "type": "pertenece a"})

nueva = {"type": "Producto", "name": "Vino rosado", "source": "Base ventas", "data": {"precio": 5000}}
ver("T31 sin login → 401", api.post("/api/entities", json=nueva).status_code == 401)
ver("Login con prueba@local", api.post("/api/auth/login",
                                      json={"email": "prueba@local", "password": "prueba123"}).status_code == 200)
r = api.post("/api/entities", json=nueva)
ver("T31 POST válido → 201 con la Entity", r.status_code == 201 and r.get_json()["name"] == "Vino rosado")
id_nuevo = r.get_json()["id"]
ver("T31 datos inválidos → 400",
    api.post("/api/entities", json={"type": "Otro", "name": "x", "data": {}}).status_code == 400
    and api.post("/api/entities", json={"type": "Cliente", "name": " ", "data": {}}).status_code == 400
    and api.post("/api/entities", json={"type": "Cliente", "name": "x", "data": [1]}).status_code == 400)

nueva["name"] = "Vino rosado 750 ml"
r = api.put(f"/api/entities/{id_nuevo}", json=nueva)
ver("T32 PUT → 200 con el cambio", r.status_code == 200 and r.get_json()["name"] == "Vino rosado 750 ml")
r = api.put(f"/api/entities/{id_nuevo}", json={"type": "Producto", "name": "Vino rosado 750 ml"})
ver("T32 PUT sin data no borra los datos", r.status_code == 200 and r.get_json()["data"] == {"precio": 5000})
ver("T32 PUT inexistente → 404", api.put("/api/entities/cli-999", json=nueva).status_code == 404)
ver("T32 DELETE → 204", api.delete(f"/api/entities/{id_nuevo}").status_code == 204)
ver("T32 DELETE otra vez → 404", api.delete(f"/api/entities/{id_nuevo}").status_code == 404)

rel = {"sourceId": "cli-1", "targetId": "pro-5", "type": "compró"}
ver("T33 POST relación → 201", api.post("/api/relationships", json=rel).status_code == 201)
ver("T33 duplicada → 409", api.post("/api/relationships", json=rel).status_code == 409)
ver("T33 lazo → 409", api.post("/api/relationships",
                              json={"sourceId": "cli-1", "targetId": "cli-1", "type": "x"}).status_code == 409)
ver("T33 nodo inexistente → 404", api.post("/api/relationships", json={**rel, "targetId": "pro-999"}).status_code == 404)
ver("T33 DELETE → 204", api.delete("/api/relationships", json=rel).status_code == 204)
ver("T33 DELETE otra vez → 404", api.delete("/api/relationships", json=rel).status_code == 404)

conn = conectar(ruta)
acciones = [f["accion"] for f in historial_de(conn, id_base(id_nuevo))]
ver("T31/T32 crear, editar y borrar quedan en el historial", acciones == ["borrar", "editar", "editar", "crear"])
conn.close()

print()
print("TODO OK" if fallas == 0 else f"{fallas} FALLA(S)")
sys.exit(1 if fallas else 0)
