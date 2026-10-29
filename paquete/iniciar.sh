#!/usr/bin/env bash
# Linux / macOS. Primera vez: crea un entorno de Python e instala Flask (necesita internet)
cd "$(dirname "$0")"
if [ ! -d .venv ]; then
  echo "Preparando por primera vez..."
  python3 -m venv .venv || { echo "Falta python3 (y python3-venv en Debian/Ubuntu/Pop)"; exit 1; }
  .venv/bin/python -m pip install --quiet -r back/requirements.txt
fi
exec .venv/bin/python iniciar.py
