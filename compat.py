"""Compatibility helpers for pydantic/instagrapi on modern Python."""
from __future__ import annotations

import os
from importlib import import_module


def ensure_pydantic_compat() -> None:
    """Expose Pydantic v1 symbols required by instagrapi when running on v2."""
    os.environ.setdefault("PYDANTIC_V1", "1")
    try:
        import pydantic  # type: ignore
    except Exception:
        return

    version = getattr(pydantic, "__version__", "")
    if version.startswith("1."):
        return

    try:
        pydantic_v1 = import_module("pydantic.v1")
    except Exception:
        return

    required_attrs = (
        "BaseConfig",
        "BaseModel",
        "BaseSettings",
        "ValidationError",
        "Field",
        "root_validator",
        "validator",
    )

    for attr in required_attrs:
        try:
            getattr(pydantic, attr)
            needs_patch = False
        except Exception:
            needs_patch = True

        if needs_patch and hasattr(pydantic_v1, attr):
            setattr(pydantic, attr, getattr(pydantic_v1, attr))
