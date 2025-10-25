"""Utility helpers for the Instagram scraper CLI."""
from __future__ import annotations

import csv
import json
import logging
from pathlib import Path
from typing import Iterable, Mapping, Sequence

APP_HEADER = "INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite"


def get_project_root() -> Path:
    return Path(__file__).resolve().parent


def get_session_path() -> Path:
    return get_project_root() / "session.json"


def get_session_meta_path() -> Path:
    return get_project_root() / "session_meta.json"


def get_desktop_path() -> Path:
    desktop = Path.home() / "Desktop"
    if desktop.exists():
        return desktop
    logging.getLogger(__name__).warning(
        "El escritorio no existe en %s. Usando el directorio actual para guardar resultados.",
        desktop,
    )
    return Path.cwd()


def get_results_root() -> Path:
    root = get_desktop_path() / "instagram_scraper_results"
    root.mkdir(parents=True, exist_ok=True)
    return root


def ensure_directory(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def write_csv(path: Path, fieldnames: Sequence[str], rows: Iterable[Mapping[str, object]]) -> None:
    ensure_directory(path.parent)
    with path.open("w", encoding="utf-8", newline="") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def load_session_meta() -> dict:
    meta_path = get_session_meta_path()
    if not meta_path.exists():
        return {}
    try:
        return json.loads(meta_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError:
        logging.getLogger(__name__).warning("El archivo de metadatos de sesión está dañado. Se ignorará.")
        return {}


def save_session_meta(data: Mapping[str, object]) -> None:
    meta_path = get_session_meta_path()
    meta_path.write_text(json.dumps(dict(data), ensure_ascii=False, indent=2), encoding="utf-8")


def clear_session_files() -> None:
    for path in (get_session_path(), get_session_meta_path()):
        try:
            path.unlink()
        except FileNotFoundError:
            continue


def list_csv_files() -> list[Path]:
    results = []
    root = get_results_root()
    for path in root.rglob("*.csv"):
        results.append(path)
    return sorted(results)
