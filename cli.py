#!/usr/bin/env python3
"""Interfaz principal para el Instagram Scraper CLI."""
from __future__ import annotations

import argparse
import logging
import os
import sys
from pathlib import Path
from typing import Iterable, List

os.environ.setdefault("PYDANTIC_V1", "1")

import pandas as pd
from rich import box
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, IntPrompt, Prompt
from rich.table import Table

try:
    from instagrapi.exceptions import TwoFactorRequired
except ImportError as exc:  # pragma: no cover - se maneja en tiempo de ejecución
    raise SystemExit(
        "[ERROR] No se pudo importar instagrapi. Ejecuta ./run.sh para reinstalar las dependencias."
    ) from exc

from filters import FilterCriteria, apply_filters
from scraper import ScraperService
from utils import (
    APP_HEADER,
    clear_session_files,
    get_results_root,
    get_session_path,
    list_csv_files,
    load_session_meta,
    save_session_meta,
    write_csv,
)

logging.basicConfig(level=logging.INFO, format="[%(levelname)s] %(message)s")

if sys.version_info >= (3, 14):  # pragma: no cover - mensaje informativo
    print(
        "⚠️  Advertencia: Python 3.14 o superior detectado. Algunas dependencias pueden requerir versiones preliminares compatibles."
    )

console = Console()

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Herramienta interactiva para scraping de Instagram.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Forzar el menú interactivo (por defecto se muestra si no se pasan argumentos).",
    )
    return parser


def render_header(subtitle: str | None = None) -> None:
    text = APP_HEADER
    if subtitle:
        text += f"\n[bold cyan]{subtitle}[/bold cyan]"
    console.print(Panel(text, expand=False, border_style="magenta", box=box.DOUBLE))


def prompt_filters() -> FilterCriteria | None:
    console.print("\n[bold]Configurar filtros opcionales[/bold]")
    if not Confirm.ask("¿Deseas aplicar filtros a los resultados?", default=False):
        return None

    min_followers = _prompt_optional_int("Mínimo de seguidores (enter para omitir): ")
    max_followers = _prompt_optional_int("Máximo de seguidores (enter para omitir): ")
    min_posts = _prompt_optional_int("Mínimo de publicaciones (enter para omitir): ")

    require_public: bool | None = None
    if Confirm.ask("¿Filtrar por cuentas públicas?", default=False):
        require_public = True
    elif Confirm.ask("¿Filtrar por cuentas privadas?", default=False):
        require_public = False

    require_verified = Confirm.ask("¿Solo cuentas verificadas?", default=False)
    require_highlights = Confirm.ask("¿Solo cuentas con historias destacadas?", default=False)

    return FilterCriteria(
        min_followers=min_followers,
        max_followers=max_followers,
        min_posts=min_posts,
        require_public=require_public,
        require_verified=require_verified,
        require_highlights=require_highlights,
    )


def _prompt_optional_int(message: str) -> int | None:
    value = Prompt.ask(message, default="", show_default=False)
    if not value:
        return None
    try:
        number = int(value)
    except ValueError:
        console.print("[red]Valor inválido. Se ignorará.")
        return None
    return number


def ensure_logged_in(service: ScraperService) -> bool:
    if service.is_logged_in():
        return True
    console.print("[yellow]No hay una sesión activa. Inicia sesión primero.[/yellow]")
    return False


def handle_login(service: ScraperService) -> None:
    render_header("Inicio de sesión")
    session_path = get_session_path()
    meta = load_session_meta()

    if session_path.exists():
        msg = "Se encontró una sesión guardada."
        if meta.get("username"):
            msg += f" Usuario almacenado: [bold]{meta['username']}[/bold]."
        console.print(msg)
        if Confirm.ask("¿Quieres intentar reutilizar la sesión existente?", default=True):
            try:
                client = service.ensure_client()
                client.load_settings(str(session_path))
                client.account_info()
                service.mark_authenticated(meta.get("username"))
                console.print("[green]Sesión reutilizada correctamente.[/green]\n")
                return
            except Exception as exc:  # pragma: no cover
                console.print(
                    f"[yellow]No fue posible reutilizar la sesión automáticamente: {exc}. Se solicitarán credenciales.[/yellow]"
                )

    username = Prompt.ask("Usuario de Instagram", default=meta.get("username", ""))
    if not username:
        console.print("[red]Debes ingresar un usuario válido.[/red]")
        return
    password = Prompt.ask("Contraseña", password=True)
    if not password:
        console.print("[red]Debes ingresar una contraseña.[/red]")
        return

def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Herramienta interactiva para scraping de Instagram.",
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Forzar el menú interactivo (por defecto se muestra si no se pasan argumentos).",
    )
    return parser


def render_header(subtitle: str | None = None) -> None:
    text = APP_HEADER
    if subtitle:
        text += f"\n[bold cyan]{subtitle}[/bold cyan]"
    console.print(Panel(text, expand=False, border_style="magenta", box=box.DOUBLE))


