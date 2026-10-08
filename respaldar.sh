#!/usr/bin/env bash
# Sube un .zip con fecha del proyecto a Drive: "Base de datos desde cero/respaldos/".
set -euo pipefail
cd "$(dirname "$0")"
zip_=/tmp/bd-respaldo-$(date +%Y-%m-%d_%H%M).zip
zip -qr "$zip_" . -x '.git/*' '*/.venv/*' '.venv/*' '*__pycache__*' '*.pytest_cache*'
rclone copy "$zip_" marcamaldita:respaldos --drive-root-folder-id 1UOvqMpUjifbOxgqPm_IbEcJN6Puh83NY
rclone copyto TAREAS.md "marcamaldita:Tareas — Backend Knowledge System.md" \
  --drive-root-folder-id 1UOvqMpUjifbOxgqPm_IbEcJN6Puh83NY --drive-import-formats md --drive-export-formats md
rm -f "$zip_"
echo "Respaldo subido: $(basename "$zip_")"
