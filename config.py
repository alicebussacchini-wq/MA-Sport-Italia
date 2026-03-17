import os
from dotenv import load_dotenv

load_dotenv(override=True)

# -- Claude API ---------------------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-20250514"

# Numero massimo di notizie da tenere dopo ranking (le piu importanti)
MAX_TOP_NEWS = int(os.getenv("MAX_TOP_NEWS", "20"))

# -- RSS Feeds ----------------------------------------------------------------
RSS_FEEDS = {
    "Gazzetta dello Sport": "https://www.gazzetta.it/rss/home.xml",
    "Corriere dello Sport": "https://www.corrieredellosport.it/rss/home.xml",
    "Calcio e Finanza": "https://www.calcioefinanza.it/feed/",
    "Il Sole 24 Ore - Sport": "https://www.ilsole24ore.com/rss/sport.xml",
}

# -- Scraping ------------------------------------------------------------------
CALCIO_FINANZA_BASE_URL = "https://www.calcioefinanza.it"
CALCIO_FINANZA_CATEGORIES = [
    "/",
    "/tag/serie-a/",
]

# -- Mergermarket (abbonamento) -----------------------------------------------
MERGERMARKET_EMAIL = os.getenv("MERGERMARKET_EMAIL", "")
MERGERMARKET_PASSWORD = os.getenv("MERGERMARKET_PASSWORD", "")

# -- SerpApi (Google News) ----------------------------------------------------
SERPAPI_KEY = os.getenv("SERPAPI_KEY", "")
GOOGLE_NEWS_QUERIES = [
    "acquisizione club calcio Italia",
    "cessione societa sportiva Italia",
    "M&A sport Italia",
    "investitori calcio Serie A",
    "private equity sport italiano",
]

# -- Google Sheets -------------------------------------------------------------
GOOGLE_SHEETS_CREDENTIALS_JSON = os.getenv(
    "GOOGLE_SHEETS_CREDENTIALS_JSON", "credentials/service_account.json"
)
GOOGLE_SHEETS_SPREADSHEET_NAME = os.getenv(
    "GOOGLE_SHEETS_SPREADSHEET_NAME", "MA_Sport_Italia"
)

# -- Streamlit Auth ------------------------------------------------------------
WHITELIST_EMAILS = [
    e.strip()
    for e in os.getenv("WHITELIST_EMAILS", "").split(",")
    if e.strip()
]
DASHBOARD_PASSWORD = os.getenv("DASHBOARD_PASSWORD", "MilanM&A_Sport2026!")

# -- M&A Keywords (pre-filter before Claude) -----------------------------------
MA_KEYWORDS = [
    "acquisizione", "cessione", "vendita", "compravendita",
    "quote societarie", "azionista", "proprieta", "takeover",
    "private equity", "investimento", "merger", "fusione",
    "partnership", "sponsor", "diritti tv", "stadio",
    "debito", "bilancio", "ricapitalizzazione", "IPO",
    "fondi", "closing", "due diligence", "offerta",
    "M&A", "rumour", "trattativa", "negoziazione",
]
