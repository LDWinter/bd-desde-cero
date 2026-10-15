# Registro de cambios

Todo lo que se va modificando en el proyecto, lo más nuevo arriba.
Formato: `fecha — quién — qué cambió (archivos)`. Se agrega una línea por cada commit.

## 2026-10-15
- LDev — T39 parte back: prueba de humo con el servidor real, sin errores (`docs/prueba-humo.md`); `docs/INTEGRACION.md` al día con las rutas provisionales
- LDev — T36: tests de API de login, fuentes e historial (`back/tests/test_api_auth.py`, 46 OK)
- LDev — T34 provisional `GET /api/entities/<id>/history` (`back/rutas_nodos.py`); `/api/sources` sin login
- LDev — T28 provisional `GET /api/sources` (`back/rutas_fuentes_provisional.py`); `app.py` usa `*_provisional.py` mientras falten los de B
- LDev — Docstrings detallados en `back/nodos.py` y `back/relaciones.py` (solo documentación, sin cambios de lógica)
- LDev — Guía de integración para el front y el login (`docs/INTEGRACION.md`, enlazada desde `README.md`); T01: dudas para el front en su sección 7; `respaldar.sh` ya no sube los archivos locales de Claude
- LDev — Docstrings detallados de cada ruta (para integrar el front) y PUT sin `data` ya no borra los datos del nodo (`back/rutas_nodos.py`, `back/probar_a.py`)
- LDev — Limpieza: se borran las copias provisionales ya reemplazadas por el código de B (app, formato, historial, usuarios, conftest), `back/esquema_mysql.sql` (sin uso, queda en el historial de git) y `docs/modelo.md` (solo apuntaba a `modelo_relacional.md`)
- LDev — Integración con el código de B: las rutas usan los ids del front (`cli-1`) con `formato.id_base()`, `/api/relationships` usa `formato.SELECT_RELACION`; T33 (POST y DELETE /api/relationships, 409 en duplicado o lazo); tests y `probar_a.py` al día (`back/rutas_nodos.py`, `back/relaciones.py`, `back/nodos.py`, `back/probar_a.py`, `back/tests/`)
- LDev — Ignorar los informes de análisis locales `docs/analisis/` (`.gitignore`)

## 2026-10-14
- LDev — Nota: T13 a T32 las hizo Claude por falta de tiempo. Las piezas de B que hacían falta para probarlas son **copias provisionales** con otro nombre (`*_provisional.py`); el código de A usa el archivo de B en cuanto exista. Las tareas de B siguen pendientes
- LDev — Prueba manual de las tareas de A (T13 a T32): back/probar_a.py (61ab0dd: `back/probar_a.py`)
- LDev — T32: PUT y DELETE /api/entities/<id> (d962238: `back/rutas_nodos.py`, `tareas/18-T32-put-delete-entity.md`)
- LDev — T31: POST /api/entities (467357e: `back/rutas_nodos.py`, `tareas/17-T31-post-entity.md`)
- LDev — T27: GET /api/relationships (20acdfa: `back/rutas_nodos.py`, `tareas/16-T27-get-relationships.md`)
- LDev — T26: GET /api/entities y GET /api/entities/<id> (c2f2b3c: `back/rutas_nodos.py`, `tareas/15-T26-get-entities.md`)
- LDev — Copias provisionales de B (T19, T25, T29 y T30): formato, app y rutas_auth (b4fefd1: `back/app_provisional.py`, `back/formato_provisional.py`, `back/rutas_auth_provisional.py`)
- LDev — T24: tests de historial y usuarios (código de B) (2475b33: `back/tests/test_historial.py`, `back/tests/test_usuarios.py`, `tareas/14-T24-tests-historial-usuarios.md`)
- LDev — Copias provisionales de B (T14 y T23): conftest_provisional.py y usuarios_provisional.py (cf2b469: `back/tests/conftest_provisional.py`, `back/usuarios_provisional.py`)
- LDev — T22b: relacionar y desrelacionar registran en el historial de los dos nodos (cac84f9: `back/relaciones.py`, `tareas/13-T22b-historial-relaciones.md`)
- LDev — T22: crear, editar y borrar nodo registran en el historial (misma transacción) (a2d0521: `back/nodos.py`, `tareas/12-T22-historial-nodos.md`)
- LDev — Copia provisional de historial.py de B (T20 y T21): historial_provisional.py (c671b5a: `back/historial_provisional.py`)
- LDev — T17: relacionar(), desrelacionar() y vecinos() en relaciones.py (b1d2f17: `back/relaciones.py`, `tareas/11-T17-relaciones.md`)
- LDev — T16: listar_nodos(), editar_nodo() y borrar_nodo() en nodos.py (52d5f5a: `back/nodos.py`, `tareas/10-T16-listar-editar-borrar.md`)
- LDev — T15: crear_nodo() y obtener_nodo() en nodos.py (277e664: `back/nodos.py`, `tareas/09-T15-crear-obtener-nodo.md`)
- LDev — T13: conectar() y crear_esquema() en db.py (4c7e295: `back/db.py`, `tareas/08-T13-db.md`)
- LDev — T12 completada: las 3 consultas de práctica (nodos con su tipo, vecinos con UNION, cantidad por tipo) verificadas sobre la semilla (`back/consultas.sql`, `tareas/07-T12-consultas.md`)
- LDev — T11 completada: `back/semilla.py` reemplazada por la versión con los datos reales del mock (3 fuentes, 14 nodos, 15 relaciones, usuario `prueba@local`). Origen: `tareas/semilla.py`, trabajo de B (`back/semilla.py`, `tareas/B/05-T11-semilla.md`, `tareas/B/README.md`)
- LDev — Se borra `MIS-TAREAS.md`: todas las tareas están en `TAREAS.md`, en `tareas/` (A) y en `tareas/B/` (B), en orden. Se borra la copia duplicada `tareas/semilla.py`; queda solo `back/semilla.py`
- LDev — Se crea este registro de cambios (`CAMBIOS.md`). Se saca del repo `PUNTO-DE-GUARDADO.md` (es de uso personal, sigue en local) y se borra `Guía_Git_Proyecto_BD.pdf`
- LDev — T11 (parcial): semilla.py de B, enviada por WhatsApp (5ecf38c: `back/semilla.py`)

