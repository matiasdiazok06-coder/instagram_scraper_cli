#!/bin/bash
set -euo pipefail

PYTHON_BIN=${PYTHON_BIN:-python3}
VENV_DIR="venv"

echo "=== INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite ==="

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERROR] No se encontró un intérprete 'python3'." >&2
  exit 1
fi

if [ ! -d "$VENV_DIR" ]; then
  echo "Creando entorno virtual..."
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

PY_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
PY_MAJOR=$(python -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')

python -m pip install --upgrade pip setuptools wheel

if [ "$PY_MAJOR" -gt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 14 ]; }; then
  echo "⚠️  Python $PY_VERSION detectado. Algunas dependencias pueden requerir versiones preliminares compatibles."
  if ! python -m pip install --upgrade --pre pydantic-core pydantic; then
    echo "Intentando instalación mediante binarios precompilados de pydantic-core..."
    if command -v rustc >/dev/null 2>&1; then
      if ! PIP_ONLY_BINARY=:all: python -m pip install --upgrade pydantic-core; then
        echo "No se pudo instalar pydantic-core incluso forzando binarios." >&2
        exit 1
      fi
    else
      if ! python -m pip install --only-binary=:all: --upgrade pydantic-core; then
        echo "No se pudo instalar pydantic-core con binarios precompilados." >&2
        exit 1
      fi
    fi
    if ! python -m pip install --upgrade --pre pydantic; then
      echo "No se pudo actualizar pydantic a una versión compatible." >&2
      exit 1
    fi
  fi
fi

python -m pip install --upgrade -r requirements.txt

echo -e "\n=== Menú interactivo ==="
python cli.py
