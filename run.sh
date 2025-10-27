#!/bin/bash
set -euo pipefail

PYTHON_BIN=${PYTHON_BIN:-python3}
VENV_DIR="venv"
BASE_REQUIREMENTS="requirements-base.txt"

HEADER="=== INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite ==="
CORE_PKGS=("pydantic-core>=2.27.0" "pydantic>=2.9.2")
INSTAGRAPI_SPEC="instagrapi>=2.1.2"

printf '%s\n' "$HEADER"

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

export PYDANTIC_V1=1

PY_VERSION=$(python -c 'import sys; print(f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}")')
PY_MAJOR=$(python -c 'import sys; print(sys.version_info.major)')
PY_MINOR=$(python -c 'import sys; print(sys.version_info.minor)')

export PIP_PREFER_BINARY=1
if ! python -m pip install --upgrade pip setuptools wheel; then
  echo "[WARN] No se pudo actualizar pip/setuptools/wheel. Se continuará con las versiones instaladas." >&2
fi

if [ "$PY_MAJOR" -gt 3 ] || { [ "$PY_MAJOR" -eq 3 ] && [ "$PY_MINOR" -ge 14 ]; }; then
  echo "⚠️  Python $PY_VERSION detectado. Se forzará el uso de ruedas binarias o versiones preliminares."
  export PIP_PRE=1
  export PIP_ONLY_BINARY="pydantic-core,pydantic"
  if ! python -m pip install --upgrade --pre --only-binary=:all: "${CORE_PKGS[@]}"; then
    cat <<'EOW'
⚠️  No se encontraron binarios compatibles de pydantic-core/pydantic para Python 3.14 o superior.
    Para evitar compilaciones fallidas, instala Python 3.13.x (recomendado con pyenv) y vuelve a ejecutar ./run.sh.
EOW
    exit 1
  fi
  unset PIP_ONLY_BINARY
  unset PIP_PRE
else
  python -m pip install --upgrade "${CORE_PKGS[@]}"
fi

if [ -f "$BASE_REQUIREMENTS" ]; then
  python -m pip install --upgrade --no-cache-dir -r "$BASE_REQUIREMENTS"
fi

# Instala instagrapi sin resolver dependencias para permitir pydantic 2.x
if ! python -m pip install --upgrade --no-cache-dir --no-deps "$INSTAGRAPI_SPEC"; then
  cat <<'EOW' >&2
[ERROR] No fue posible instalar instagrapi con las dependencias actuales.
        Verifica tu conexión a Internet o instala Python 3.13 para asegurar compatibilidad.
EOW
  exit 1
fi

if ! python - <<'PY'
from compat import ensure_pydantic_compat

ensure_pydantic_compat()

try:
    import instagrapi  # noqa: F401
    from instagrapi import exceptions  # noqa: F401
except Exception as exc:
    raise SystemExit(exc)
PY
then
  echo "Reinstalando instagrapi para asegurar módulos completos..."
  python -m pip install --force-reinstall --no-cache-dir --no-deps "$INSTAGRAPI_SPEC"
  python - <<'PY'
from compat import ensure_pydantic_compat

ensure_pydantic_compat()

try:
    import instagrapi  # noqa: F401
    from instagrapi import exceptions  # noqa: F401
except Exception as exc:
    raise SystemExit("instagrapi no quedó instalado correctamente") from exc
PY
fi

unset PIP_PREFER_BINARY

echo -e "\n=== Menú interactivo ==="
python cli.py
