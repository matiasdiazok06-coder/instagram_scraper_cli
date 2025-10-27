@echo off
setlocal enabledelayedexpansion

echo === INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite ===

set "BASE_REQUIREMENTS=requirements-base.txt"
set "INSTAGRAPI_SPEC=instagrapi>=2.1.2"
set "CORE_PKGS=pydantic-core>=2.27.0 pydantic>=2.9.2"

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

if %PY_VERSION_NUM% GEQ 314 (
  echo ⚠️  Python %PY_VERSION% detectado. Se priorizaran ruedas binarias o versiones preliminares.
  set "PIP_PRE=1"
  set "PIP_ONLY_BINARY=pydantic-core,pydantic"
  python -m pip install --upgrade --pre --only-binary=:all: %CORE_PKGS%
  if errorlevel 1 (
    echo ⚠️  No se encontraron binarios compatibles de pydantic-core o pydantic para Python 3.14 o superior.
    echo     Instala Python 3.13.x para evitar compilaciones fallidas y vuelve a ejecutar run.bat.
    goto :error
  )
  set "PIP_ONLY_BINARY="
  set "PIP_PRE="
) else (
  python -m pip install --upgrade %CORE_PKGS% || goto :error
)

if exist "%BASE_REQUIREMENTS%" (
  python -m pip install --upgrade --no-cache-dir -r "%BASE_REQUIREMENTS%" || goto :error
)

python -m pip install --upgrade --no-cache-dir --no-deps %INSTAGRAPI_SPEC%
if errorlevel 1 (
  echo [ERROR] No fue posible instalar instagrapi. Verifica la conexion a Internet o usa Python 3.13 para asegurar compatibilidad.
  goto :error
)

set "PIP_PREFER_BINARY="
set PYDANTIC_V1=1

echo.
echo === Menú interactivo ===
python cli.py
exit /b 0

:error
echo Hubo un problema instalando dependencias.
exit /b 1
