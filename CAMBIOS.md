# Registro de cambios

Todo lo que se va modificando en el proyecto, lo más nuevo arriba.
Formato: `fecha — quién — qué cambió (archivos)`. Se agrega una línea por cada commit.

## 2026-10-14
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
