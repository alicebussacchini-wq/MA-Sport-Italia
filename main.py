"""Orchestratore principale – raccolta settimanale M&A Sport Italia."""

from __future__ import annotations

import logging
import sys

from scraper import collect_rss, collect_google_news, scrape_calcioefinanza
from processing import filter_with_claude, deduplicate
from storage import save_to_sheets

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)


def run_pipeline():
    """Esegue l'intera pipeline di raccolta, filtro e salvataggio."""
    logger.info("=" * 60)
    logger.info("INIZIO PIPELINE M&A Sport Italia")
    logger.info("=" * 60)

    # 1. Raccolta da tutte le fonti
    logger.info("── FASE 1: Raccolta notizie ──")
    rss_articles = collect_rss()
    google_articles = collect_google_news()
    scraped_articles = scrape_calcioefinanza()

    all_articles = rss_articles + google_articles + scraped_articles
    logger.info("Totale articoli raccolti: %d", len(all_articles))

    if not all_articles:
        logger.warning("Nessun articolo raccolto. Pipeline terminata.")
        return

    # 2. Deduplicazione
    logger.info("── FASE 2: Deduplicazione ──")
    unique_articles = deduplicate(all_articles)
    logger.info("Articoli dopo dedup: %d", len(unique_articles))

    # 3. Filtro Claude AI
    logger.info("── FASE 3: Filtro rilevanza M&A (Claude) ──")
    relevant_articles = filter_with_claude(unique_articles)
    logger.info("Articoli rilevanti M&A: %d", len(relevant_articles))

    # 4. Salvataggio su Google Sheets
    logger.info("── FASE 4: Salvataggio su Google Sheets ──")
    new_count = save_to_sheets(relevant_articles)

    # Riepilogo
    logger.info("=" * 60)
    logger.info("RIEPILOGO PIPELINE")
    logger.info("  Raccolti:   %d", len(all_articles))
    logger.info("  Dedup:      %d", len(unique_articles))
    logger.info("  Rilevanti:  %d", len(relevant_articles))
    logger.info("  Nuovi in GS: %d", new_count)
    logger.info("=" * 60)


if __name__ == "__main__":
    run_pipeline()