def prompt_filters() -> FilterCriteria | None:
    console.print("\n[bold]Configurar filtros opcionales[/bold]")
    if not Confirm.ask("¿Deseas aplicar filtros a los resultados?", default=False):
        return None

    min_followers = _prompt_optional_int("Mínimo de seguidores (enter para omitir): ")
    max_followers = _prompt_optional_int("Máximo de seguidores (enter para omitir): ")
    min_posts = _prompt_optional_int("Mínimo de publicaciones (enter para omitir): ")

    require_public: bool | None = None
    if Confirm.ask("¿Filtrar por cuentas públicas?", default=False):
        require_public = True
    elif Confirm.ask("¿Filtrar por cuentas privadas?", default=False):
        require_public = False

    require_verified = Confirm.ask("¿Solo cuentas verificadas?", default=False)
    require_highlights = Confirm.ask("¿Solo cuentas con historias destacadas?", default=False)

    return FilterCriteria(
        min_followers=min_followers,
        max_followers=max_followers,
        min_posts=min_posts,
        require_public=require_public,
        require_verified=require_verified,
        require_highlights=require_highlights,
    )


def _prompt_optional_int(message: str) -> int | None:
    value = Prompt.ask(message, default="", show_default=False)
    if not value:
        return None
    try:
        number = int(value)
    except ValueError:
        console.print("[red]Valor inválido. Se ignorará.")
        return None
    return number


def ensure_logged_in(service: ScraperService) -> bool:
    if service.is_logged_in():
        return True
    console.print("[yellow]No hay una sesión activa. Inicia sesión primero.[/yellow]")
    return False


def handle_login(service: ScraperService) -> None:
    render_header("Inicio de sesión")
    session_path = get_session_path()
    meta = load_session_meta()

    if session_path.exists():
        msg = "Se encontró una sesión guardada."
        if meta.get("username"):
            msg += f" Usuario almacenado: [bold]{meta['username']}[/bold]."
        console.print(msg)
        if Confirm.ask("¿Quieres intentar reutilizar la sesión existente?", default=True):
            try:
                client = service.ensure_client()
                client.load_settings(str(session_path))
                client.account_info()
                service.mark_authenticated(meta.get("username"))
                console.print("[green]Sesión reutilizada correctamente.[/green]\n")
                return
            except Exception as exc:  # pragma: no cover
                console.print(
                    f"[yellow]No fue posible reutilizar la sesión automáticamente: {exc}. Se solicitarán credenciales.[/yellow]"
                )

    username = Prompt.ask("Usuario de Instagram", default=meta.get("username", ""))
    if not username:
        console.print("[red]Debes ingresar un usuario válido.[/red]")
        return
    password = Prompt.ask("Contraseña", password=True)
    if not password:
        console.print("[red]Debes ingresar una contraseña.[/red]")
        return

    try:
        service.login(username, password)
    except TwoFactorRequired:
        code = Prompt.ask("Código 2FA", password=True)
        try:
            service.login(username, password, verification_code=code)
        except Exception as exc:
            console.print(f"[red]No se pudo completar el inicio de sesión: {exc}[/red]")
            return
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        return

    save_session_meta({"username": username})
    console.print("[green]Inicio de sesión exitoso.[/green]")


def handle_hashtag(service: ScraperService) -> None:
    render_header("Scraping por hashtag")
    if not ensure_logged_in(service):
        return

    hashtag = Prompt.ask("Hashtag (sin #)").strip().lstrip("#")
    if not hashtag:
        console.print("[red]Debes ingresar un hashtag válido.[/red]")
        return

    amount = IntPrompt.ask("Cantidad máxima de publicaciones a analizar", default=100)
    criteria = prompt_filters()

    try:
        result = service.scrape_hashtag(hashtag, amount, criteria)
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        return

    target_dir = get_results_root() / hashtag
    csv_path = target_dir / "result.csv"
    write_csv(csv_path, _csv_fields(), result.rows)
    console.print(f"[green]Resultados guardados en {csv_path}[/green]")

    _render_rows_table(result.rows[:10], subtitle=result.description)


def handle_profiles(service: ScraperService) -> None:
    render_header("Scraping por perfiles")
    if not ensure_logged_in(service):
        return

    mode = Prompt.ask(
        "¿Cómo deseas proporcionar los usuarios? [1] Lista manual, [2] Archivo .txt",
        choices=["1", "2"],
        default="1",
    )
    usernames: List[str] = []
    if mode == "1":
        raw = Prompt.ask("Usernames separados por coma")
        usernames = [item.strip() for item in raw.split(",") if item.strip()]
    else:
        file_path = Prompt.ask("Ruta del archivo .txt con usernames")
        path = Path(file_path).expanduser()
        if not path.exists():
            console.print("[red]El archivo indicado no existe.[/red]")
            return
        usernames = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]

    if not usernames:
        console.print("[red]No se proporcionaron usuarios válidos.[/red]")
        return

    relation = Prompt.ask("¿Qué deseas obtener?", choices=["followers", "following"], default="followers")
    criteria = prompt_filters()

    try:
        results = service.scrape_profile_relations(usernames, relation, criteria)
    except Exception as exc:
        console.print(f"[red]{exc}[/red]")
        return

    for username, result in results.items():
        sub_dir = get_results_root() / "perfiles" / username
        file_name = "followers.csv" if relation == "followers" else "following.csv"
        csv_path = sub_dir / file_name
        write_csv(csv_path, _csv_fields(extra_source=True), result.rows)
        console.print(f"[green]Resultados para {username} guardados en {csv_path}[/green]")
        _render_rows_table(result.rows[:10], subtitle=result.description)


