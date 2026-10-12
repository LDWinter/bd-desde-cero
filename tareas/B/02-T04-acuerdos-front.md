# T04 — Acuerdos con el front

**Estado:** [ ] pendiente · **Prioridad 2** · **Día 1** · **Archivo:** `docs/API.md` · **Depende de:** T03

## Qué
Dejar por escrito los detalles técnicos que, si no se acuerdan, rompen la integración del jueves.

## Cómo
1. Fechas en ISO (`2026-10-05T10:32:00`); las formatea el front.
2. Ids en texto (`"cli-1"`), aunque en la base sean números o texto.
3. Login con cookie de sesión de Flask (el front manda `credentials: "include"` o usa el proxy).
4. Proxy de Vite: `/api` → `http://localhost:5000`, así no hay problemas de CORS.
5. Anotá todo en una sección "Acuerdos" al principio de `docs/API.md`.

## Herramientas
VS Code, chat con el del front

## Cumplido cuando
- [ ] Los 4 acuerdos están anotados en API.md y el del front dijo que sí.
- [ ] Corriste `./respaldar.sh` e hiciste commit.
