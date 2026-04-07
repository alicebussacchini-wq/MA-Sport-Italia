"""Raccoglie notizie da Google News tramite feed RSS (gratis, no API key).

Sostituisce la versione SerpApi — stessi risultati, zero crediti.
"""

from __future__ import annotations

import logging
import urllib.parse
from datetime import datetime, timezone

import feedparser

from config import GOOGLE_NEWS_QUERIES

logger = logging.getLogger(__name__)

GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search"


def collect_google_news() -> list[dict]:
    """Interroga Google News RSS per ciascuna query M&A configurata.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    articles: list[dict] = []
    seen_links: set[str] = set()

    for query in GOOGLE_NEWS_QUERIES:
        logger.info("Google News RSS query: %s", query)
        try:
            params = urllib.parse.urlencode({
                "q": query,
                "hl": "it",
                "gl": "IT",
                "ceid": "IT:it",
            })
            url = f"{GOOGLE_NEWS_RSS_BASE}?{params}"
            feed = feedparser.parse(url)

            for entry in feed.entries:
                link = entry.get("link", "")
                if link in seen_links:
                    continue
                seen_links.add(link)

                # Google News RSS ha il nome fonte in <source>
                source_name = "Google News"
                if hasattr(entry, "source") and hasattr(entry.source, "title"):
                    source_name = entry.source.title

                published = entry.get("published", "")
                if hasattr(entry, "published_parsed") and entry.published_parsed:
                    try:
                        published = datetime(
                            *entry.published_parsed[:6], tzinfo=timezone.utc
                        ).isoformat()
                    except Exception:
                        pass

                title = entry.get("title", "")
                # Google News spesso appende " - NomeFonte" al titolo
                if " - " in title and source_name != "Google News":
                    title = title.rsplit(" - ", 1)[0].strip()

                articles.append({
                    "title": title,
                    "link": link,
                    "source": source_name,
                    "published": published,
                    "summary": entry.get("summary", "")[:500],
                })

        except Exception:
            logger.exception("Errore Google News RSS per query '%s'", query)

    logger.info("Google News RSS totale: %d articoli raccolti", len(articles))
    return articles