def handle_filters_existing() -> None:
    render_header("Filtrar resultados existentes")
    files = list_csv_files()
    if not files:
        console.print("[yellow]Aún no hay archivos CSV guardados para filtrar.[/yellow]")
        return

    table = Table(title="Archivos disponibles", show_lines=True)
    table.add_column("#")
    table.add_column("Ruta")
    for idx, path in enumerate(files, start=1):
        table.add_row(str(idx), str(path))
    console.print(table)

    choice = Prompt.ask("Selecciona un archivo por número", choices=[str(i) for i in range(1, len(files) + 1)])
    csv_path = files[int(choice) - 1]
    criteria = prompt_filters()
    if criteria is None:
        console.print("[yellow]No se aplicaron filtros. Nada que hacer.[/yellow]\n")
        return

    df = pd.read_csv(csv_path)
    rows = df.to_dict(orient="records")
    filtered = apply_filters(rows, criteria)
    if not filtered:
        console.print("[yellow]Ningún registro coincide con los filtros seleccionados.[/yellow]")
        return

    output_path = csv_path.with_name("filtered_result.csv")
    has_source = any("source" in row for row in rows)
    write_csv(output_path, _csv_fields(extra_source=has_source), filtered)
    console.print(f"[green]Archivo filtrado guardado en {output_path}[/green]")
    _render_rows_table(filtered[:10], subtitle="Vista previa del filtrado")


def handle_configuration(service: ScraperService) -> None:
    render_header("Configuración y sesión")
    session_path = get_session_path()
    meta = load_session_meta()

    info_table = Table(show_header=False, box=box.SIMPLE_HEAVY)
    info_table.add_row("Sesión activa", "Sí" if service.is_logged_in() else "No")
    info_table.add_row("Usuario autenticado", service.logged_username or "-")
    info_table.add_row("Archivo de sesión", str(session_path))
    info_table.add_row("Resultados", str(get_results_root()))
    info_table.add_row("Usuario guardado", meta.get("username", "-"))
    console.print(info_table)

    if session_path.exists() and Confirm.ask("¿Deseas eliminar la sesión guardada?", default=False):
        clear_session_files()
        console.print("[green]La sesión guardada se eliminó correctamente.[/green]")


def handle_exit() -> None:
    console.print("Gracias por usar INSTAGRAM SCRAPER CLI - propiedad de matidiazlife/elite")


def _render_rows_table(rows: Iterable[dict], subtitle: str | None = None) -> None:
    if not rows:
        console.print("[yellow]No hay datos para mostrar.[/yellow]")
        return

    table = Table(title=subtitle or "Resultados", box=box.SIMPLE_HEAVY)
    columns = [
        "username",
        "full_name",
        "followers",
        "following",
        "media_count",
        "is_private",
        "is_verified",
        "has_highlight_reels",
    ]
    if any("source" in row for row in rows):
        columns.append("source")

    for col in columns:
        table.add_column(col)

    for row in rows:
        table.add_row(*(str(row.get(col, "")) for col in columns))

    console.print(table)


def _csv_fields(extra_source: bool | None = False) -> List[str]:
    base = [
        "username",
        "full_name",
        "followers",
        "following",
        "media_count",
        "is_private",
        "is_verified",
        "has_highlight_reels",
    ]
    if extra_source:
        base.append("source")
    return base


def interactive_loop(service: ScraperService) -> None:
    options = {
        "1": handle_login,
        "2": handle_hashtag,
        "3": handle_profiles,
        "4": lambda svc: handle_filters_existing(),
        "5": handle_configuration,
        "6": lambda svc: handle_exit(),
    }

    if service.is_logged_in():
        username = service.logged_username or "(usuario desconocido)"
        console.print(
            f"[green]Sesión restaurada automáticamente. Usuario autenticado: [bold]{username}[/bold].[/green]\n"
        )

    while True:
        render_header("Menú principal")
        console.print(
            "===========================================\n"
            "1. Iniciar sesión en Instagram\n"
            "2. Hacer scraping por hashtags\n"
            "3. Hacer scraping por perfiles\n"
            "4. Aplicar filtros a resultados existentes\n"
            "5. Configuración y sesión actual\n"
            "6. Salir\n"
        )
        choice = Prompt.ask("Seleccione una opción (1-6)", choices=list(options.keys()))
        if choice == "6":
            handle_exit()
            break
        handler = options[choice]
        if choice == "4":
            handler(None)  # type: ignore[arg-type]
        else:
            handler(service)


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if not args.interactive and any(vars(args).values()):
        console.print("[yellow]Las opciones no interactivas aún no están implementadas. Se usará el menú.[/yellow]")

    service = ScraperService(get_session_path())
    interactive_loop(service)


if __name__ == "__main__":
    main()
