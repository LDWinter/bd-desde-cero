#!/usr/bin/env bash
# Arma KnowledgeSystem.zip: este back + el front compilado, listo para correr con solo Python.
# Uso: paquete/armar.sh <carpeta del front Knowledge-System>   (corre `npm run build` ahí)
set -euo pipefail
FRONT="${1:?Uso: paquete/armar.sh <carpeta del front>}"
AQUI="$(cd "$(dirname "$0")" && pwd)"
TMP="$(mktemp -d)"; DEST="$TMP/KnowledgeSystem"
(cd "$FRONT" && npm run build)
mkdir -p "$DEST/back" "$DEST/web"
cp "$AQUI"/../back/{app,db,formato,historial,nodos,relaciones,semilla,usuarios}.py "$AQUI"/../back/rutas_*.py "$AQUI"/../back/esquema.sql "$DEST/back/"
echo flask > "$DEST/back/requirements.txt"
cp -r "$FRONT/dist/." "$DEST/web/"
cp "$AQUI"/{iniciar.py,"Iniciar (Windows).bat",iniciar.sh,LEEME.txt} "$DEST/"
(cd "$TMP" && zip -qr "$AQUI/KnowledgeSystem.zip" KnowledgeSystem)
rm -rf "$TMP"
echo "Listo: $AQUI/KnowledgeSystem.zip"
