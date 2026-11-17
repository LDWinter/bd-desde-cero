# Modelo relacional — Knowledge System

> Diagrama: `docs/der.drawio` (exportado en `docs/der.drawio.png`). Motor: SQLite.
> Convenciones: fechas en texto; los `id` son `INTEGER` en la base y la API entrega los de los nodos
> como texto (`cli-1`). El esquema está en `back/esquema.sql`.

## Resumen de relaciones

| Tabla padre (PK) | Tabla hija (FK) | Cardinalidad | Obligatoria | Significado |
|---|---|---|---|---|
| `tipos_nodo.id` | `nodos.tipo_id` | 1 : N | Sí | Cada nodo es de un tipo; un tipo agrupa muchos nodos |
| `fuentes.id` | `nodos.fuente_id` | 1 : N | Sí | Cada nodo viene de una fuente; una fuente aporta muchos nodos |
| `usuarios.id` | `nodos.creado_por` | 0..1 : N | No | Quién creó el nodo (NULL si no lo creó un usuario) |
| `nodos.id` | `relaciones.origen_id` | 1 : N | Sí | Un nodo puede ser origen de muchas relaciones |
| `nodos.id` | `relaciones.destino_id` | 1 : N | Sí | Un nodo puede ser destino de muchas relaciones |
| `usuarios.id` | `historial.usuario_id` | 1 : N | Sí | Todo cambio lo hizo un usuario |
| `nodos.id` | `historial.nodo_id` | 1 : N | Sí | Cada nodo tiene su historial (se guardan los últimos 5) |
| `relaciones.id` | `historial.relacion_id` | 0..1 : N | No | Columna reservada: hoy el código no la escribe (queda NULL) |

`relaciones` es una tabla puente de `nodos` consigo misma: resuelve la relación **N : M** entre nodos
(un nodo se relaciona con muchos y es relacionado por muchos) con **dos** FK a `nodos`.

## tipos_nodo
Catálogo de tipos de entidad. Los tipos son libres: se crea una fila la primera vez que se usa un tipo.
La semilla trae `Cliente`, `Producto` y `Pedido`.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | Identificador |
| `nombre` | TEXT | NOT NULL, UNIQUE | Nombre del tipo → `Entity.type` |

## fuentes
Orígenes de datos (`Source` del front).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | → `Source.id` |
| `nombre` | TEXT | NOT NULL, UNIQUE | → `Source.name` y `Entity.source` (por eso es único) |
| `tipo` | TEXT | NOT NULL | → `Source.type` (ej. Excel, SQL; `Manual` en las que se crean solas) |
| `estado` | TEXT | NOT NULL, CHECK (`ok`, `error`) | → `Source.status` |
| `ultima_sync` | TEXT | ISO, puede ser NULL | → `Source.lastSync` (la API lo manda en ISO, o `null` si es NULL; el front lo formatea) |

`Source.recordCount` **no se guarda**: se calcula contando los `nodos` no borrados de cada `fuente_id`,
así nunca queda desactualizado.

## usuarios
Cuentas para el login (cookie de sesión).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | Identificador |
| `email` | TEXT | NOT NULL, UNIQUE | Con qué inicia sesión |
| `nombre` | TEXT | NULL | Nombre visible |
| `hash_clave` | TEXT | NOT NULL | Hash de la contraseña (nunca la clave en texto plano) |
| `rol` | TEXT | NOT NULL, CHECK (`admin`, `editor`, `lector`) | Permisos |
| `creado` | TEXT | DEFAULT `datetime('now')` | Fecha de alta (el código la guarda en ISO, hora local) |

