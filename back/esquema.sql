-- Esquema SQLite (compartido: avisar a Oziel antes de tocarlo)
-- Modelo: docs/modelo_relacional.md · Fechas en texto ISO · Las FK necesitan PRAGMA foreign_keys = ON
-- (lo activa db.py en cada conexión; acá también, para probar con: sqlite3 prueba.db < back/esquema.sql)
PRAGMA foreign_keys = ON;

-- T06 (A) tipos_nodo y fuentes — Listo cuando: el script se ejecuta 2 veces sin error
-- Catálogo de tipos de nodo (EntityType del front)
CREATE TABLE IF NOT EXISTS tipos_nodo (
    id     INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre TEXT NOT NULL UNIQUE
);

-- Orígenes de datos (Source del front)
-- tipo: tipo de la fuente (CRM, ERP, CSV) → Source.type; NO es FK a tipos_nodo
-- estado: en minúscula porque el contrato es Source.status: "ok" | "error"
-- ultima_sync: texto ISO o NULL (el CHECK rechaza fechas que SQLite no puede leer)
CREATE TABLE IF NOT EXISTS fuentes (
    id          INTEGER PRIMARY KEY AUTOINCREMENT,
    nombre      TEXT NOT NULL UNIQUE,
    tipo        TEXT NOT NULL,
    estado      TEXT NOT NULL CHECK (estado IN ('ok', 'error')),
    ultima_sync TEXT CHECK (ultima_sync IS NULL OR datetime(ultima_sync) IS NOT NULL)
);

-- T09 (Oziel) usuarios — Listo cuando: rechaza un email repetido
-- (va antes que nodos porque nodos.creado_por la referencia)
CREATE TABLE IF NOT EXISTS usuarios (
    id         INTEGER PRIMARY KEY,
    email      TEXT NOT NULL UNIQUE,
    nombre     TEXT,
    hash_clave TEXT NOT NULL,
    rol        TEXT NOT NULL CHECK (rol IN ('admin', 'editor', 'lector')),
    creado     TEXT DEFAULT (datetime('now'))
);

-- T07 (A) nodos — Listo cuando: rechaza un JSON inválido y un tipo inexistente
CREATE TABLE IF NOT EXISTS nodos (
    id             INTEGER PRIMARY KEY,
    tipo_id        INTEGER NOT NULL REFERENCES tipos_nodo (id),
    fuente_id      INTEGER NOT NULL REFERENCES fuentes (id),
    creado_por     INTEGER REFERENCES usuarios (id),
    titulo         TEXT NOT NULL,
    contenido      TEXT NOT NULL DEFAULT '{}' CHECK (json_valid(contenido)),
    creado_en      TEXT NOT NULL DEFAULT (datetime('now')),
    actualizado_en TEXT,
    borrado        INTEGER NOT NULL DEFAULT 0 CHECK (borrado IN (0, 1))
);

-- T08 (A) relaciones — Listo cuando: rechaza duplicados y lazos
CREATE TABLE IF NOT EXISTS relaciones (
    id         INTEGER PRIMARY KEY,
    origen_id  INTEGER NOT NULL REFERENCES nodos (id),
    destino_id INTEGER NOT NULL REFERENCES nodos (id),
    tipo       TEXT NOT NULL,
    UNIQUE (origen_id, destino_id, tipo),
    CHECK (origen_id <> destino_id)
);

-- T10 (Oziel) historial + índice — Listo cuando: se crea sin error
CREATE TABLE IF NOT EXISTS historial (
    id          INTEGER PRIMARY KEY,
    nodo_id     INTEGER NOT NULL REFERENCES nodos (id),
    usuario_id  INTEGER NOT NULL REFERENCES usuarios (id),
    relacion_id INTEGER REFERENCES relaciones (id) ON DELETE SET NULL,
    accion      TEXT NOT NULL
                CHECK (accion IN ('crear', 'editar', 'borrar', 'relacionar', 'desrelacionar')),
    antes       TEXT CHECK (antes IS NULL OR json_valid(antes)),
    despues     TEXT CHECK (despues IS NULL OR json_valid(despues)),
    fecha       TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE INDEX IF NOT EXISTS idx_historial_nodo_fecha ON historial (nodo_id, fecha);
