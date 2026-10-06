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

## Siguiente paso
- Etapa 0 (la hace el usuario): instalar DB Browser (`flatpak install --user -y flathub org.sqlitebrowser.sqlitebrowser`),
  crear `etapa-00/practica.db` y correr `python3 verificar.py 0`.
- Después: dar la lección de la etapa 1 (modelo en papel / DER) y agregar `etapa_1`/`etapa_2` a verificar.py.
