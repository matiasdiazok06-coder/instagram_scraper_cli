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
else
  echo "Reutilizando entorno virtual existente..."
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

PY_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
PY_MAJOR=$(python -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')

export PIP_PREFER_BINARY=1

python -m pip install --upgrade pip setuptools wheel

if [ "$PY_MAJOR" -gt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 14 ]; }; then
  echo "⚠️  Python $PY_VERSION detectado. Intentando usar paquetes precompilados compatibles."
  if ! python -m pip install --upgrade --pre --only-binary=:all: "pydantic-core>=2.27.0" "pydantic>=2.9.2"; then
    cat <<'EOF'
⚠️  No se encontraron binarios compatibles de pydantic-core/pydantic para Python 3.14 o superior.
    Para evitar compilaciones fallidas, instala Python 3.13.x (recomendado con pyenv) y vuelve a ejecutar ./run.sh.
EOF
    exit 1
  fi
else
  python -m pip install --upgrade "pydantic-core>=2.27.0" "pydantic>=2.9.2"
fi

if ! python -m pip install --upgrade --no-cache-dir -r requirements.txt; then
  if [ "$PY_MAJOR" -gt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 14 ]; }; then
    echo "[ERROR] La instalación de dependencias falló con Python $PY_VERSION. Se recomienda usar Python 3.13 para máxima estabilidad." >&2
  fi
  exit 1
fi

echo -e "\n=== Menú interactivo ==="
python cli.py
