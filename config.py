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
    # --- Testate sportive italiane ---
    "Gazzetta dello Sport": "https://www.gazzetta.it/rss/home.xml",
    "Corriere dello Sport": "https://www.corrieredellosport.it/rss/home.xml",
    "Calcio e Finanza": "https://www.calcioefinanza.it/feed/",
    "Tuttosport": "https://www.tuttosport.com/rss/home.xml",
    # --- Testate economico-finanziarie ---
    "Il Sole 24 Ore - Sport": "https://www.ilsole24ore.com/rss/sport.xml",
    "Il Sole 24 Ore - Finanza": "https://www.ilsole24ore.com/rss/finanza.xml",
    "Milano Finanza": "https://www.milanofinanza.it/rss/",
    "ANSA Economia": "https://www.ansa.it/sito/notizie/economia/economia_rss.xml",
    "ANSA Sport": "https://www.ansa.it/sito/notizie/sport/sport_rss.xml",
    "Reuters Italy": "https://www.reuters.com/rssFeed/sportsNews",
    # --- Sport business internazionali ---
    "SportBusiness": "https://www.sportbusiness.com/feed/",
    "Sport Business Journal": "https://www.sportsbusinessjournal.com/rss/feed",
    "Football Italia": "https://football-italia.net/feed/",
    "Inside Sport Finance": "https://www.insideworldfootball.com/feed/",
    # --- Private equity & deals ---
    "Private Equity Wire": "https://www.privateequitywire.co.uk/rss.xml",
    "PE Hub": "https://www.pehub.com/feed/",
    "Pitchbook News": "https://pitchbook.com/feed",
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
    # --- Deal e acquisizioni ---
    "acquisizione club calcio Italia",
    "cessione societa sportiva Italia",
    "M&A sport Italia",
    "investitori calcio Serie A",
    "private equity sport italiano",
    # --- Rumour e trattative ---
    "rumour cessione club Serie A",
    "trattativa vendita societa calcio",
    "nuovo proprietario club calcio Italia",
    "fondo investimento calcio italiano",
    # --- Sport business allargato ---
    "football club acquisition Europe",
    "sport M&A deal Italy investor",
    "Serie A ownership change",
    "stadium naming rights Italy",
    "diritti TV Serie A trattativa",
    # --- PE e finance ---
    "private equity football Europe deal",
    "sport investment fund Italy",
    "ricapitalizzazione club sportivo Italia",
    "IPO societa sportiva",
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
    # --- Operazioni M&A ---
    "acquisizione", "cessione", "vendita", "compravendita",
    "quote societarie", "azionista", "proprieta", "takeover",
    "private equity", "investimento", "merger", "fusione",
    "closing", "due diligence", "offerta", "signing",
    "M&A", "trattativa", "negoziazione", "mandato",
    # --- Strumenti finanziari ---
    "debito", "bilancio", "ricapitalizzazione", "IPO",
    "obbligazioni", "bond", "emissione", "aumento di capitale",
    # --- Attori e strutture ---
    "fondi", "fondo", "investor", "investitore", "advisor",
    "consortium", "cordata", "holding", "veicolo societario",
    # --- Rumour e segnali ---
    "rumour", "indiscrezione", "potrebbe", "in vendita",
    "interesse per", "manifestazione di interesse", "LOI",
    "lettera di intenti", "esclusiva", "prelazione",
    # --- Asset sportivi ---
    "diritti tv", "stadio", "naming rights", "media rights",
    "broadcast", "partnership strategica", "sponsor tecnico",
    # --- Inglese (fonti internazionali) ---
    "acquisition", "disposal", "buyout", "stake",
    "ownership", "deal", "transaction", "bid",
    "football club", "sport franchise", "equity",
]
