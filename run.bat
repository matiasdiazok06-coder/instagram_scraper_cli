@echo off
setlocal enabledelayedexpansion

echo === INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite ===

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

echo Actualizando herramientas base de instalacion...
python -m pip install --upgrade pip setuptools wheel || goto :error

if %PY_VERSION_NUM% GEQ 314 (
  echo ⚠️  Python %PY_VERSION% detectado. Algunas dependencias requieren versiones preliminares compatibles.
  python -m pip install --upgrade --pre pydantic-core pydantic
  if errorlevel 1 (
    echo Intentando instalación mediante binarios precompilados de pydantic-core...
    where rustc >nul 2>nul
    if errorlevel 1 (
      python -m pip install --only-binary=:all: --upgrade pydantic-core || goto :error
    ) else (
      set "PIP_ONLY_BINARY=:all:"
      python -m pip install --upgrade pydantic-core || goto :error
      set "PIP_ONLY_BINARY="
    )
    python -m pip install --upgrade --pre pydantic || goto :error
  )
)

python -m pip install --upgrade -r requirements.txt || goto :error

echo.
echo === Menú interactivo ===
python cli.py
exit /b 0

:error
echo Hubo un problema instalando dependencias.
exit /b 1
