import os
from dotenv import load_dotenv

load_dotenv(override=True)

# -- Claude API ---------------------------------------------------------------
ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
CLAUDE_MODEL = "claude-sonnet-4-6"

# Numero massimo di notizie da tenere dopo ranking (le piu importanti)
MAX_TOP_NEWS = int(os.getenv("MAX_TOP_NEWS", "15"))

# -- RSS Feeds ----------------------------------------------------------------
RSS_FEEDS = {
    # --- Testate sportive italiane ---
    "Gazzetta dello Sport": "https://www.gazzetta.it/rss/home.xml",
    "Corriere dello Sport": "https://www.corrieredellosport.it/rss/home.xml",
    "Calcio e Finanza": "https://www.calcioefinanza.it/feed/",
    "Tuttosport": "https://www.tuttosport.com/rss/home.xml",
    "Football Italia": "https://football-italia.net/feed/",
    # --- Testate economico-finanziarie italiane ---
    "Il Sole 24 Ore - Sport": "https://www.ilsole24ore.com/rss/sport.xml",
    "Il Sole 24 Ore - Finanza": "https://www.ilsole24ore.com/rss/finanza.xml",
    "Milano Finanza": "https://www.milanofinanza.it/rss/",
    "ANSA Economia": "https://www.ansa.it/sito/notizie/economia/economia_rss.xml",
    "ANSA Sport": "https://www.ansa.it/sito/notizie/sport/sport_rss.xml",
    "La Repubblica Economia": "https://www.repubblica.it/rss/economia/rss2.0.xml",
    "Corriere Economia": "https://xml2.corriereobjects.it/rss/economia.xml",
    # --- Sport business internazionali ---
    "SportBusiness": "https://www.sportbusiness.com/feed/",
    "Sport Business Journal": "https://www.sportsbusinessjournal.com/rss/feed",
    "SportsPro Media": "https://www.sportspromedia.com/feed/",
    "Sportico": "https://www.sportico.com/feed/",
    "Front Office Sports": "https://frontofficesports.com/feed/",
    "Inside Sport Finance": "https://www.insideworldfootball.com/feed/",
    "Reuters Sports": "https://www.reuters.com/rssFeed/sportsNews",
    # --- Private equity & deals ---
    "Private Equity Wire": "https://www.privateequitywire.co.uk/rss.xml",
    "PE Hub": "https://www.pehub.com/feed/",
    "Pitchbook News": "https://pitchbook.com/feed",
    "BeBeez": "https://bebeez.it/feed/",
    # --- Wire service (comunicati stampa deal) ---
    "GlobeNewswire Sport": "https://www.globenewswire.com/RssFeed/subjectcode/14-Sport/feedTitle/GlobeNewswire%20-%20Sport",
    "PR Newswire Sport": "https://www.prnewswire.com/rss/sports-news/sport-news.rss",
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
    # --- Deal e acquisizioni (IT) ---
    "acquisizione cessione club calcio Italia",
    "M&A sport Italia investitore fondo",
    "private equity calcio Serie A Italia",
    # --- Rumour e trattative (IT) ---
    "rumour cessione vendita societa sportiva Italia",
    "trattativa nuovo proprietario club calcio Serie A",
    # --- Sport business (EN) ---
    "football club acquisition investment Italy Serie A",
    "sport M&A deal Europe investor private equity",
    # --- Finance e IPO ---
    "ricapitalizzazione IPO societa sportiva Italia",
    "diritti TV Serie A trattativa cessione",
    # --- Advisor e due diligence ---
    "advisor mandato due diligence sport calcio Italia",
    # --- Non-calcio ---
    "basket pallavolo rugby acquisizione cessione Italia",
    # --- Infrastrutture ---
    "stadio infrastrutture sportive concessione Italia",
    # --- Fondi specifici (alto valore) ---
    "fondo sovrano calcio Europa investimento",
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
    # --- Sport non-calcio ---
    "basket", "pallavolo", "rugby", "ciclismo", "motorsport",
    "Formula 1", "MotoGP", "pallacanestro", "tennis",
    # --- Infrastrutture ---
    "project finance stadio", "concessione impianto sportivo",
    "PPP sport", "ristrutturazione stadio",
    # --- Inglese (fonti internazionali) ---
    "acquisition", "disposal", "buyout", "stake",
    "ownership", "deal", "transaction", "bid",
    "football club", "sport franchise", "equity",
    "sovereign wealth fund", "minority stake",
    "Serie A investment", "club valuation",
]
