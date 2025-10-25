@echo off
setlocal enabledelayedexpansion
set "VENV_DIR=.venv"
set "PYTHON_BIN=python"

where %PYTHON_BIN% >nul 2>&1
if errorlevel 1 (
  echo [ERROR] No se encontro Python en el PATH. Instala Python 3 y vuelve a intentarlo.
  exit /b 1
)

%PYTHON_BIN% -c "import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)" >nul 2>&1
if errorlevel 1 (
  echo [ERROR] Se requiere Python 3.9 o superior.
  exit /b 1
)

%PYTHON_BIN% -c "import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)" >nul 2>&1
if errorlevel 1 (
  echo [WARN] Python 3.10+ ofrece mayor compatibilidad. Continuando con dependencias para versiones anteriores.
)

if not exist %VENV_DIR%\Scripts\python.exe (
  %PYTHON_BIN% -m venv %VENV_DIR%
)

call %VENV_DIR%\Scripts\activate

%PYTHON_BIN% -m pip install --upgrade pip setuptools wheel
if errorlevel 1 (
  echo [WARN] No se pudo actualizar pip/setuptools/wheel automaticamente. Continuando con las versiones actuales.
)

pip install --upgrade --no-cache-dir -r requirements.txt || goto :pip_error

set "RUN_ARGS=%*"
if "%~1"=="" set "RUN_ARGS=--menu"

%PYTHON_BIN% cli.py %RUN_ARGS%
exit /b 0

:pip_error
echo [ERROR] Fallo la instalacion de dependencias. Revisa tu conexion a internet o configura tu proxy.
exit /b 2
