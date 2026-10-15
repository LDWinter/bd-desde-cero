# T37 — Conectar el front al back

**Estado:** [x] completado por A en lo que toca al back (guía en docs/INTEGRACION.md §6; el cambio en el repo del front lo hace la compañera; 15/10) · **Día 7 · Jue 15** · **Archivo:** repo del front: `vite.config.ts`, `src/api.ts` · **Depende de:** T27, T28

## Qué
Que el front deje de usar los mocks y lea SQLite (junto al del front).

## Cómo
1. En `vite.config.ts`: `server.proxy` con `'/api': 'http://localhost:5000'`.
2. En `api.ts`: cambiar el cuerpo de cada función por `fetch('/api/...')` + `.json()`, sin cambiar sus firmas.

## Herramientas
TypeScript, Vite, npm

## Cumplido cuando
- [ ] El front muestra los datos de SQLite (Inicio, Grafo y Entidad).
- [ ] Corriste `./respaldar.sh` e hiciste commit.
