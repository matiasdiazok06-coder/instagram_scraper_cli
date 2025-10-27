@echo off
setlocal enabledelayedexpansion

echo === INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite ===

set "DEFAULT_REQUIREMENTS=requirements.txt"
set "BASE_REQUIREMENTS=requirements-base.txt"
set "REQ_FILE=%DEFAULT_REQUIREMENTS%"
set "PIP_ARGS=--no-cache-dir -r"

if exist venv\Scripts\activate.bat (
  echo Reutilizando entorno virtual...
) else (
  echo Creando entorno virtual...
  py -3 -m venv venv || (
    echo No se pudo crear el entorno virtual.
    exit /b 1
  )
)

call venv\Scripts\activate.bat || (
  echo No se pudo activar el entorno virtual.
  exit /b 1
)

for /f %%v in ('python -c "import sys; print(f'{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}')"') do set "PY_VERSION=%%v"
for /f "tokens=1,2 delims=." %%a in ("%PY_VERSION%") do (
  set "PY_MAJOR=%%a"
  set "PY_MINOR=%%b"
)
set /a PY_VERSION_NUM=%PY_MAJOR%*100+%PY_MINOR%

set "PIP_PREFER_BINARY=1"

echo Actualizando herramientas base de instalacion...
python -m pip install --upgrade pip setuptools wheel || goto :error

set "CORE_PKGS=pydantic-core>=2.27.0 pydantic>=2.9.2"

if %PY_VERSION_NUM% GEQ 314 (
  echo ⚠️  Python %PY_VERSION% detectado. Intentando usar paquetes precompilados compatibles.
  set "PIP_PRE=1"
  set "PIP_ONLY_BINARY=pydantic-core,pydantic"
  python -m pip install --upgrade --pre --only-binary=:all: %CORE_PKGS%
  if errorlevel 1 (
    echo ⚠️  No se encontraron binarios compatibles de pydantic-core o pydantic para Python 3.14 o superior.
    echo     Para evitar compilaciones fallidas, instala Python 3.13.x recomendado con pyenv o Microsoft Store y vuelve a ejecutar run.bat.
    goto :error
  )
  where rustc >nul 2>&1
  if errorlevel 1 (
    echo ℹ️  rustc no esta instalado; se forzara el uso de binarios precompilados para evitar compilaciones locales.
  )
  if exist "%BASE_REQUIREMENTS%" set "REQ_FILE=%BASE_REQUIREMENTS%"
) else (
  python -m pip install --upgrade %CORE_PKGS% || goto :error
  set "PIP_ARGS=--upgrade --no-cache-dir -r"
)

python -m pip install %PIP_ARGS% %REQ_FILE%
if errorlevel 1 (
  if %PY_VERSION_NUM% GEQ 314 (
    echo [ERROR] La instalacion de dependencias fallo con Python %PY_VERSION%. Se recomienda usar Python 3.13 para maxima estabilidad.
  )
  goto :error
)

set "PIP_PREFER_BINARY="
set "PIP_PRE="
set "PIP_ONLY_BINARY="

echo.
echo === Menú interactivo ===
python cli.py
exit /b 0

:error
echo Hubo un problema instalando dependencias.
exit /b 1
