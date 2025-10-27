"""High level scraping workflows for the Instagram CLI."""
from __future__ import annotations

import logging
import random
import time
from dataclasses import dataclass
from pathlib import Path
from typing import Iterable, List

from instagrapi import Client
from instagrapi.exceptions import (
    ChallengeRequired,
    ClientConnectionError,
    ClientError,
    ClientLoginError,
    LoginRequired,
    PleaseWaitFewMinutes,
    PrivateError,
    RateLimitError,
    TwoFactorRequired,
    UserNotFound,
)

from filters import FilterCriteria, apply_filters
from utils import load_session_meta

logger = logging.getLogger(__name__)

DEFAULT_DELAY = (2.0, 5.0)


@dataclass
class ScraperResult:
    rows: List[dict]
    description: str


class ScraperService:
    """Encapsula el acceso al cliente de instagrapi y operaciones de scraping."""

    def __init__(self, session_path: Path) -> None:
        self.session_path = session_path
        self.client: Client | None = None
        self.logged_username: str | None = None
        self._authenticated: bool = False

        self._try_restore_session()

    # ------------------------------------------------------------------
    # Login / sesión
    # ------------------------------------------------------------------
    def ensure_client(self) -> Client:
        if self.client is None:
            self.client = Client()
            if self.session_path.exists():
                try:
                    self.client.load_settings(str(self.session_path))
                    logger.info("Sesión previa cargada desde %s", self.session_path)
                except Exception as exc:  # pragma: no cover
                    logger.warning("No fue posible cargar la sesión previa: %s", exc)
        return self.client

    def mark_authenticated(self, username: str | None = None) -> None:
        self._authenticated = True
        if username:
            self.logged_username = username

    def _try_restore_session(self) -> None:
        """Restores the persisted session if it is still valid."""
        if not self.session_path.exists():
            return

        try:
            client = self.ensure_client()
        except Exception as exc:  # pragma: no cover - fallo inesperado al cargar ajustes
            logger.warning("No se pudo inicializar el cliente con la sesión guardada: %s", exc)
            return

        try:
            client.account_info()
        except (LoginRequired, ClientLoginError):
            logger.info("La sesión almacenada requiere autenticación nuevamente.")
            return
        except Exception as exc:  # pragma: no cover - errores no anticipados
            logger.warning("No se pudo validar la sesión almacenada: %s", exc)
            return

        meta = load_session_meta()
        username = meta.get("username") if isinstance(meta, dict) else None
        self.mark_authenticated(username)
        if username:
            logger.info("Sesión restaurada automáticamente para %s", username)
        else:
            logger.info("Sesión restaurada automáticamente.")

    def login(self, username: str, password: str, verification_code: str | None = None) -> None:
        client = self.ensure_client()
        try:
            client.login(username, password, verification_code=verification_code)
        except TwoFactorRequired as exc:
            raise
        except ChallengeRequired as exc:
            raise RuntimeError(
                "Instagram solicitó un challenge adicional. Resuélvelo en la app oficial y vuelve a intentar."
            ) from exc
        except (RateLimitError, PleaseWaitFewMinutes) as exc:
            raise RuntimeError(
                "Instagram aplicó un rate limit. Espera unos minutos antes de intentarlo nuevamente."
            ) from exc
        except (ClientConnectionError, ConnectionError) as exc:  # type: ignore[arg-type]
            raise RuntimeError("No fue posible conectar con Instagram. Verifica tu conexión o proxy.") from exc
        except (ClientLoginError, LoginRequired) as exc:
            raise RuntimeError("Instagram rechazó las credenciales. Verifica usuario y contraseña.") from exc
        except ClientError as exc:
            raise RuntimeError(f"No se pudo iniciar sesión: {exc}") from exc

        try:
            client.dump_settings(str(self.session_path))
        except Exception as exc:  # pragma: no cover
            logger.warning("No se pudo guardar la sesión: %s", exc)
        self.logged_username = username
        self._authenticated = True

    def is_logged_in(self) -> bool:
        return self._authenticated

    # ------------------------------------------------------------------
    # Scraping helpers
    # ------------------------------------------------------------------
    def _sleep(self) -> None:
        start, end = DEFAULT_DELAY
        time.sleep(random.uniform(start, end))

    def _ensure_login(self) -> Client:
        client = self.ensure_client()
        if not self.is_logged_in():
            raise RuntimeError("Debes iniciar sesión antes de continuar.")
        return client

    def _serialize_user(self, info) -> dict:
        return {
            "username": getattr(info, "username", ""),
            "full_name": getattr(info, "full_name", ""),
            "followers": getattr(info, "follower_count", getattr(info, "followers_count", None)),
            "following": getattr(info, "following_count", getattr(info, "following", None)),
            "media_count": getattr(info, "media_count", None),
            "is_private": getattr(info, "is_private", False),
            "is_verified": getattr(info, "is_verified", False),
            "has_highlight_reels": getattr(info, "has_highlight_reels", False),
        }

    def scrape_hashtag(
        self,
        hashtag: str,
        amount: int,
        criteria: FilterCriteria | None = None,
    ) -> ScraperResult:
        client = self._ensure_login()
        seen_users: set[int] = set()
        collected: List[dict] = []
        try:
            medias = client.hashtag_medias_recent(hashtag, amount=amount)
        except ClientError as exc:
            raise RuntimeError(f"Instagram rechazó la consulta del hashtag: {exc}") from exc

        for media in medias:
            user = getattr(media, "user", None)
            if not user:
                continue
            if user.pk in seen_users:
                continue
            seen_users.add(user.pk)
            try:
                info = client.user_info(user.pk)
            except PrivateError:
                row = {
                    "username": user.username,
                    "full_name": user.full_name,
                    "followers": None,
                    "following": None,
                    "media_count": None,
                    "is_private": True,
                    "is_verified": getattr(user, "is_verified", False),
                    "has_highlight_reels": False,
                }
            except UserNotFound:
                continue
            except (RateLimitError, PleaseWaitFewMinutes) as exc:
                raise RuntimeError(
                    "Instagram aplicó un rate limit durante la consulta. Espera antes de continuar."
                ) from exc
            else:
                row = self._serialize_user(info)
            collected.append(row)
            self._sleep()

        if criteria:
            filtered_rows = apply_filters(collected, criteria)
        else:
            filtered_rows = collected
        description = (
            f"Hashtag #{hashtag} - {len(filtered_rows)} cuentas" + (
                f" (de {len(collected)} encontradas)" if criteria else ""
            )
        )
        return ScraperResult(filtered_rows, description)

    def scrape_profile_relations(
        self,
        usernames: Iterable[str],
        relation: str,
        criteria: FilterCriteria | None = None,
    ) -> dict[str, ScraperResult]:
        client = self._ensure_login()
        relation = relation.lower()
        if relation not in {"followers", "following"}:
            raise ValueError("La relación debe ser 'followers' o 'following'.")

        responses: dict[str, ScraperResult] = {}
        for username in usernames:
            username = username.strip()
            if not username:
                continue
            try:
                user_id = client.user_id_from_username(username)
            except UserNotFound:
                raise RuntimeError(f"El usuario {username} no existe o es inaccesible.")

            try:
                if relation == "followers":
                    relation_data = client.user_followers(user_id)
                else:
                    relation_data = client.user_following(user_id)
            except (RateLimitError, PleaseWaitFewMinutes) as exc:
                raise RuntimeError(
                    "Instagram aplicó un rate limit mientras se consultaban relaciones."
                ) from exc
            except PrivateError as exc:
                raise RuntimeError(f"La cuenta {username} es privada y no se puede consultar.") from exc

            rows: List[dict] = []
            for short_user in relation_data.values():
                try:
                    info = client.user_info(short_user.pk)
                except PrivateError:
                    row = {
                        "username": short_user.username,
                        "full_name": short_user.full_name,
                        "followers": None,
                        "following": None,
                        "media_count": None,
                        "is_private": True,
                        "is_verified": getattr(short_user, "is_verified", False),
                        "has_highlight_reels": False,
                    }
                except UserNotFound:
                    continue
                else:
                    row = self._serialize_user(info)
                row["source"] = username
                rows.append(row)
                self._sleep()

            final_rows = apply_filters(rows, criteria) if criteria else rows
            responses[username] = ScraperResult(
                final_rows,
                f"{relation.title()} de {username}: {len(final_rows)} resultados",
            )
        return responses
