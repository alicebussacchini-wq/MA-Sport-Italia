"""Raccoglie notizie da Mergermarket (scraping con autenticazione)."""

from __future__ import annotations

import logging

import requests
from bs4 import BeautifulSoup

from config import MERGERMARKET_EMAIL, MERGERMARKET_PASSWORD

logger = logging.getLogger(__name__)

LOGIN_URL = "https://www.mergermarket.com/login"
SEARCH_URL = "https://www.mergermarket.com/intelligence/search"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/124.0.0.0 Safari/537.36"
    )
}

# Query per notizie M&A sport Italia
SEARCH_QUERIES = [
    "Italy sport acquisition",
    "Italy football club deal",
    "Serie A investment",
    "Italy sport private equity",
]


def _login(session: requests.Session) -> bool:
    """Effettua il login su Mergermarket."""
    try:
        # Carica pagina di login per ottenere token CSRF
        resp = session.get(LOGIN_URL, headers=HEADERS, timeout=30)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        # Cerca token CSRF
        csrf_input = soup.select_one("input[name='_token'], input[name='csrf_token']")
        csrf_token = csrf_input["value"] if csrf_input else ""

        # Effettua login
        login_data = {
            "email": MERGERMARKET_EMAIL,
            "password": MERGERMARKET_PASSWORD,
            "_token": csrf_token,
        }
        login_resp = session.post(
            LOGIN_URL, data=login_data, headers=HEADERS, timeout=30
        )

        if login_resp.status_code == 200 and "dashboard" in login_resp.url.lower():
            logger.info("Mergermarket: login riuscito")
            return True

        # Prova anche verifica tramite cookie
        if any("session" in c.name.lower() for c in session.cookies):
            logger.info("Mergermarket: login riuscito (via cookie)")
            return True

        logger.warning("Mergermarket: login fallito (status %d)", login_resp.status_code)
        return False

    except Exception:
        logger.exception("Mergermarket: errore durante il login")
        return False


def _search_articles(session: requests.Session, query: str) -> list[dict]:
    """Cerca articoli su Mergermarket per una query."""
    articles = []
    try:
        resp = session.get(
            SEARCH_URL,
            params={"q": query, "sector": "leisure", "geography": "italy"},
            headers=HEADERS,
            timeout=30,
        )
        if resp.status_code != 200:
            logger.warning("Mergermarket search '%s': status %d", query, resp.status_code)
            return []

        soup = BeautifulSoup(resp.text, "html.parser")

        for item in soup.select(
            ".search-result, .intelligence-item, .article-item, article"
        ):
            title_tag = item.select_one("h2 a, h3 a, .title a, .headline a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            link = title_tag.get("href", "")
            if link and not link.startswith("http"):
                link = f"https://www.mergermarket.com{link}"

            excerpt_tag = item.select_one(
                ".excerpt, .summary, .snippet, p"
            )
            summary = excerpt_tag.get_text(strip=True)[:500] if excerpt_tag else ""

            date_tag = item.select_one("time, .date, .published-date")
            published = ""
            if date_tag:
                published = date_tag.get("datetime", date_tag.get_text(strip=True))

            articles.append({
                "title": title,
                "link": link,
                "source": "Mergermarket",
                "published": published,
                "summary": summary,
            })

    except Exception:
        logger.exception("Mergermarket: errore ricerca '%s'", query)

    return articles


def collect_mergermarket() -> list[dict]:
    """Raccoglie notizie M&A sport Italia da Mergermarket.

    Returns:
        Lista di dict con chiavi: title, link, source, published, summary.
    """
    if not MERGERMARKET_EMAIL or not MERGERMARKET_PASSWORD:
        logger.warning(
            "Mergermarket: credenziali non configurate - skip"
        )
        return []

    session = requests.Session()

    if not _login(session):
        logger.warning("Mergermarket: impossibile accedere, skip raccolta")
        return []

    all_articles: list[dict] = []
    for query in SEARCH_QUERIES:
        logger.info("Mergermarket query: %s", query)
        results = _search_articles(session, query)
        all_articles.extend(results)

    logger.info("Mergermarket totale: %d articoli raccolti", len(all_articles))
    return all_articles
