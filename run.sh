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

pip install --upgrade pip
pip install --upgrade -r requirements.txt

echo "\n=== Menú interactivo ==="
python3 cli.py
