# T28 (B) — GET /api/sources
# COPIA PROVISIONAL de `rutas_fuentes.py` (tarea de B), escrita por A (15/10) siguiendo la ficha de B para poder probar
# la integración. NO es el archivo de B: cuando B suba `rutas_fuentes.py`, app.py usa el de B y esta copia se puede borrar.
from flask import Blueprint, g, jsonify

try:
    from rutas_auth import requiere_login
except ImportError:
    from rutas_auth_provisional import requiere_login

bp = Blueprint("fuentes", __name__)


@bp.get("/api/sources")
@requiere_login
def get_sources():
    query = """
        SELECT
            f.id,
            f.nombre,
            f.tipo,
            f.estado,
            f.ultima_sync,
            COUNT(n.id) as recordCount
        FROM fuentes f
        LEFT JOIN nodos n ON n.fuente_id = f.id AND n.borrado = 0
        GROUP BY f.id
        ORDER BY f.id
    """
    rows = g.conn.execute(query).fetchall()
    return jsonify([
        {
            "id": row[0],
            "name": row[1],
            "type": row[2],
            "status": row[3],
            "lastSync": row[4],
            "recordCount": row[5]
        } for row in rows
    ])