## nodos
Entidades del grafo (`Entity` del front).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK AUTOINCREMENT | → `Entity.id` (como texto en la API). No se reutiliza: el historial de un nodo eliminado nunca pasa a otro |
| `tipo_id` | INTEGER | FK → `tipos_nodo.id`, NOT NULL | → `Entity.type` (por JOIN) |
| `fuente_id` | INTEGER | FK → `fuentes.id`, NOT NULL | → `Entity.source` (por JOIN, `fuentes.nombre`) |
| `creado_por` | INTEGER | FK → `usuarios.id`, NULL | Autor, si lo creó un usuario |
| `titulo` | TEXT | NOT NULL | → `Entity.name` |
| `contenido` | TEXT | NOT NULL, `CHECK(json_valid(contenido))` | → `Entity.data` (`{clave: texto\|número}`; `'{}'` si está vacío) |
| `creado_en` | TEXT | NOT NULL DEFAULT `datetime('now')` | Fecha de alta (el código la guarda en ISO, hora local) |
| `actualizado_en` | TEXT | NULL | Última edición o borrado (ISO, hora local) |
| `borrado` | INTEGER | NOT NULL DEFAULT 0, CHECK (0, 1) | Borrado lógico: 1 = borrado; la API no lo muestra |

## relaciones
Aristas del grafo (`Relationship` del front).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | Identificador |
| `origen_id` | INTEGER | FK → `nodos.id`, NOT NULL | → `Relationship.sourceId` |
| `destino_id` | INTEGER | FK → `nodos.id`, NOT NULL | → `Relationship.targetId` |
| `tipo` | TEXT | NOT NULL | → `Relationship.type` (ej. "compró", "contiene") |

Restricciones de tabla: `UNIQUE(origen_id, destino_id, tipo)` (sin duplicados) y
`CHECK(origen_id <> destino_id)` (sin lazos).

## historial
Registro de cambios por nodo.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | Identificador (también desempata el orden) |
| `usuario_id` | INTEGER | FK → `usuarios.id`, NOT NULL | Quién hizo el cambio |
| `nodo_id` | INTEGER | FK → `nodos.id`, NOT NULL | Nodo afectado |
| `relacion_id` | INTEGER | FK → `relaciones.id`, NULL, `ON DELETE SET NULL` | Reservada: hoy el código no la escribe |
| `accion` | TEXT | CHECK (`crear`, `editar`, `borrar`, `relacionar`, `desrelacionar`) | Tipo de cambio |
| `antes` | TEXT | NULL, `CHECK(antes IS NULL OR json_valid(antes))` | Estado previo (NULL en `crear`) |
| `despues` | TEXT | NULL, `CHECK(despues IS NULL OR json_valid(despues))` | Estado nuevo (NULL en `borrar`) |
| `fecha` | TEXT | NOT NULL DEFAULT `datetime('now')` | Momento del cambio (el código la guarda en ISO, hora local: `2026-10-05T10:32:00`) |

Índice `idx_historial_nodo_fecha` en `(nodo_id, fecha)` para traer rápido los últimos `HISTORIAL_MAX = 5` cambios de un nodo.
Índices en `relaciones (destino_id)`, `historial (relacion_id)` y `nodos (fuente_id)`: sin ellos, borrar una fuente
recorre tablas enteras por cada fila.

## Decisiones
- **`contenido` es JSON en texto**: el `data` del front tiene claves libres que cambian según el tipo;
  una columna por clave obligaría a cambiar el esquema cada vez.
- **`recordCount` calculado, no guardado**: evita que el contador y los nodos reales no coincidan.
- **`fuentes.nombre` único**: el front identifica la fuente de un nodo por su nombre (`Entity.source`).
- **Una relación se anota dos veces en `historial`**: una fila con el `nodo_id` del origen y otra con el
  del destino, porque el cambio afecta a los dos nodos. La relación queda descripta en el JSON de `antes` / `despues`.
- **Borrado lógico de nodos** (`borrado = 1`): al borrar una entidad el nodo queda en la tabla, así que
  `historial.nodo_id` puede ser NOT NULL y el historial no se pierde. Borrar una fuente o vaciar los datos sí
  elimina los nodos, junto con su historial y sus relaciones.
- **`nodos.id` con `AUTOINCREMENT`**: un id eliminado no se reutiliza, así el historial de otros nodos nunca
  termina apuntando a un nodo distinto.
- **`desrelacionar` sí borra la fila de `relaciones`**: el historial queda y el JSON de `antes` conserva cómo
  era la relación.
- **Recordar `PRAGMA foreign_keys = ON`** en cada conexión: SQLite no controla las FK por defecto.
