"""Filtering logic for Instagram scraper results."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List, Optional


@dataclass
class FilterCriteria:
    min_followers: Optional[int] = None
    max_followers: Optional[int] = None
    min_posts: Optional[int] = None
    require_public: Optional[bool] = None
    require_verified: Optional[bool] = None
    require_highlights: Optional[bool] = None

    def describe(self) -> List[str]:
        messages: List[str] = []
        if self.min_followers is not None or self.max_followers is not None:
            messages.append(
                f"Seguidores entre {self.min_followers or 0} y {self.max_followers or '∞'}"
            )
        if self.min_posts:
            messages.append(f"Mínimo {self.min_posts} publicaciones")
        if self.require_public is not None:
            messages.append("Solo cuentas públicas" if self.require_public else "Solo cuentas privadas")
        if self.require_verified:
            messages.append("Solo cuentas verificadas")
        if self.require_highlights:
            messages.append("Solo cuentas con historias destacadas")
        return messages


def apply_filters(rows: Iterable[dict], criteria: FilterCriteria) -> List[dict]:
    filtered: List[dict] = []
    for row in rows:
        followers = row.get("followers")
        media_count = row.get("media_count") or row.get("posts")
        is_private = row.get("is_private")
        is_verified = row.get("is_verified")
        has_highlights = row.get("has_highlight_reels") or row.get("has_highlights")

        if criteria.min_followers is not None and (followers is None or followers < criteria.min_followers):
            continue
        if criteria.max_followers is not None and (followers is None or followers > criteria.max_followers):
            continue
        if criteria.min_posts is not None and (media_count is None or media_count < criteria.min_posts):
            continue
        if criteria.require_public is not None:
            if criteria.require_public and is_private:
                continue
            if not criteria.require_public and not is_private:
                continue
        if criteria.require_verified is True and not is_verified:
            continue
        if criteria.require_highlights is True and not has_highlights:
            continue
        filtered.append(row)
    return filtered
