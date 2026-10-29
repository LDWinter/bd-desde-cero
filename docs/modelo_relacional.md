# Modelo relacional — Knowledge System (T02)

> Diagrama: `docs/der.drawio` (exportado en `docs/der.drawio.png`). Motor: SQLite.
> Convenciones: fechas en texto ISO (`2026-10-05T10:32:00`); los `id` son `INTEGER` en la base
> y la API los entrega como texto al front (T04).

## Resumen de relaciones

| Tabla padre (PK) | Tabla hija (FK) | Cardinalidad | Obligatoria | Significado |
|---|---|---|---|---|
| `tipos_nodo.id` | `nodos.tipo_id` | 1 : N | Sí | Cada nodo es de un tipo; un tipo agrupa muchos nodos |
| `fuentes.id` | `nodos.fuente_id` | 1 : N | Sí | Cada nodo viene de una fuente; una fuente aporta muchos nodos |
| `usuarios.id` | `nodos.creado_por` | 0..1 : N | No | Quién creó el nodo (los importados de una fuente no tienen autor) |
| `nodos.id` | `relaciones.origen_id` | 1 : N | Sí | Un nodo puede ser origen de muchas relaciones |
| `nodos.id` | `relaciones.destino_id` | 1 : N | Sí | Un nodo puede ser destino de muchas relaciones |
| `usuarios.id` | `historial.usuario_id` | 1 : N | Sí | Todo cambio lo hizo un usuario |
| `nodos.id` | `historial.nodo_id` | 1 : N | Sí | Cada nodo tiene su historial (se muestran los últimos 5) |
| `relaciones.id` | `historial.relacion_id` | 0..1 : N | No | Solo en acciones `relacionar` / `desrelacionar` (NULL si la relación ya se borró) |

`relaciones` es una tabla puente de `nodos` consigo misma: resuelve la relación **N : M** entre nodos
(un nodo se relaciona con muchos y es relacionado por muchos) con **dos** FK a `nodos`.

## tipos_nodo
Catálogo de tipos de entidad. Semilla: `Cliente`, `Producto`, `Pedido` (`EntityType` del front).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | Identificador |
| `nombre` | TEXT | NOT NULL, UNIQUE | Nombre del tipo → `Entity.type` |

## fuentes
Orígenes de datos (`Source` del front).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | → `Source.id` |
| `nombre` | TEXT | NOT NULL, UNIQUE | → `Source.name` y `Entity.source` (por eso es único) |
| `tipo` | TEXT | NOT NULL | → `Source.type` (ej. CRM, ERP, CSV) |
| `estado` | TEXT | NOT NULL, CHECK (`ok`, `error`) | → `Source.status` |
| `ultima_sync` | TEXT | ISO, puede ser NULL | → `Source.lastSync` (la API lo manda en ISO, o `null` si es NULL; el front lo formatea) |

`Source.recordCount` **no se guarda**: se calcula con `COUNT(*)` de `nodos` por `fuente_id`,
así nunca queda desactualizado.

## usuarios
Cuentas para el login (cookie de sesión, T04). Columnas según T09.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | Identificador |
| `email` | TEXT | NOT NULL, UNIQUE | Con qué inicia sesión |
| `nombre` | TEXT | NULL | Nombre visible |
| `hash_clave` | TEXT | NOT NULL | Hash de la contraseña (nunca la clave en texto plano) |
| `rol` | TEXT | NOT NULL, CHECK (`admin`, `editor`, `lector`) | Permisos |
| `creado` | TEXT | ISO, DEFAULT `datetime('now')` | Fecha de alta |

## nodos
Entidades del grafo (`Entity` del front).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | → `Entity.id` (como texto en la API) |
| `tipo_id` | INTEGER | FK → `tipos_nodo.id`, NOT NULL | → `Entity.type` (por JOIN) |
| `fuente_id` | INTEGER | FK → `fuentes.id`, NOT NULL | → `Entity.source` (por JOIN, `fuentes.nombre`) |
| `creado_por` | INTEGER | FK → `usuarios.id`, NULL | Autor, si lo creó un usuario |
| `titulo` | TEXT | NOT NULL | → `Entity.name` |
| `contenido` | TEXT | NOT NULL, `CHECK(json_valid(contenido))` | → `Entity.data` (`{clave: texto\|número}`; `'{}'` si está vacío) |
| `creado_en` | TEXT | ISO, NOT NULL | Fecha de alta |
| `actualizado_en` | TEXT | ISO, NULL | Última edición |
| `borrado` | INTEGER | NOT NULL DEFAULT 0 | Borrado lógico (T07): 1 = borrado; la API no lo muestra |

