#!/usr/bin/env python3
"""
cli.py - Extrae info básica de usuarios de Instagram usando instagrapi.
"""

import argparse
import csv
import json
import sys
import time
from getpass import getpass
from pathlib import Path
from typing import Any, Dict, List, Optional

try:
    from instagrapi import Client
    from instagrapi.exceptions import ChallengeRequired, ClientError, TwoFactorRequired
except ModuleNotFoundError as exc:  # pragma: no cover - feedback para instalaciones incompletas
    missing = exc.name
    print(
        "[ERROR] Falta la dependencia '%s'. Ejecuta 'pip install -r requirements.txt' "
        "(o ./run.sh en macOS/Linux, run.bat en Windows) para completar la instalación." % missing,
        file=sys.stderr,
    )
    sys.exit(3)


def save_json(path: str, data: Any) -> None:
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False), encoding="utf-8")


def load_targets_from_file(path: str) -> List[str]:
    file_path = Path(path)
    if not file_path.exists():
        raise FileNotFoundError(f"No se encontró el archivo de usuarios: {path}")
    return [line.strip() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]


def follower_bucket(n: Optional[int]) -> str:
    if n is None:
        return "unknown"
    if n < 1_000:
        return "0-1k"
    if n < 10_000:
        return "1k-10k"
    if n < 100_000:
        return "10k-100k"
    if n < 1_000_000:
        return "100k-1M"
    return "1M+"


def prompt_input(message: str, default: Optional[str] = None, required: bool = False, secret: bool = False) -> str:
    while True:
        try:
            if secret:
                value = getpass(message)
            else:
                value = input(message)
        except KeyboardInterrupt:
            print("\n[INFO] Operación cancelada por el usuario.")
            sys.exit(130)
        value = value.strip()
        if not value and default is not None:
            return default
        if value:
            return value
        if not required:
            return ""
        print("Este campo es obligatorio. Intenta nuevamente.")


def prompt_bool(message: str, default: bool = False) -> bool:
    suffix = " [S/n]: " if default else " [s/N]: "
    options = {"s": True, "n": False, "": default}
    while True:
        answer = prompt_input(message + suffix).lower()
        if answer in options:
            return options[answer]
        print("Responde 's' o 'n'.")


def prompt_float(message: str, default: float) -> float:
    while True:
        raw = prompt_input(f"{message} [{default}]: ")
        if not raw:
            return default
        try:
            return float(raw)
        except ValueError:
            print("Ingresa un número válido.")


def interactive_menu(args: argparse.Namespace) -> argparse.Namespace:
    print("\n=== Instagram Scraper CLI - Modo interactivo ===\n")
    session_default = args.session or "session.json"
    session_file = prompt_input(f"Archivo de sesión [{session_default}]: ", default=session_default)

    print("\nInicio de sesión")
    print("----------------")
    username_default = args.username_mi_cuenta or ""
    username = prompt_input(
        "Usuario de tu cuenta Instagram%s: " % (f" [{username_default}]" if username_default else ""),
        default=username_default or None,
        required=True,
    )
    password = prompt_input("Password (no se mostrará): ", secret=True, required=True)

    proxy_default = args.proxy or ""
    proxy = prompt_input(
        "Proxy opcional (ej. http://usuario:pass@host:puerto) [%s]: " % (proxy_default or ""),
        default=proxy_default or None,
    )

    print("\nObjetivos")
    print("----------")
    use_file = prompt_bool("¿Quieres cargar los usernames desde un archivo?", default=bool(args.targets_file))
    targets: List[str] = []
    targets_file: Optional[str] = None
    if use_file:
        default_file = args.targets_file or "usernames.txt"
        targets_file = prompt_input(f"Ruta del archivo con usernames [{default_file}]: ", default=default_file, required=True)
    else:
        default_targets = " ".join(args.targets or [])
        raw_targets = prompt_input(
            "Ingresa los usernames separados por espacio (ej. usuario1 usuario2)%s: "
            % (f" [{default_targets}]" if default_targets else ""),
            default=default_targets or None,
            required=True,
        )
        targets = [item.strip().lstrip("@") for item in raw_targets.replace(",", " ").split() if item.strip()]

    out_default = args.out_file or "result.csv"
    out_file = prompt_input(f"Archivo de salida CSV [{out_default}]: ", default=out_default, required=True)

    delay = prompt_float("Segundos de espera entre consultas", default=args.delay or 2.0)

    print("\nConfiguración lista. Iniciando scraping...\n")

    return argparse.Namespace(
        session=session_file,
        username_mi_cuenta=username,
        password=password,
        proxy=proxy or None,
        targets=targets or None,
        targets_file=targets_file,
        out_file=out_file,
        delay=delay,
        menu=True,
    )


