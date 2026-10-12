# Tareas de B (compañero) — Backend Knowledge System

Ordenadas por **prioridad**: primero lo que bloquea al front y a A, después el resto según las dependencias.
Fuente completa: `../../TAREAS.md`. Al terminar cada tarea: se cumple "Cumplido cuando" → `./respaldar.sh` → commit → marcar `[x]` acá y en su archivo.

## Compartidas con A (están en `tareas/`)
- [ ] [T01 — Leer el contrato del front](../01-T01-leer-contrato-front.md) · antes que todo
- [ ] [T39 — Prueba de humo](../22-T39-prueba-humo.md) · Día 7
- [ ] [T40 — Respaldo final](../23-T40-respaldo-final.md) · Día 7

## Tareas de B (en orden de prioridad)
- [ ] [T03 — Contrato de la API](01-T03-contrato-api.md) · Día 1 · Jue 8 – Vie 9 · depende de T01
- [ ] [T04 — Acuerdos con el front](02-T04-acuerdos-front.md) · Día 1 · depende de T03
- [ ] [T09 — CREATE TABLE usuarios](03-T09-tabla-usuarios.md) · Día 2 · Sáb 10 · depende de T06
- [ ] [T10 — CREATE TABLE historial](04-T10-tabla-historial.md) · Día 2 · depende de T07, T09
- [ ] [T11 — Semilla con los datos de los mocks](05-T11-semilla.md) · Día 2 · depende de T08, T10
- [ ] [T14 — Fixture conn para los tests](06-T14-fixture-conn.md) · Día 3 · Dom 11 · depende de T13 (de A)
- [ ] [T19 — a_entity y a_relationship](07-T19-formato.md) · Día 3 · depende de T15 (de A)
- [ ] [T18 — Tests de nodos y relaciones (código de A)](08-T18-tests-nodos-relaciones.md) · Día 3 · depende de T14, T17 (de A)
- [ ] [T20 — registrar() e historial_de()](09-T20-registrar-historial.md) · Día 4 · Lun 12 · depende de T10, T13 (de A)
- [ ] [T21 — Purga del historial (tope de 5 por nodo)](10-T21-purga-historial.md) · Día 4 · depende de T20
- [ ] [T23 — registrar_usuario y verificar_clave](11-T23-usuarios.md) · Día 4 · depende de T09, T13 (de A)
- [ ] [T25 — app.py: base de Flask](12-T25-app.md) · Día 5 · Mar 13 · depende de T13 (de A)
- [ ] [T29 — Login, logout y me](13-T29-login.md) · Día 5 · depende de T23, T25
- [ ] [T30 — Decorador @requiere_login](14-T30-requiere-login.md) · Día 5 · depende de T29
- [ ] [T28 — GET /api/sources](15-T28-get-sources.md) · Día 5 · depende de T25
- [ ] [T34 — GET /api/entities/<id>/history](16-T34-get-history.md) · Día 6 · Mié 14 · depende de T20, T26 (de A)
- [ ] [T35 — Tests de API de las rutas de A](17-T35-tests-api-nodos.md) · Día 6 · depende de T33 (de A)
- [ ] [T38 — README del back](18-T38-readme.md) · Día 7 · Jue 15 · depende de T36 (de A)
