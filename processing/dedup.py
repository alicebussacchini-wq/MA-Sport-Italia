"""Deduplicazione notizie tramite hash del titolo."""

from __future__ import annotations

import hashlib
import logging

logger = logging.getLogger(__name__)


def _title_hash(title: str) -> str:
    """Genera un hash MD5 del titolo normalizzato."""
    normalized = title.strip().lower()
    return hashlib.md5(normalized.encode("utf-8")).hexdigest()


def deduplicate(articles: list[dict]) -> list[dict]:
    """Rimuove articoli duplicati basandosi sull'hash del titolo.

    Args:
        articles: Lista di articoli (dict con chiave 'title').

    Returns:
        Lista deduplicata preservando l'ordine originale.
    """
    seen_hashes: set[str] = set()
    unique: list[dict] = []

    for art in articles:
        h = _title_hash(art.get("title", ""))
        if h in seen_hashes:
            continue
        seen_hashes.add(h)
        art["title_hash"] = h
        unique.append(art)

    removed = len(articles) - len(unique)
    if removed:
        logger.info("Dedup: rimossi %d duplicati, restano %d", removed, len(unique))
    return unique