def login_client(
    session_file: Optional[str] = None,
    username: Optional[str] = None,
    password: Optional[str] = None,
    proxy: Optional[str] = None,
) -> Client:
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)
    if session_file and Path(session_file).exists():
        try:
            cl.load_settings(session_file)
            if username and password:
                cl.login(username, password)
                return cl
            print("[WARN] Se cargaron ajustes guardados, pero faltan credenciales para iniciar sesión.")
        except Exception as exc:
            print(f"[!] No se pudo cargar la sesión guardada: {exc}")
    if not username or not password:
        raise ValueError("Se requieren username y password para iniciar sesión.")
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        code = prompt_input("Código 2FA: ", required=True)
        cl.login(username, password, verification_code=code)
    except ChallengeRequired:
        print("Challenge requerido. Completa desde el dispositivo o navegador.")
        raise
    if session_file:
        try:
            cl.dump_settings(session_file)
        except Exception as exc:
            print(f"[WARN] No se pudo guardar la sesión en {session_file}: {exc}")
    return cl


def fetch_user_info(cl: Client, username: str) -> Dict[str, Any]:
    try:
        user = cl.user_info_by_username(username)
    except ClientError as exc:
        return {"username": username, "error": str(exc)}

    def g(obj: Any, *names: str, default=None):
        for name in names:
            val = getattr(obj, name, None)
            if val is not None:
                return val
        return default

    followers = g(user, "follower_count", "followers_count", "followerCount")
    media_count = g(user, "media_count")
    is_private = g(user, "is_private")
    is_verified = g(user, "is_verified")
    biography = g(user, "biography", default="") or ""
    biography = biography.replace("\r", " ").replace("\n", " ").strip()
    has_highlights = g(
        user,
        "has_highlight_reels",
        "has_highlight_reel",
        "highlight_reel_count",
        default=False,
    )
    if isinstance(has_highlights, (int, float)):
        has_highlights = has_highlights > 0

    return {
        "username": g(user, "username", default=username),
        "pk": g(user, "pk"),
        "full_name": g(user, "full_name", default=""),
        "followers": followers,
        "media_count": media_count,
        "is_private": bool(is_private),
        "is_public": not bool(is_private) if is_private is not None else "",
        "is_verified": bool(is_verified),
        "biography": biography,
        "has_highlight_reels": bool(has_highlights),
        "follower_bucket": follower_bucket(followers) if isinstance(followers, int) else "unknown",
    }


def run_scraper(args: argparse.Namespace) -> None:
    targets: List[str] = []
    if args.targets_file:
        try:
            targets.extend(load_targets_from_file(args.targets_file))
        except FileNotFoundError as exc:
            print(f"[ERROR] {exc}")
            sys.exit(1)
    if args.targets:
        targets.extend([t.strip().lstrip("@") for t in args.targets if t.strip()])
    if not targets:
        print("No hay targets. Usa --targets, --targets-file o el modo interactivo con --menu.")
        sys.exit(1)

    try:
        client = login_client(
            session_file=args.session,
            username=args.username_mi_cuenta,
            password=args.password,
            proxy=args.proxy,
        )
    except Exception as exc:
        print(f"[ERROR] Login falló: {exc}")
        sys.exit(2)

    results: List[Dict[str, Any]] = []
    for idx, username in enumerate(targets, start=1):
        print(f"[{idx}/{len(targets)}] consultando @{username} ...")
        info = fetch_user_info(client, username)
        results.append(info)
        time.sleep(args.delay)

    keys = [
        "username",
        "pk",
        "full_name",
        "followers",
        "media_count",
        "is_private",
        "is_public",
        "is_verified",
        "biography",
        "has_highlight_reels",
        "follower_bucket",
        "error",
    ]
    with open(args.out_file, "w", newline="", encoding="utf-8") as handler:
        writer = csv.DictWriter(handler, fieldnames=keys)
        writer.writeheader()
        for item in results:
            writer.writerow({key: item.get(key, "") for key in keys})
    print(f"Guardado CSV -> {args.out_file}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Scraper básico de Instagram (instagrapi) - CLI")
    parser.add_argument("--session", help="Archivo session.json", default="session.json")
    parser.add_argument("--username-mi-cuenta", help="Usuario para login (si no usas session existente)")
    parser.add_argument("--password", help="Password para login")
    parser.add_argument("--proxy", help="Proxy opcional")
    parser.add_argument("--targets", nargs="*", help="Lista de usernames objetivo")
    parser.add_argument("--targets-file", help="Archivo con usernames (uno por línea)")
    parser.add_argument("--out-file", default="result.csv")
    parser.add_argument("--delay", type=float, default=2.0, help="Segundos de espera entre requests")
    parser.add_argument("--menu", action="store_true", help="Mostrar menú interactivo")
    return parser


def main() -> None:
    parser = build_parser()
    args = parser.parse_args()

    if args.menu or (not args.targets and not args.targets_file):
        args = interactive_menu(args)

    run_scraper(args)


if __name__ == "__main__":
    main()
