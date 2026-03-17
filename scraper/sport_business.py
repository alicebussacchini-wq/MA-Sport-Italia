"""Scraper aggiuntivo per testate sport-business via Google News (SerpApi).

Cerca notizie M&A sport da fonti autorevoli internazionali che non hanno
RSS affidabili: SportBusiness, Bloomberg, Financial Times, Sky Sport Business.
"""

from __future__ import annotations

import logging

import requests

from config import SERPAPI_KEY

logger = logging.getLogger(__name__)

# Query mirate per fonti autorevoli sport-business
SPORT_BIZ_QUERIES = [
    # Bloomberg / FT / Reuters — deal sport
    "site:bloomberg.com football club acquisition OR investment OR deal",
    "site:ft.com sport M&A deal OR acquisition Italy",
    "site:reuters.com Serie A club ownership OR investor OR deal",
    # Sky Sport — sezione business
    "site:sport.sky.it cessione OR acquisizione OR proprietario OR investitore",
    # Calcio e Finanza — articoli piu recenti
    "site:calcioefinanza.it acquisizione OR cessione OR fondo OR investitore",
    # Sport Business internazionale
    "SportBusiness football acquisition OR investment Italy 2025 2026",
    "football club deal investor private equity Europe Serie A",
    # Gazzetta sezione economia sport
    "site:gazzetta.it cessione OR acquisizione OR proprietario societa",
]


def collect_sport_business() -> list[dict]:
    """Cerca notizie sport-business da fonti autorevoli via Google.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    if not SERPAPI_KEY:
        logger.warning("SERPAPI_KEY non configurata - skip Sport Business scraper")
        return []

    articles: list[dict] = []
    seen_links: set[str] = set()

    for query in SPORT_BIZ_QUERIES:
        logger.info("Sport Business query: %s", query)
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": SERPAPI_KEY,
                "num": 10,
                "gl": "it",
                "hl": "it",
                "tbm": "nws",
                "tbs": "qdr:w",  # ultima settimana
            }
            resp = requests.get(
                "https://serpapi.com/search", params=params, timeout=30
            )
            resp.raise_for_status()
            data = resp.json()

            for result in data.get("news_results", []):
                link = result.get("link", "")
                if link in seen_links:
                    continue
                seen_links.add(link)

                # Identifica la fonte reale
                source_name = result.get("source", "")
                if not source_name:
                    source_name = "Sport Business"

                articles.append({
                    "title": result.get("title", ""),
                    "link": link,
                    "source": source_name,
                    "published": result.get("date", ""),
                    "summary": result.get("snippet", "")[:500],
                })

        except Exception:
            logger.exception("Errore query Sport Business: %s", query)

    logger.info("Sport Business: %d articoli raccolti", len(articles))
    return articles
