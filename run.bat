@echo off
setlocal enabledelayedexpansion

echo === INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite ===

if exist venv\Scripts\activate.bat (
  echo Reutilizando entorno virtual...
) else (
  echo Creando entorno virtual...
  py -3 -m venv venv
)

call venv\Scripts\activate.bat || (
  echo No se pudo activar el entorno virtual.
  exit /b 1
)

python -m pip install --upgrade pip
python -m pip install --upgrade -r requirements.txt || goto :error

echo.
echo === Menú interactivo ===
python cli.py
exit /b 0

:error
echo Hubo un problema instalando dependencias.
exit /b 1