## 2026-10-12
- LDev — Verificación T01-T09, README con la estructura y docs corregidas (f729179: `.gitignore`, `MIS-TAREAS.md`, `PUNTO-DE-GUARDADO.md`, `README.md`, `docs/modelo.md`, `tareas/02-T05-entorno.md`)
- LDev — Limpieza: ignorar caché de pytest (T06-T08 ya completadas) (826aaf0: `.gitignore`)
- LDev — T06, T07 y T08 completadas: esquema verificado y tareas al día (32d18bb: `MIS-TAREAS.md`, `back/esquema.sql`, `tareas/04-T06-tipos-y-fuentes.md`, `tareas/05-T07-nodos.md`, `tareas/06-T08-relaciones.md`)
- LDev — Esquema SQLite completo (T06-T10) a partir del trabajo de B (b2a053a: `back/esquema.sql`)
- Ozis02 — Merge branch 'main' of https://github.com/LDWinter/bd-desde-cero (03e69f3)
- Ozis02 — Trabajo de B (9be5ffe: `back/esquema_mysql.sql`)
- LDev — Ignorar temporales de draw.io (fafabda: `.gitignore`, `docs/.$der.drawio.bkp`)
- LDev — T02 marcada como completada (d805f12: `docs/.$der-simplificado.drawio.dtmp`, `docs/.$der.drawio.bkp`, `docs/der-simplificado.drawio`)
- LDev — T02 marcada como completada (e2e806e: `tareas/03-T02-der.md`)
- LDev — T02: DER completo de las 6 tablas, modelo relacional y avance de tareas (e47c29d: `docs/der.drawio`, `docs/der.drawio.png`, `docs/modelo_relacional.md`, `tareas/02-T05-entorno.md`, `tareas/03-T02-der.md`)
- LDev — Actualización de tareas para el usuario B y estructura de documentos (1f068d4: `PLAN.md`, `docs/.$der-simplificado.drawio.dtmp`, `tareas/B/01-T03-contrato-api.md`, `tareas/B/02-T04-acuerdos-front.md`, `tareas/B/03-T09-tabla-usuarios.md`, `tareas/B/04-T10-tabla-historial.md`)
- LDev — Backend, docs y tareas del proyecto (ceaed01: `MIS-TAREAS.md`, `PUNTO-DE-GUARDADO.md`, `back/consultas.sql`, `back/db.py`, `back/esquema.sql`, `back/nodos.py`)

## 2026-10-08
- LDev — Reparto de tareas del backend (base firme 15/10) y respaldo a Drive (c066b51: `PUNTO-DE-GUARDADO.md`, `TAREAS.md`, `respaldar.sh`)

## 2026-10-06
- LDev — Punto de guardado para retomar (035a164: `PUNTO-DE-GUARDADO.md`)
- LDev — Plan de aprendizaje: base de datos desde cero + verificador (etapa 0) (0007e91: `.gitignore`, `PLAN.md`, `verificar.py`)
