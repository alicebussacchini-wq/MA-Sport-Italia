"""Raccoglie intelligence M&A sport Italia da Mergermarket.

Mergermarket richiede SSO — il login automatico non e supportato.
Strategia alternativa:
1. Cerca notizie Mergermarket indicizzate su Google (fonti pubbliche)
2. La dashboard permette import manuale CSV di dati esportati da Mergermarket
"""

from __future__ import annotations

import logging

import requests

from config import SERPAPI_KEY

logger = logging.getLogger(__name__)

# Query Google News filtrate per contenuti Mergermarket + M&A sport Italia
MERGERMARKET_QUERIES = [
    "mergermarket sport Italy acquisition",
    "mergermarket calcio cessione acquisizione Italia",
    "mergermarket Serie A football club deal investor",
    "mergermarket sport M&A Italy private equity",
]


def collect_mergermarket() -> list[dict]:
    """Cerca notizie Mergermarket indicizzate pubblicamente via Google News.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    if not SERPAPI_KEY:
        logger.warning("SERPAPI_KEY non configurata - skip Mergermarket")
        return []

    articles: list[dict] = []
    seen_links: set[str] = set()

    for query in MERGERMARKET_QUERIES:
        logger.info("Mergermarket query: %s", query)
        try:
            params = {
                "engine": "google",
                "q": query,
                "api_key": SERPAPI_KEY,
                "num": 10,
                "gl": "it",
                "hl": "it",
                "tbm": "nws",
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

                articles.append({
                    "title": result.get("title", ""),
                    "link": link,
                    "source": "Mergermarket",
                    "published": result.get("date", ""),
                    "summary": result.get("snippet", "")[:500],
                })

        except Exception:
            logger.exception("Errore query Mergermarket: %s", query)

    logger.info("Mergermarket: %d articoli raccolti", len(articles))
    return articles
