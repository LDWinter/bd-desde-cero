@echo off
cd /d "%~dp0"
rem Primera vez: crea un entorno de Python e instala Flask (necesita internet)
if not exist .venv (
  echo Preparando por primera vez...
  py -3 -m venv .venv 2>nul || python -m venv .venv
  if errorlevel 1 (
    echo No se encontro Python. Instalalo desde https://www.python.org/downloads/ marcando "Add python.exe to PATH".
    pause
    exit /b 1
  )
  .venv\Scripts\python -m pip install --quiet -r back\requirements.txt
)
.venv\Scripts\python iniciar.py
pause
