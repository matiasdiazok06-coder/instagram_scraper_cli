#!/usr/bin/env python3
"""
cli.py - Extrae info básica de usuarios de Instagram usando instagrapi.
"""

import argparse
import csv
import json
import sys
import time
from pathlib import Path
from typing import Any, Dict, List

from instagrapi import Client
from instagrapi.exceptions import ClientError, ChallengeRequired, TwoFactorRequired


def save_json(path: str, data):
    Path(path).write_text(json.dumps(data, indent=2, ensure_ascii=False))


def load_targets_from_file(path: str) -> List[str]:
    return [line.strip() for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def follower_bucket(n: int) -> str:
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


def login_client(session_file: str = None, username: str = None, password: str = None, proxy: str = None) -> Client:
    cl = Client()
    if proxy:
        cl.set_proxy(proxy)
    if session_file and Path(session_file).exists():
        try:
            cl.load_settings(session_file)
            cl.login(username or "", password or "")
            return cl
        except Exception as e:
            print(f"[!] No se pudo cargar sesión: {e}")
    if not username or not password:
        raise ValueError("Se requieren username y password si no hay session existente.")
    try:
        cl.login(username, password)
    except TwoFactorRequired:
        code = input("Código 2FA: ").strip()
        cl.login(username, password, verification_code=code)
    except ChallengeRequired:
        print("Challenge requerido. Completa desde el dispositivo o navegador.")
        raise
    if session_file:
        cl.dump_settings(session_file)
    return cl


def fetch_user_info(cl: Client, username: str) -> Dict[str, Any]:
    try:
        user = cl.user_info_by_username(username)
    except ClientError as e:
        return {"username": username, "error": str(e)}
    def g(obj, *names, default=None):
        for n in names:
            val = getattr(obj, n, None)
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


def main():
    p = argparse.ArgumentParser(description="Scraper básico de Instagram (instagrapi) - CLI")
    p.add_argument("--session", help="Archivo session.json", default="session.json")
    p.add_argument("--username-mi-cuenta", help="Usuario para login (si no usas session existente)")
    p.add_argument("--password", help="Password para login")
    p.add_argument("--proxy", help="Proxy opcional")
    p.add_argument("--targets", nargs="*", help="Lista de usernames objetivo")
    p.add_argument("--targets-file", help="Archivo con usernames (uno por línea)")
    p.add_argument("--out-file", default="result.csv")
    p.add_argument("--delay", type=float, default=2.0, help="Segundos de espera entre requests")
    args = p.parse_args()

    targets: List[str] = []
    if args.targets_file:
        targets += load_targets_from_file(args.targets_file)
    if args.targets:
        targets += args.targets
    if not targets:
        print("No hay targets. Usa --targets o --targets-file.")
        sys.exit(1)

    try:
        cl = login_client(session_file=args.session, username=args.username_mi_cuenta, password=args.password, proxy=args.proxy)
    except Exception as e:
        print(f"[ERROR] Login fallo: {e}")
        sys.exit(2)

    results = []
    for i, t in enumerate(targets, start=1):
        print(f"[{i}/{len(targets)}] consultando @{t} ...")
        info = fetch_user_info(cl, t)
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
    with open(args.out_file, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for r in results:
            writer.writerow({k: r.get(k, "") for k in keys})
    print(f"Guardado CSV -> {args.out_file}")


if __name__ == "__main__":
    main()
