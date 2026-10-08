# Punto de guardado — Base de datos desde cero

**Para retomar:** abrir Claude Code en `~/Proyectos/bd-desde-cero` y decir "continuá desde PUNTO-DE-GUARDADO.md".

## Contexto
- Proyecto de la facu (Metodología y Testing). El usuario APRENDE a hacer la base de datos y sus conexiones desde cero.
  Claude enseña: lección por etapa, el usuario escribe el código, Claude revisa y amplía `verificar.py`.
- Plan completo: `PLAN.md` (12 etapas). Drive: carpeta "Base de datos desde cero" en la RAÍZ del Drive
  (id 1UOvqMpUjifbOxgqPm_IbEcJN6Puh83NY), doc "Plan" (1-A7i6ub9sj4_uZn8x8Kl9mbFSffssOEsL0xEJiXLGZs).
  Subir cambios: `rclone copyto PLAN.md "marcamaldita:Plan — Base de datos desde cero.md" --drive-root-folder-id 1UOvqMpUjifbOxgqPm_IbEcJN6Puh83NY --drive-import-formats md --drive-export-formats md`
- Solución de referencia (no mostrar antes de terminar cada etapa): `~/Proyectos/gestion-nodos`
  (su carpeta de Drive "Gestión de Nodos" también está en la raíz).

## Estado
- 2026-10-06: plan creado y verificador con la etapa 0. **Ninguna etapa hecha todavía.**

- 2026-10-08: CAMBIO DE RUMBO: trabajo en grupo, prototipo para el lun 19/10 y **base firme el jue 15/10**.
  Backend (A = usuario, B = compañero) para el front `NickSPC/Knowledge-System` (copia de lectura en
  ~/Proyectos/front-knowledge-system). El contrato está en `src/types.ts`: Entity, Relationship y Source.
  Reparto en `TAREAS.md` (T01–T40). Historial: 5 cambios por nodo, de todo tipo (también relaciones, en los 2 nodos).
  Respaldos: `./respaldar.sh` → zip en Drive `Base de datos desde cero/respaldos/` + doc "Tareas — Backend Knowledge System".
  Sin repo de GitHub por ahora. El código va en `back/`.

## Siguiente paso
- T01–T05 (día 1). Sin definir: el modo de trabajo (aprendizaje o mixto con IAs locales). Falta compartir la carpeta de Drive con el compañero.
- PLAN.md (etapas) queda como guía de conceptos; el que manda ahora es TAREAS.md.

- Etapa 0 (la hace el usuario): instalar DB Browser (`flatpak install --user -y flathub org.sqlitebrowser.sqlitebrowser`),
  crear `etapa-00/practica.db` y correr `python3 verificar.py 0`.
- Después: dar la lección de la etapa 1 (modelo en papel / DER) y agregar `etapa_1`/`etapa_2` a verificar.py.
