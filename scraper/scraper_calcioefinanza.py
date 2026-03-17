"""Scraping diretto di Calcio e Finanza per le categorie business/finanza."""

from __future__ import annotations

import logging

import requests
from bs4 import BeautifulSoup

from config import CALCIO_FINANZA_BASE_URL, CALCIO_FINANZA_CATEGORIES, MA_KEYWORDS

logger = logging.getLogger(__name__)

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}


def _matches_keywords(text: str) -> bool:
    text_lower = text.lower()
    return any(kw.lower() in text_lower for kw in MA_KEYWORDS)


def _scrape_category(path: str) -> list[dict]:
    """Scrape una singola pagina di categoria."""
    url = f"{CALCIO_FINANZA_BASE_URL}{path}"
    logger.info("Scraping: %s", url)

    try:
        resp = requests.get(url, headers=HEADERS, timeout=30)
        resp.raise_for_status()
    except Exception:
        logger.exception("Errore fetch %s", url)
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    articles: list[dict] = []

    # Cerca articoli nella pagina della categoria
    for article_tag in soup.select("article, .post, .entry"):
        # Titolo
        title_tag = article_tag.select_one("h2 a, h3 a, .entry-title a")
        if not title_tag:
            continue

        title = title_tag.get_text(strip=True)
        link = title_tag.get("href", "")

        # Estratto / sommario
        excerpt_tag = article_tag.select_one(
            ".entry-summary, .excerpt, .post-excerpt, p"
        )
        summary = excerpt_tag.get_text(strip=True)[:500] if excerpt_tag else ""

        # Data
        time_tag = article_tag.select_one("time, .entry-date, .post-date")
        published = ""
        if time_tag:
            published = time_tag.get("datetime", time_tag.get_text(strip=True))

        combined = f"{title} {summary}"
        if not _matches_keywords(combined):
            continue

        articles.append(
            {
                "title": title,
                "link": link,
                "source": "Calcio e Finanza (scraping)",
                "published": published,
                "summary": summary,
            }
        )

    return articles


def scrape_calcioefinanza() -> list[dict]:
    """Scrape tutte le categorie configurate di Calcio e Finanza.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    all_articles: list[dict] = []
    for cat_path in CALCIO_FINANZA_CATEGORIES:
        all_articles.extend(_scrape_category(cat_path))

    logger.info(
        "Calcio e Finanza scraping: %d articoli raccolti", len(all_articles)
    )
    return all_articles
