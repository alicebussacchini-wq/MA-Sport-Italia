"""Scraper per notizie M&A sport da testate finanziarie italiane.

Cerca notizie da fonti come MF/Milano Finanza, ANSA, Il Fatto Quotidiano,
La Repubblica Economia — focalizzate su operazioni societarie nello sport.
"""

from __future__ import annotations

import logging

import requests

from config import SERPAPI_KEY

logger = logging.getLogger(__name__)

# Query mirate per stampa finanziaria italiana
FINANZA_SPORT_QUERIES = [
    # Milano Finanza
    "site:milanofinanza.it sport calcio cessione OR acquisizione OR investitore",
    "site:milanofinanza.it Serie A fondo OR private equity OR quotazione",
    # La Repubblica Economia
    "site:repubblica.it economia sport acquisizione OR cessione OR investimento",
    # Il Fatto Quotidiano
    "site:ilfattoquotidiano.it calcio cessione OR vendita OR proprietario OR fondo",
    # Corriere della Sera Economia
    "site:corriere.it economia sport club OR societa acquisizione OR cessione",
    # ANSA — operazioni societarie sport
    "site:ansa.it sport calcio cessione OR acquisizione OR investitore OR fondo",
    # BeBeez (PE/VC italiano)
    "site:bebeez.it sport OR calcio OR stadio",
    # Italia Oggi
    "site:italiaoggi.it calcio OR sport cessione OR acquisizione OR fondo",
]


def collect_finanza_sport() -> list[dict]:
    """Cerca notizie M&A sport dalla stampa finanziaria italiana.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    if not SERPAPI_KEY:
        logger.warning("SERPAPI_KEY non configurata - skip Finanza Sport scraper")
        return []

    articles: list[dict] = []
    seen_links: set[str] = set()

    for query in FINANZA_SPORT_QUERIES:
        logger.info("Finanza Sport query: %s", query)
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

                source_name = result.get("source", "")
                if not source_name:
                    source_name = "Finanza Sport"

                articles.append({
                    "title": result.get("title", ""),
                    "link": link,
                    "source": source_name,
                    "published": result.get("date", ""),
                    "summary": result.get("snippet", "")[:500],
                })

        except Exception:
            logger.exception("Errore query Finanza Sport: %s", query)

    logger.info("Finanza Sport: %d articoli raccolti", len(articles))
    return articles