## relaciones
Aristas del grafo (`Relationship` del front).

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | Identificador (lo usa `historial.relacion_id`) |
| `origen_id` | INTEGER | FK → `nodos.id`, NOT NULL | → `Relationship.sourceId` |
| `destino_id` | INTEGER | FK → `nodos.id`, NOT NULL | → `Relationship.targetId` |
| `tipo` | TEXT | NOT NULL | → `Relationship.type` (ej. "compró", "contiene") |

Restricciones de tabla: `UNIQUE(origen_id, destino_id, tipo)` (sin duplicados) y
`CHECK(origen_id <> destino_id)` (sin lazos), según T08.

## historial
Registro de cambios por nodo.

| Campo | Tipo | Restricciones | Descripción |
|---|---|---|---|
| `id` | INTEGER | PK | Identificador (también desempata el orden) |
| `usuario_id` | INTEGER | FK → `usuarios.id`, NOT NULL | Quién hizo el cambio |
| `nodo_id` | INTEGER | FK → `nodos.id`, NOT NULL | Nodo afectado |
| `relacion_id` | INTEGER | FK → `relaciones.id`, NULL, `ON DELETE SET NULL` | Relación afectada (solo `relacionar`/`desrelacionar`) |
| `accion` | TEXT | CHECK (`crear`, `editar`, `borrar`, `relacionar`, `desrelacionar`) | Tipo de cambio |
| `antes` | TEXT | NULL, `CHECK(antes IS NULL OR json_valid(antes))` | Estado previo (NULL en `crear`) |
| `despues` | TEXT | NULL, `CHECK(despues IS NULL OR json_valid(despues))` | Estado nuevo (NULL en `borrar`) |
| `fecha` | TEXT | ISO, NOT NULL DEFAULT `datetime('now')` | Momento del cambio |

Índice `idx_historial_nodo_fecha` en `(nodo_id, fecha)` para traer rápido los últimos `HISTORIAL_MAX = 5` cambios de un nodo (T10).

## Decisiones
- **`contenido` es JSON en texto**: el `data` del front tiene claves libres que cambian según el tipo;
  una columna por clave obligaría a cambiar el esquema cada vez.
- **`recordCount` calculado, no guardado**: evita que el contador y los nodos reales no coincidan.
- **`fuentes.nombre` único**: el front identifica la fuente de un nodo por su nombre (`Entity.source`).
- **Una relación se anota dos veces en `historial`**: una fila con el `nodo_id` del origen y otra con el
  del destino, ambas con el mismo `relacion_id`, porque el cambio afecta a los dos nodos.
- **Borrado lógico de nodos** (`borrado = 1`, T07): el nodo nunca desaparece de la tabla, así que
  `historial.nodo_id` puede ser NOT NULL y el historial no se pierde.
- **`historial.relacion_id` con `ON DELETE SET NULL`**: `desrelacionar` sí borra la fila de `relaciones`;
  el historial queda y el JSON de `antes` conserva cómo era la relación.
- **Recordar `PRAGMA foreign_keys = ON`** en cada conexión: SQLite no controla las FK por defecto.

## Correcciones hechas al diagrama (12/10, segunda revisión)
- El archivo guardado todavía tenía las flechas viejas (draw.io estaba abierto y pisó la primera corrección).
  Se rehízo: todas las flechas salen de la PK y llegan a su FK (`nodos.id` → `origen_id` y `destino_id`,
  `usuarios.id` → `historial.usuario_id`, `relaciones.id` → `historial.relacion_id`) con pata de gallo.
- Se quitó la flecha `relaciones.tipo → historial` (`tipo` es texto, no es clave).
- `usuarios` pasó a las columnas de T09 (`email`, `nombre`, `hash_clave`, `rol`, `creado`).
- Agregados: `nodos.actualizado_en`, `nodos.borrado` (T07), NOT NULL/UNIQUE en el diagrama, restricciones de
  `relaciones`, índice de `historial` y una nota con `recordCount`.
- Respaldo de la versión anterior: `~/Documentos/Asistente/respaldos/der.drawio.2026-10-12-antes-revision`.
