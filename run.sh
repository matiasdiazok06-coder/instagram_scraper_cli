#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$PROJECT_DIR"

PYTHON_BIN="${PYTHON_BIN:-python3}"
VENV_DIR="${VENV_DIR:-.venv}"

if ! command -v "$PYTHON_BIN" >/dev/null 2>&1; then
  echo "[ERROR] No se encontró $PYTHON_BIN. Instala Python 3 desde https://www.python.org/downloads/" >&2
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 9) else 1)'; then
  echo "[ERROR] Se requiere Python 3.9 o superior." >&2
  exit 1
fi

if ! "$PYTHON_BIN" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 10) else 1)'; then
  echo "[WARN] Python 3.10+ ofrece mayor compatibilidad. Continuando con dependencias para versiones anteriores." >&2
fi

if [ ! -d "$VENV_DIR" ]; then
  "$PYTHON_BIN" -m venv "$VENV_DIR"
fi

# shellcheck disable=SC1090
source "$VENV_DIR/bin/activate"

if ! python -m pip install --upgrade pip setuptools wheel; then
  echo "[WARN] No se pudo actualizar pip/setuptools/wheel automáticamente. Continuando con las versiones actuales." >&2
fi

pip install --upgrade --no-cache-dir -r requirements.txt

if [ "$#" -eq 0 ]; then
  set -- --menu
fi

python cli.py "$@"
