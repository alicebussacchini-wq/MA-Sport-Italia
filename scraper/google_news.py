"""Raccoglie notizie da Google News tramite SerpApi."""

from __future__ import annotations

import logging

import requests

from config import SERPAPI_KEY, GOOGLE_NEWS_QUERIES

logger = logging.getLogger(__name__)

SERPAPI_ENDPOINT = "https://serpapi.com/search.json"


def collect_google_news() -> list[dict]:
    """Interroga SerpApi per ciascuna query M&A configurata.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    if not SERPAPI_KEY:
        logger.warning("SERPAPI_KEY non configurata – skip Google News")
        return []

    articles: list[dict] = []

    for query in GOOGLE_NEWS_QUERIES:
        logger.info("Google News query: %s", query)
        try:
            resp = requests.get(
                SERPAPI_ENDPOINT,
                params={
                    "engine": "google_news",
                    "q": query,
                    "gl": "it",
                    "hl": "it",
                    "api_key": SERPAPI_KEY,
                },
                timeout=30,
            )
            resp.raise_for_status()
            data = resp.json()
        except Exception:
            logger.exception("Errore SerpApi per query '%s'", query)
            continue

        for item in data.get("news_results", []):
            articles.append(
                {
                    "title": item.get("title", ""),
                    "link": item.get("link", ""),
                    "source": item.get("source", {}).get("name", "Google News"),
                    "published": item.get("date", ""),
                    "summary": item.get("snippet", "")[:500],
                }
            )

        # Gestisci anche sotto-storie (stories con sub_results)
        for item in data.get("news_results", []):
            for sub in item.get("stories", []):
                articles.append(
                    {
                        "title": sub.get("title", ""),
                        "link": sub.get("link", ""),
                        "source": sub.get("source", {}).get("name", "Google News"),
                        "published": sub.get("date", ""),
                        "summary": sub.get("snippet", "")[:500],
                    }
                )

    logger.info("Google News totale: %d articoli raccolti", len(articles))
    return articles
