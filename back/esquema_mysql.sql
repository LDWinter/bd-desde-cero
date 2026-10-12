CREATE TABLE IF NOT EXISTS tipos_nodo(
	id INT AUTO_INCREMENT PRIMARY KEY, 
	nombre VARCHAR(100) NOT NULL UNIQUE
    ); 
CREATE TABLE IF NOT EXISTS fuentes(
id INT AUTO_INCREMENT PRIMARY KEY, 
nombre VARCHAR (100) NOT NULL UNIQUE, 
tipo VARCHAR (50) NOT NULL, 
estado VARCHAR (10) NOT NULL CHECK (estado IN ('ok', 'error')),
ultima_sync DATETIME NULL 
);

CREATE TABLE IF NOT EXISTS usuarios(
id INT AUTO_INCREMENT PRIMARY KEY, 
email VARCHAR (250) NOT NULL UNIQUE, 
nombre VARCHAR (100) NULL, 
hash_clave VARCHAR(20) NOT NULL, 
rol VARCHAR (10) NOT NULL CHECK (rol IN ('admin', 'lector''editor')), 
creado DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP
); 
CREATE TABLE IF NOT EXISTS nodos (
id INT AUTO_INCREMENT PRIMARY KEY 
tipo_id INT NOT NULL, 
fuente_id INT NOT NULL, 
creado_por INT NULL, 
titulo VARCHAR (250) NOT NULL, 
creado_en DATETIME NOT NULL DEFAULT CURRENT_TIMEAMP, 
actualizado_en DATETIME NULL, 
borrado TINYINT NOT NULL DEFAULT 0, 
FOREIGN KEY (tipo_id) REFERENCES tipos_nodo(id),
FOREIGN KEY (fuente_id) REFERENCES fuentes (id),
FOREIGN KEY (creado_por) REFERENCES usuarios (id)
);
CREATE TABLE IF NOT EXISTS relaciones (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    origen_id   INT NOT NULL,
    destino_id  INT NOT NULL,
    tipo        VARCHAR(100) NOT NULL,
    UNIQUE (origen_id, destino_id, tipo),
    CHECK (origen_id <> destino_id),
    FOREIGN KEY (origen_id)  REFERENCES nodos(id),
    FOREIGN KEY (destino_id) REFERENCES nodos(id)
);
CREATE TABLE IF NOT EXISTS historial (
    id           INT AUTO_INCREMENT PRIMARY KEY,
    usuario_id   INT NOT NULL,
    nodo_id      INT NOT NULL,
    relacion_id  INT NULL,
    accion       VARCHAR(20) NOT NULL
                 CHECK (accion IN ('crear', 'editar', 'borrar', 'relacionar', 'desrelacionar')),
    antes        JSON NULL,
    despues      JSON NULL,
    fecha        DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
    INDEX idx_historial_nodo_fecha (nodo_id, fecha),
    FOREIGN KEY (usuario_id)  REFERENCES usuarios(id),
    FOREIGN KEY (nodo_id)     REFERENCES nodos(id),
    FOREIGN KEY (relacion_id) REFERENCES relaciones(id)
);