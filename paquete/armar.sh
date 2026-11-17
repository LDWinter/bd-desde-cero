#!/usr/bin/env bash
# Uso: paquete/armar.sh <carpeta del front Knowledge-System>
# Compila el front, lo deja en web/ (lo que sirve iniciar.py) y arma paquete/KnowledgeSystem.zip.
set -euo pipefail
FRONT="$(cd "${1:?Uso: paquete/armar.sh <carpeta del front>}" && pwd)"
AQUI="$(cd "$(dirname "$0")" && pwd)"; RAIZ="$(dirname "$AQUI")"
TMP="$(mktemp -d)"; DEST="$TMP/KnowledgeSystem"
(cd "$FRONT" && npm run build)
rm -rf "$RAIZ/web" && cp -r "$FRONT/dist" "$RAIZ/web"  # de cero: los archivos del build cambian de nombre
mkdir -p "$DEST/back"
cp "$RAIZ"/back/{app,db,formato,historial,nodos,relaciones,semilla,usuarios}.py "$RAIZ"/back/rutas_*.py "$RAIZ"/back/esquema.sql "$DEST/back/"
grep -vi pytest "$RAIZ/back/requirements.txt" > "$DEST/back/requirements.txt"
cp -r "$RAIZ/web" "$DEST/web"
cp "$RAIZ"/{iniciar.py,"Iniciar (Windows).bat",iniciar.sh} "$AQUI/LEEME.txt" "$RAIZ"/docs/ejemplo-*.json "$DEST/"
(cd "$TMP" && zip -qr nuevo.zip KnowledgeSystem && mv -f nuevo.zip "$AQUI/KnowledgeSystem.zip")  # no agrega a un zip viejo
rm -rf "$TMP"
echo "Listo: $AQUI/KnowledgeSystem.zip"
