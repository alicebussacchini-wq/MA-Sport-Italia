"""Raccoglie notizie site-specific tramite Google News RSS (gratis).

Sostituisce finanza_sport.py e sport_business.py che usavano SerpApi.
Combina query site: da entrambi i moduli in un unico scraper RSS.
Filtra solo notizie recenti (ultimi 30 giorni).
"""

from __future__ import annotations

import logging
import urllib.parse
from datetime import datetime, timezone, timedelta

import feedparser

logger = logging.getLogger(__name__)

MAX_AGE_DAYS = 30


def _is_recent(entry, cutoff: datetime) -> bool:
    """Verifica che l'articolo sia recente (dopo cutoff)."""
    if hasattr(entry, "published_parsed") and entry.published_parsed:
        try:
            pub_dt = datetime(*entry.published_parsed[:6], tzinfo=timezone.utc)
            return pub_dt >= cutoff
        except Exception:
            pass
    return True

GOOGLE_NEWS_RSS_BASE = "https://news.google.com/rss/search"

# Query consolidate da finanza_sport.py e sport_business.py
# Ridotte e ottimizzate per evitare sovrapposizioni con RSS_FEEDS
SITE_QUERIES = [
    # --- Stampa finanziaria italiana ---
    "site:milanofinanza.it sport calcio cessione OR acquisizione OR investitore",
    "site:repubblica.it economia sport acquisizione OR cessione OR investimento",
    "site:ilfattoquotidiano.it calcio cessione OR vendita OR proprietario OR fondo",
    "site:corriere.it economia sport acquisizione OR cessione",
    "site:lastampa.it calcio cessione OR acquisizione OR investitore",
    # --- Deal tracker e PE italiani ---
    "site:bebeez.it sport OR calcio OR stadio private equity acquisizione",
    "site:diritto24.ilsole24ore.com sport calcio stadio",
    # --- Fonti internazionali autorevoli ---
    "site:bloomberg.com football club acquisition OR investment Italy",
    "site:ft.com sport M&A deal acquisition Italy",
    "site:reuters.com Serie A club ownership investor deal",
    "site:sky.it sport cessione OR acquisizione OR proprietario",
    # --- Query generiche ad alto valore ---
    "football club deal investor private equity Europe Serie A",
    "sovereign wealth fund football club Europe investment acquisition",
    "Italia sport M&A closing signing advisor 2025 2026",
    "cessione quote club calcio Serie B Serie C Italia",
]


def collect_site_news() -> list[dict]:
    """Cerca notizie M&A sport da fonti specifiche via Google News RSS.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    articles: list[dict] = []
    seen_links: set[str] = set()
    cutoff = datetime.now(timezone.utc) - timedelta(days=MAX_AGE_DAYS)

    for query in SITE_QUERIES:
        logger.info("Site News RSS query: %s", query)
        try:
            full_query = f"{query} when:30d"
            params = urllib.parse.urlencode({
                "q": full_query,
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
                if not _is_recent(entry, cutoff):
                    continue
                seen_links.add(link)

                source_name = "News"
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
                if " - " in title and source_name != "News":
                    title = title.rsplit(" - ", 1)[0].strip()

                articles.append({
                    "title": title,
                    "link": link,
                    "source": source_name,
                    "published": published,
                    "summary": entry.get("summary", "")[:500],
                })

        except Exception:
            logger.exception("Errore Site News RSS per query: %s", query)

    logger.info("Site News RSS: %d articoli raccolti", len(articles))
    return articles
