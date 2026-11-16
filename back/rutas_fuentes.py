from flask import Blueprint, g, jsonify

bp = Blueprint("fuentes", __name__)

# El filtro de borrados va en el ON y no en un WHERE: asi una fuente sin nodos
# (o con todos borrados) sigue apareciendo, con recordCount = 0.
SELECT_FUENTES = """
    SELECT f.id, f.nombre, f.tipo, f.estado, f.ultima_sync,
           COUNT(n.id) AS cantidad
    FROM fuentes f
    LEFT JOIN nodos n ON n.fuente_id = f.id AND n.borrado = 0
    GROUP BY f.id
    ORDER BY f.id
"""


def _a_source(fila):
    return {
        "id": fila["id"],
        "name": fila["nombre"],
        "type": fila["tipo"],
        "status": fila["estado"],
        "lastSync": fila["ultima_sync"],
        "recordCount": fila["cantidad"],
    }


@bp.route("/api/sources", methods=["GET"])
def listar_fuentes():
    return jsonify([_a_source(f) for f in g.conn.execute(SELECT_FUENTES).fetchall()])
