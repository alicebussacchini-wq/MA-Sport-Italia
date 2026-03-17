"""Raccoglie articoli dai feed RSS delle testate italiane."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import feedparser

from config import RSS_FEEDS, MA_KEYWORDS

logger = logging.getLogger(__name__)


def _matches_keywords(text: str) -> bool:
    """Pre-filtro rapido su keyword M&A (case-insensitive)."""
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in MA_KEYWORDS)


def collect_rss() -> list[dict]:
    """Scarica e filtra gli articoli dai feed RSS configurati.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    articles: list[dict] = []

    for source_name, feed_url in RSS_FEEDS.items():
        logger.info("Fetching RSS: %s", source_name)
        try:
            feed = feedparser.parse(feed_url)
        except Exception:
            logger.exception("Errore parsing RSS %s", source_name)
            continue

        for entry in feed.entries:
            title = entry.get("title", "")
            summary = entry.get("summary", entry.get("description", ""))
            combined = f"{title} {summary}"

            if not _matches_keywords(combined):
                continue

            published = entry.get("published", "")
            if hasattr(entry, "published_parsed") and entry.published_parsed:
                try:
                    published = datetime(
                        *entry.published_parsed[:6], tzinfo=timezone.utc
                    ).isoformat()
                except Exception:
                    pass

            articles.append(
                {
                    "title": title,
                    "link": entry.get("link", ""),
                    "source": source_name,
                    "published": published,
                    "summary": summary[:500],
                }
            )

        logger.info("  -> %d articoli dopo pre-filtro da %s", len(articles), source_name)

    logger.info("RSS totale: %d articoli raccolti", len(articles))
    return articles
