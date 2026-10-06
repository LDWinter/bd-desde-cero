# Base de datos desde cero — Plan de aprendizaje

**Para:** Metodología y Testing (3.er semestre).
**Objetivo:** que **vos** construyas, entiendas y puedas explicar la base de datos del proyecto (lotes,
relaciones y registro) y su conexión con Python. Empezamos desde cero y avanzamos un paso por vez.
**Al terminar vas a saber:** diseñar tablas, escribir SQL, relacionar tablas, conectar Python a la base,
hacer el CRUD completo, llevar un registro de cambios y **probar** todo con tests.

---

## Cómo vamos a trabajar

1. Cada **etapa** tiene: qué vas a aprender, los conceptos, los pasos, un **ejercicio** y una forma de
   **comprobar** que te salió bien.
2. **Vos escribís el código.** Yo te explico, te reviso y te ayudo cuando te trabás. No hay que copiar y pegar:
   escribirlo a mano es lo que hace que se aprenda.
3. Al final de cada etapa corrés el verificador: `python3 verificar.py 3` (por ejemplo, para la etapa 3).
   El verificador se va ampliando: cada etapa se agrega cuando vemos su lección.
   Si sale todo en verde, pasás a la siguiente.
4. Cuando algo no se entienda, me preguntás con la lección y la parte exacta ("etapa 4, paso 3, no entiendo el JOIN").
5. Cada etapa termina con un **commit** en Git, así queda el registro de tu avance para la materia.

> 📁 Carpeta de trabajo: `~/Proyectos/bd-desde-cero/`. Cada etapa tiene su subcarpeta (`etapa-01/`, `etapa-02/`…).
> El proyecto que armé antes (`~/Proyectos/gestion-nodos`) queda como **solución de referencia**. No lo mires
> hasta terminar cada etapa. Después sí: comparar tu versión con otra es una buena forma de aprender.

**Ritmo sugerido:** 2 o 3 sesiones por semana de 1 a 2 horas, con una etapa por sesión. En total son entre 4 y 6 semanas.

---

## Mapa del recorrido

```
 PARTE A — SQL puro (sin programar)          PARTE B — Python + base         PARTE C — Calidad
 ┌─────────────────────────────────┐        ┌──────────────────────────┐    ┌──────────────────┐
 │ 0 Preparar el entorno           │        │ 6 Conectar Python        │    │ 9  Tests (pytest)│
 │ 1 Pensar los datos (en papel)   │  ───▶  │ 7 CRUD en funciones      │──▶ │ 10 Consultas de  │
 │ 2 Crear tablas                  │        │ 8 Registro y transacción │    │    grafo         │
 │ 3 Insertar y consultar (CRUD)   │        └──────────────────────────┘    │ 11 Módulos y     │
 │ 4 Relacionar tablas (FK, JOIN)  │                                        │    entrega       │
 │ 5 Guardar JSON en la base       │                                        └──────────────────┘
 └─────────────────────────────────┘
```

---

## PARTE A — SQL puro

### Etapa 0 · Preparar el entorno  *(30 min)*
**Aprendés:** qué herramientas se usan y para qué sirve cada una.
- **Python 3**: ya está instalado (`python3 --version`).
- **VS Code**: donde vas a escribir.
- **DB Browser for SQLite**: un programa para **ver y tocar la base de datos con el mouse**, como si fuera un
  Excel. Es ideal para aprender, porque ves las tablas mientras las creás.
  Instalación sin contraseña: `flatpak install --user -y flathub org.sqlitebrowser.sqlitebrowser`
- **Git**: para guardar el avance (`git init` en la carpeta).

**Ejercicio:** abrí DB Browser, creá una base nueva `practica.db` dentro de `etapa-00/` y cerrala.
**Comprobar:** `python3 verificar.py 0` → encuentra `etapa-00/practica.db`.

---

### Etapa 1 · Pensar los datos antes de tocar la compu  *(1 h)*
**Aprendés:** el **modelo de datos**, es decir, cómo traducir una idea a tablas.
**Conceptos:** entidad, atributo, tabla, fila, columna, **clave primaria (PK)**, tipos de dato, cardinalidad
(1 a 1, 1 a muchos, muchos a muchos), **diagrama entidad-relación (DER)**.

**Pasos:**
1. Hacé una lista de las "cosas" del sistema: *tipo de lote*, *lote*, *relación entre lotes* y *registro de cambios*.
2. Para cada una, anotá qué datos tiene. Por ejemplo, un lote tiene un título, un tipo, un contenido y una fecha.
3. Pensá cómo se conectan. Un tipo tiene **muchos** lotes y un lote puede unirse con **muchos** lotes.
4. Dibujá el DER en papel o en [draw.io](https://app.diagrams.net).

**Ejercicio:** entregá `etapa-01/modelo.md` con las 4 tablas, sus columnas y el tipo de cada columna,
más una foto o archivo del DER.
**Comprobar:** lo revisamos juntos. No hay una única respuesta correcta, pero sí hay errores típicos que vamos a evitar.

---

### Etapa 2 · Crear las tablas  *(1 h)*
**Aprendés:** `CREATE TABLE` y las reglas de una tabla.
**Conceptos:** tipos de SQLite (`INTEGER`, `TEXT`, `REAL`), `PRIMARY KEY`, `NOT NULL`, `DEFAULT`, `UNIQUE`,
`CHECK` y `CURRENT_TIMESTAMP`.

**Pasos:**
1. En DB Browser, pestaña *Ejecutar SQL*, escribí tu primera tabla:
   ```sql
   CREATE TABLE tipos_lote (
       id     INTEGER PRIMARY KEY,
       nombre TEXT NOT NULL UNIQUE
   );
   ```
2. Mirá la pestaña *Estructura*: ahí está tu tabla.
3. Ahora escribí **vos** la tabla `lotes` a partir de tu modelo de la etapa 1.
4. Guardá todo el SQL en `etapa-02/esquema.sql`. Ese archivo es tu "plano" de la base.

**Ejercicio:** `esquema.sql` con `tipos_lote` y `lotes`. Que se pueda ejecutar 2 veces sin error
(pista: `IF NOT EXISTS`).
**Comprobar:** `python3 verificar.py 2` → crea una base con tu archivo y revisa columnas y reglas.

---

### Etapa 3 · Insertar y consultar: el CRUD en SQL  *(1,5 h)*
**Aprendés:** las 4 operaciones básicas.
**Conceptos:** `INSERT`, `SELECT`, `WHERE`, `ORDER BY`, `LIMIT`, `COUNT`, `UPDATE` y `DELETE`, y por qué
nunca hay que olvidar el `WHERE` en un `UPDATE` o un `DELETE`.

**Pasos:**
1. Insertá 2 tipos (`cliente`, `factura`) y 5 lotes.
2. Practicá consultas: todos los lotes, los de un tipo, ordenados por título, cuántos hay de cada tipo.
3. Cambiá el título de un lote con `UPDATE`. Borrá uno con `DELETE` y mirá qué pasó.

**Ejercicio:** `etapa-03/consultas.sql` con 10 consultas pedidas (te las paso en la lección), cada una con un
comentario que explique qué hace.
**Comprobar:** `python3 verificar.py 3` → ejecuta tus consultas y compara los resultados.

---

### Etapa 4 · Relacionar tablas  *(2 h)*: la etapa más importante
**Aprendés:** cómo se "conectan" las tablas: la base de todo lo "basado en nodos".
**Conceptos:** **clave foránea (FK)** (`REFERENCES`), `PRAGMA foreign_keys = ON`, **JOIN** (`INNER` y `LEFT`),
la tabla intermedia para relaciones **muchos a muchos**, la autorrelación (lote ↔ lote), `UNIQUE` compuesto
y `CHECK (origen_id <> destino_id)`.

**Pasos:**
1. Conectá `lotes.tipo_id` con `tipos_lote.id` usando una FK y probá insertar un lote con un tipo inexistente.
   Vas a ver un error, y eso es lo correcto.
2. Hacé un `JOIN` para mostrar cada lote con el **nombre** de su tipo.
3. Creá la tabla `relaciones (origen_id, destino_id, tipo)`. Cada fila es una **flecha** del grafo.
4. Uní lotes entre sí y consultá: "¿con qué lotes está unido el lote 1?" (dos JOIN).

**Ejercicio:** `esquema.sql` con las 3 tablas + `etapa-04/consultas.sql` con las consultas de vecinos.
**Comprobar:** `python3 verificar.py 4` → prueba que la base rechace lo inválido (FK, duplicados, lazos).

---

### Etapa 5 · Guardar información flexible en JSON  *(1 h)*
**Aprendés:** por qué el contenido de un lote va en una columna JSON y cómo consultarlo.
**Conceptos:** JSON, `TEXT` con JSON adentro, `json_extract()` y `json_valid()` de SQLite, y las ventajas y
desventajas frente a tener columnas fijas.

**Pasos:**
1. Guardá el contenido de un lote como `{"razon_social": "Acme", "empleados": 12}`.
2. Consultá: "los clientes con más de 10 empleados" usando `json_extract(contenido, '$.empleados')`.
3. Agregá `CHECK (json_valid(contenido))` para que la base rechace texto que no sea JSON.

**Ejercicio y comprobación:** `python3 verificar.py 5`.

> 🎯 **Fin de la Parte A:** tenés la base completa diseñada y probada **solo con SQL**.

---

## PARTE B — Conectar Python con la base

### Etapa 6 · La primera conexión desde Python  *(1,5 h)*
**Aprendés:** cómo un programa le habla a la base.
**Conceptos:** el módulo `sqlite3`, `connect()`, `execute()`, `fetchone()`/`fetchall()`, `commit()` y `close()`,
`row_factory` (leer por nombre de columna) y los **parámetros `?`** contra la **inyección SQL** (seguridad, muy importante).

**Pasos:**
1. `etapa-06/conexion.py`: abrir la base, crear las tablas leyendo tu `esquema.sql` y cerrar.
2. Insertar un tipo y un lote desde Python y verlos en DB Browser.
3. Ver con un ejemplo por qué `f"... WHERE titulo = '{titulo}'"` es peligroso y `"... WHERE titulo = ?"` no.

**Ejercicio:** función `conectar(ruta)` y función `crear_esquema(conn)`.
**Comprobar:** `python3 verificar.py 6`.

---

### Etapa 7 · El CRUD en funciones  *(2 h)*
**Aprendés:** a encapsular el SQL en funciones con nombres claros, el patrón **repositorio**.
**Conceptos:** funciones, parámetros, `return`, diccionarios, `json.dumps`/`json.loads`, `lastrowid` y
errores (`raise ValueError`).

**Pasos:** escribir en `etapa-07/repositorio.py`:
`crear_tipo`, `crear_lote`, `obtener_lote`, `listar_lotes`, `editar_lote`, `borrar_lote` (borrado lógico),
`relacionar`, `vecinos`.

**Ejercicio y comprobación:** `python3 verificar.py 7` → prueba cada función.

---

### Etapa 8 · El registro de cambios y las transacciones  *(1,5 h)*
**Aprendés:** la **trazabilidad**: que cada cambio deje rastro y que nunca quede "a medias".
**Conceptos:** la tabla `registro`, guardar el "antes" y el "después", **transacción**, `commit` y `rollback`
y la **atomicidad** (o se hace todo o no se hace nada).

**Pasos:**
1. Tabla `registro (fecha, usuario, accion, lote_id, detalle)`.
2. Que cada función que modifica algo escriba en el registro **dentro de la misma transacción**.
3. Provocar un error a mitad de camino y comprobar que con `rollback` no quedó nada guardado.

**Comprobar:** `python3 verificar.py 8`.

> 🎯 **Fin de la Parte B:** tu base y tu código Python funcionan juntos y todo queda registrado.

---

## PARTE C — Calidad (lo central de la materia)

### Etapa 9 · Probar todo con tests  *(2 h)*
**Aprendés:** a escribir **tus propios tests**, no solo a correr los míos.
**Conceptos:** `pytest`, `assert`, `pytest.raises`, **fixtures**, la base en memoria (`":memory:"`),
el patrón Preparar → Actuar → Verificar, los tests unitarios frente a los de integración, la cobertura y
**TDD** (test → código → refactor).

**Pasos:** reemplazar `verificar.py` por **tus** tests en `tests/`: uno por función, más los casos de error.

**Comprobar:** `pytest -v` en verde y `pytest --cov` con más del 90 % de cobertura.

---

### Etapa 10 · Consultas de grafo  *(1,5 h)*
**Aprendés:** a recorrer la red de lotes con SQL.
**Conceptos:** `UNION`, `WITH` (CTE) y **`WITH RECURSIVE`**: "todos los lotes a los que se llega desde el lote 1",
caminos y profundidad.

**Ejercicio y comprobación:** función `alcanzables(conn, lote_id)` con su test.

---

### Etapa 11 · Ordenar en módulos y entregar  *(2 h)*
**Aprendés:** a organizar el código para que crezca: núcleo + módulos intercambiables, como en la
solución de referencia.
**Pasos:** separar `db.py`, `validacion.py`, `registro.py` y los módulos `tipos`, `lotes` y `relaciones`, y armar el informe
para la materia: modelo, decisiones, plan de pruebas y resultados.

> 🎯 **Fin:** tenés tu propia base de datos basada en nodos, hecha y entendida por vos, con sus tests.
> A partir de acá se le puede sumar la web (Flask y el grafo) tomando como referencia el proyecto `gestion-nodos`.

---

## Glosario rápido
**Base de datos relacional:** datos guardados en tablas relacionadas por ids. · **SQL:** el idioma de las bases.
· **PK:** el id único de cada fila. · **FK:** una columna que apunta al id de otra tabla. · **JOIN:** juntar
tablas en una consulta. · **CRUD:** crear, leer, actualizar y borrar. · **Transacción:** un grupo de cambios que se
guarda entero o no se guarda. · **Inyección SQL:** un ataque que mete SQL en un dato; se evita con `?`.
· **Fixture:** la preparación automática de un test. · **TDD:** escribir el test antes que el código.

## Checklist de avance
- [ ] Etapa 0 — Entorno
- [ ] Etapa 1 — Modelo en papel
- [ ] Etapa 2 — Crear tablas
- [ ] Etapa 3 — CRUD en SQL
- [ ] Etapa 4 — Relaciones (FK, JOIN)
- [ ] Etapa 5 — JSON
- [ ] Etapa 6 — Conexión desde Python
- [ ] Etapa 7 — CRUD en funciones
- [ ] Etapa 8 — Registro y transacciones
- [ ] Etapa 9 — Tests propios
- [ ] Etapa 10 — Consultas de grafo
- [ ] Etapa 11 — Módulos y entrega
