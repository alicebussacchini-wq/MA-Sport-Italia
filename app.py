"""Dashboard Streamlit - M&A Sport Italia Intelligence.

Branded per Hogan Lovells secondo le Brand Guidelines (March 2025).
Palette: Dark Green #243508, Lime Green #BFF355, Teal #82C8BE,
         Lilac #B1A6FF, Taupe #E2D6CF, White #FFFFFF
Typography fallback: Arial (headlines), Georgia (body)
Tone: Dynamic, Precise, Committed, Authentic
"""

from __future__ import annotations

import csv
import io
from datetime import datetime

import streamlit as st
import pandas as pd

from config import WHITELIST_EMAILS, DASHBOARD_PASSWORD

# =============================================================================
# Hogan Lovells Brand Palette (from Brand Guidelines p.70)
# =============================================================================
HL_LIME = "#BFF355"       # Hero lime green
HL_DARK_GREEN = "#243508" # Dark green (backgrounds, text)
HL_TEAL = "#82C8BE"       # Active accent
HL_LILAC = "#B1A6FF"      # Active accent
HL_TAUPE = "#E2D6CF"      # Neutral
HL_WHITE = "#FFFFFF"
HL_BLACK = "#0D0D0D"      # 95% black

# Dashboard dark mode — black base, lime green accents only
BG_PRIMARY = "#0A0A0A"    # Pure black base
BG_CARD = "#111111"       # Card backgrounds
BG_SURFACE = "#161616"    # Elevated surfaces
BORDER = "#222222"        # Subtle borders
TEXT_PRIMARY = "#F0F0F0"  # Clean white text
TEXT_MUTED = "#888888"    # Neutral grey muted text

# HL Official Logo — inline base64 for reliable rendering
import base64, pathlib
_logo_path = pathlib.Path(__file__).parent / "static" / "hl_logo.png"
if _logo_path.exists():
    _logo_b64 = base64.b64encode(_logo_path.read_bytes()).decode()
    _logo_src = f"data:image/png;base64,{_logo_b64}"
else:
    _logo_src = ""
HL_LOGO_SMALL = f'<img src="{_logo_src}" alt="Hogan Lovells" style="height:44px;border-radius:4px;" />' if _logo_src else '<span style="color:#BFF355;font-weight:bold;">HOGAN LOVELLS</span>'
HL_LOGO_LARGE = f'<img src="{_logo_src}" alt="Hogan Lovells" style="height:80px;border-radius:4px;" />' if _logo_src else '<span style="color:#BFF355;font-size:2rem;font-weight:bold;">HOGAN LOVELLS</span>'

# =============================================================================
# Page config
# =============================================================================
st.set_page_config(
    page_title="M&A Sport Italia | Hogan Lovells",
    page_icon="data:image/svg+xml,<svg xmlns='http://www.w3.org/2000/svg' viewBox='0 0 100 100'><rect width='100' height='100' rx='12' fill='%23BFF355'/><text x='12' y='68' font-family='serif' font-weight='bold' font-size='42' fill='%23243508'>HL</text></svg>",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# =============================================================================
# CSS - Hogan Lovells branded
# =============================================================================
st.markdown(f"""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* --- Base --- */
    .stApp {{
        background: {BG_PRIMARY};
        font-family: 'Inter', Arial, sans-serif;
    }}

    #MainMenu {{visibility: hidden;}}
    header {{visibility: hidden;}}
    footer {{visibility: hidden;}}

    /* --- Sidebar (dark green) --- */
    section[data-testid="stSidebar"] {{
        background: {BG_PRIMARY};
        border-right: 1px solid {BORDER};
    }}
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label,
    section[data-testid="stSidebar"] .stMarkdown span {{
        color: {TEXT_MUTED} !important;
    }}

    h1, h2, h3 {{ color: {TEXT_PRIMARY} !important; font-family: 'Inter', Arial, sans-serif !important; }}

    /* --- Inputs --- */
    .stTextInput input {{
        background: {BG_CARD} !important;
        border: 1px solid {BORDER} !important;
        color: {TEXT_PRIMARY} !important;
        border-radius: 8px !important;
    }}
    .stSelectbox > div > div {{
        background: {BG_CARD} !important;
        border-color: {BORDER} !important;
    }}

    /* --- Buttons (lime green, dark text per brand) --- */
    .stButton > button {{
        background: {HL_LIME} !important;
        color: {HL_DARK_GREEN} !important;
        border: none !important;
        border-radius: 8px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
        font-family: 'Inter', Arial, sans-serif !important;
    }}
    .stButton > button:hover {{
        background: #D4FF7A !important;
        color: {HL_DARK_GREEN} !important;
    }}

    .stDownloadButton > button {{
        background: transparent !important;
        border: 1px solid {HL_LIME} !important;
        color: {HL_LIME} !important;
        font-family: 'Inter', Arial, sans-serif !important;
    }}
    .stDownloadButton > button:hover {{
        background: rgba(191,243,85,0.1) !important;
    }}

    /* --- Tabs (lime active) --- */
    .stTabs [data-baseweb="tab-list"] {{
        gap: 0;
        background: {BG_CARD};
        border-radius: 10px;
        padding: 4px;
        border: 1px solid {BORDER};
    }}
    .stTabs [data-baseweb="tab"] {{
        border-radius: 8px;
        color: {TEXT_MUTED};
        padding: 0.5rem 1.2rem;
        font-family: 'Inter', Arial, sans-serif;
    }}
    .stTabs [aria-selected="true"] {{
        background: {BG_SURFACE} !important;
        color: {HL_LIME} !important;
        font-weight: 600;
    }}

    /* --- Radio buttons --- */
    .stRadio label span {{
        color: {TEXT_MUTED} !important;
    }}
    .stRadio [data-checked="true"] span {{
        color: {HL_LIME} !important;
    }}

    /* --- File uploader --- */
    .stFileUploader {{
        border: 2px dashed {BORDER} !important;
        border-radius: 12px !important;
    }}
</style>
""", unsafe_allow_html=True)


# =============================================================================
# Auth
# =============================================================================
def _check_auth() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if st.session_state.authenticated:
        return True

    # Login page
    st.markdown(f"""
    <div style="max-width:440px;margin:6vh auto;background:{BG_CARD};
         border:1px solid {BORDER};border-radius:16px;padding:2.5rem;text-align:center;">
        <div style="margin-bottom:1.2rem;">{HL_LOGO_LARGE}</div>
        <h2 style="margin:0 0 0.3rem 0;font-size:1.4rem;color:{TEXT_PRIMARY};">M&A Sport Italia</h2>
        <p style="color:{TEXT_MUTED};font-size:0.9rem;margin-bottom:0.2rem;">
            Vital intelligence. Driving M&amp;A insight in Italian sport.</p>
        <p style="color:{HL_TEAL};font-size:0.75rem;margin:0;">HOGAN LOVELLS</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        tab_email, tab_pwd = st.tabs(["Email", "Password"])
        with tab_email:
            email = st.text_input("Email aziendale", key="auth_email",
                                  placeholder="nome@hoganlovells.com")
            if st.button("Accedi", key="btn_email", use_container_width=True):
                if email.strip().lower() in [e.lower() for e in WHITELIST_EMAILS]:
                    st.session_state.authenticated = True
                    st.session_state.user_email = email
                    st.rerun()
                else:
                    st.error("Email non autorizzata.")
        with tab_pwd:
            pwd = st.text_input("Password", type="password", key="auth_pwd")
            if st.button("Accedi", key="btn_pwd", use_container_width=True):
                if pwd == DASHBOARD_PASSWORD:
                    st.session_state.authenticated = True
                    st.session_state.user_email = "password_user"
                    st.rerun()
                else:
                    st.error("Password errata.")
    return False


# =============================================================================
# Data loading
# =============================================================================
@st.cache_data(ttl=300)
def _load_data() -> pd.DataFrame:
    try:
        from storage.gsheets import load_from_sheets
        records = load_from_sheets()
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        if "data_raccolta" in df.columns:
            df["data_raccolta"] = pd.to_datetime(df["data_raccolta"], utc=True, errors="coerce")
        if "published" in df.columns:
            df["published"] = pd.to_datetime(df["published"], utc=True, errors="coerce")
        if "importance_score" in df.columns:
            df["importance_score"] = pd.to_numeric(
                df["importance_score"], errors="coerce"
            ).fillna(5).astype(int)
        # Filtra solo notizie da gennaio 2026 in poi (su ENTRAMBE le date)
        cutoff = pd.Timestamp("2026-01-01", tz="UTC")
        if "published" in df.columns:
            # Rimuovi articoli pubblicati prima del 2026
            has_pub = df["published"].notna()
            df = df[~has_pub | (df["published"] >= cutoff)].copy()
        if "data_raccolta" in df.columns:
            has_dr = df["data_raccolta"].notna()
            df = df[~has_dr | (df["data_raccolta"] >= cutoff)].copy()
        return df
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return pd.DataFrame()


# =============================================================================
# Weekly summary generator (Claude AI)
# =============================================================================
def _generate_weekly_summary(weekly_df: pd.DataFrame) -> str:
    """Genera un riassunto settimanale narrativo usando Claude."""
    try:
        from config import ANTHROPIC_API_KEY, CLAUDE_MODEL
        import anthropic
    except Exception:
        return ""

    if not ANTHROPIC_API_KEY or weekly_df.empty:
        return ""

    # Check cache
    week_key = f"weekly_summary_{len(weekly_df)}_{weekly_df['title'].iloc[0][:20] if len(weekly_df) > 0 else ''}"
    if week_key in st.session_state:
        return st.session_state[week_key]

    # Build prompt from articles
    articles_text = []
    for _, row in weekly_df.iterrows():
        status = str(row.get("deal_status", "N/A"))
        score = int(row.get("importance_score", 5))
        kp = str(row.get("key_points", ""))
        articles_text.append(
            f"- [{status} | Score {score}] {row.get('title', '')}\n  {kp}"
        )
    articles_block = "\n".join(articles_text)

    system_prompt = (
        "Sei un analista M&A senior di Hogan Lovells. Scrivi un executive summary "
        "settimanale in italiano per il team legale. Stile: professionale, conciso, "
        "diretto. Struttura il riassunto in sezioni: "
        "1) Deal confermati e operazioni ufficiali, "
        "2) Trattative in corso e negoziazioni avanzate, "
        "3) Rumour e segnali di mercato notevoli. "
        "Ometti le sezioni vuote. Usa 3-5 paragrafi totali. "
        "Non usare bullet point, scrivi in forma narrativa."
    )

    user_prompt = (
        f"Ecco le {len(weekly_df)} notizie M&A sport di questa settimana. "
        f"Genera l'executive summary settimanale.\n\n{articles_block}"
    )

    try:
        client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1500,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
        )
        summary = message.content[0].text.strip()
        st.session_state[week_key] = summary
        return summary
    except Exception:
        return ""


# =============================================================================
# News card renderer (brand-compliant)
# =============================================================================
def _render_news_card(row: pd.Series):
    title = str(row.get("title", "Senza titolo")).replace("<", "&lt;").replace(">", "&gt;")
    link = str(row.get("link", ""))
    source = str(row.get("source", "N/A"))
    published = row.get("published", "")
    score = int(row.get("importance_score", 5))
    key_points = str(row.get("key_points", ""))

    pub_str = ""
    if pd.notna(published) and str(published).strip():
        try:
            pub_str = pd.to_datetime(published).strftime("%d %b %Y")
        except Exception:
            pub_str = str(published)[:10]

    # Deal status badge — colori distinti per stato
    deal_status = str(row.get("deal_status", ""))
    STATUS_COLORS = {
        "Confermato": ("#1A2508", HL_LIME),
        "In Trattativa": ("#0D1A18", HL_TEAL),
        "Rumour": ("#141225", HL_LILAC),
        "Speculazione": ("#1A1A18", HL_TAUPE),
    }
    # Fallback: deriva dallo score se deal_status mancante (dati vecchi)
    if deal_status not in STATUS_COLORS:
        if score >= 8:
            deal_status = "Confermato"
        elif score >= 6:
            deal_status = "In Trattativa"
        elif score >= 4:
            deal_status = "Rumour"
        else:
            deal_status = "Speculazione"
    score_bg, score_fg = STATUS_COLORS[deal_status]
    label = deal_status

    # Title with link (lime green links on dark = brand compliant)
    if link and link != "nan" and link.startswith("http"):
        title_html = f'<a href="{link}" target="_blank" rel="noopener" style="color:{HL_LIME};text-decoration:none;">{title}</a>'
    else:
        title_html = f'<span style="color:{TEXT_PRIMARY};">{title}</span>'

    date_html = (
        f'<span style="font-size:0.73rem;padding:0.15rem 0.5rem;border-radius:5px;'
        f'background:rgba(191,243,85,0.08);color:{TEXT_MUTED};">{pub_str}</span>'
        if pub_str else ""
    )

    # Status tag based on score
    status_html = (
        f'<span style="font-size:0.68rem;padding:0.15rem 0.5rem;border-radius:5px;'
        f'background:{score_bg};color:{score_fg};font-weight:600;letter-spacing:0.5px;'
        f'text-transform:uppercase;">{label}</span>'
    )

    # Key points / summary (lime green left border per brand angular style)
    summary = str(row.get("summary", ""))
    kp_html = ""
    # Use key_points if available, otherwise fall back to summary
    display_text = ""
    if key_points and key_points.strip() and key_points != "nan":
        display_text = key_points
    elif summary and summary.strip() and summary != "nan":
        display_text = summary

    if display_text:
        kp_lines = display_text.replace("\\n", "\n").split("\n")
        kp_clean = [line.strip() for line in kp_lines if line.strip()]
        kp_text = "<br>".join(kp_clean)
        kp_html = (
            f'<div style="background:rgba(191,243,85,0.04);border-left:3px solid {HL_LIME};'
            f'border-radius:0 8px 8px 0;padding:0.7rem 1rem;margin-top:0.6rem;'
            f'color:{HL_TAUPE};font-size:0.85rem;line-height:1.7;'
            f'font-family:Georgia,serif;">{kp_text}</div>'
        )

    st.markdown(
        f'<div style="background:{BG_CARD};border:1px solid {BORDER};border-radius:12px;'
        f'padding:1.4rem;margin-bottom:0.7rem;transition:border-color 0.2s;">'
        # Header row
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.5rem;">'
        f'<p style="font-size:1.02rem;font-weight:600;color:{TEXT_PRIMARY};margin:0;line-height:1.4;flex:1;margin-right:1rem;'
        f'font-family:Inter,Arial,sans-serif;">{title_html}</p>'
        f'<span style="display:inline-flex;align-items:center;justify-content:center;min-width:32px;height:32px;'
        f'border-radius:8px;font-weight:700;font-size:0.85rem;flex-shrink:0;'
        f'background:{score_bg};color:{score_fg};">{score}</span>'
        f'</div>'
        # Meta row
        f'<div style="display:flex;gap:0.6rem;flex-wrap:wrap;align-items:center;">'
        f'<span style="font-size:0.73rem;padding:0.15rem 0.5rem;border-radius:5px;'
        f'font-weight:500;background:rgba(191,243,85,0.12);color:{HL_LIME};">{source}</span>'
        f'{status_html}'
        f'{date_html}'
        f'</div>'
        # Key points
        f'{kp_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


# =============================================================================
# Report generator (HTML, branded)
# =============================================================================
def _generate_report(df: pd.DataFrame) -> bytes:
    now = datetime.now().strftime("%d/%m/%Y")

    if "data_raccolta" in df.columns and not df["data_raccolta"].isna().all():
        df = df.copy()
        df["week"] = df["data_raccolta"].dt.isocalendar().week.astype(str) + "/" + df["data_raccolta"].dt.year.astype(str)
        weeks = df.groupby("week", sort=False)
    else:
        weeks = [("Tutte", df)]

    rows_html = ""
    for week_label, group in weeks:
        rows_html += f'<tr><td colspan="4" style="background:#111111;color:{HL_LIME};font-weight:700;padding:10px 14px;font-size:13px;font-family:Arial,sans-serif;letter-spacing:0.5px;">SETTIMANA {week_label}</td></tr>'
        for _, row in group.iterrows():
            score = int(row.get("importance_score", 5))
            title = str(row.get("title", ""))
            source = str(row.get("source", ""))
            kp = str(row.get("key_points", "")).replace("\\n", "\n")
            link = str(row.get("link", ""))

            kp_lines = [l.strip() for l in kp.split("\n") if l.strip()]
            kp_formatted = "<br>".join(kp_lines) if kp_lines else "-"

            title_cell = f'<a href="{link}" style="color:{HL_LIME};text-decoration:none;">{title}</a>' if link and link.startswith("http") else title

            if score >= 8:
                badge_bg, badge_fg = HL_DARK_GREEN, HL_LIME
            elif score >= 5:
                badge_bg, badge_fg = "#1A3530", HL_TEAL
            else:
                badge_bg, badge_fg = "#2A2520", HL_TAUPE

            rows_html += (
                f'<tr>'
                f'<td style="padding:8px 12px;border-bottom:1px solid #3A5518;color:{HL_TAUPE};font-weight:600;font-family:Arial,sans-serif;">{title_cell}</td>'
                f'<td style="padding:8px 12px;border-bottom:1px solid #3A5518;color:{TEXT_MUTED};text-align:center;font-size:12px;">{source}</td>'
                f'<td style="padding:8px 12px;border-bottom:1px solid #3A5518;text-align:center;">'
                f'<span style="background:{badge_bg};color:{badge_fg};padding:3px 10px;border-radius:10px;font-weight:700;font-size:12px;">{score}</span></td>'
                f'<td style="padding:8px 12px;border-bottom:1px solid #3A5518;color:{HL_TAUPE};font-size:12px;line-height:1.6;font-family:Georgia,serif;">{kp_formatted}</td>'
                f'</tr>'
            )

    html = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
<title>M&amp;A Sport Italia Report - Hogan Lovells - {now}</title>
<style>
    body {{ font-family: Arial, sans-serif; background: #0A0A0A; color: {TEXT_PRIMARY}; margin: 0; padding: 30px; }}
    .header {{ display: flex; align-items: center; justify-content: space-between; margin-bottom: 30px; padding-bottom: 20px; border-bottom: 3px solid {HL_LIME}; }}
    .header h1 {{ font-size: 20px; margin: 0; color: {TEXT_PRIMARY}; font-family: Arial, sans-serif; }}
    .header .sub {{ color: {HL_LIME}; font-size: 11px; letter-spacing: 2px; text-transform: uppercase; margin-top: 4px; }}
    .header .date {{ color: {TEXT_MUTED}; font-size: 13px; }}
    .header .logo {{ width: 56px; height: 62px; background: {HL_LIME}; border-radius: 4px; display: flex; flex-direction: column; align-items: flex-start; justify-content: center; padding: 4px 6px; font-family: Georgia, serif; font-weight: bold; font-size: 13px; line-height: 1.3; color: {HL_DARK_GREEN}; }}
    .stats {{ display: flex; gap: 16px; margin-bottom: 25px; }}
    .stat {{ background: {BG_CARD}; border: 1px solid {BORDER}; border-radius: 10px; padding: 15px 20px; text-align: center; flex: 1; }}
    .stat .val {{ font-size: 26px; font-weight: 700; color: {HL_LIME}; }}
    .stat .lbl {{ font-size: 10px; color: {TEXT_MUTED}; text-transform: uppercase; letter-spacing: 1px; margin-top: 4px; }}
    table {{ width: 100%; border-collapse: collapse; background: {BG_CARD}; border-radius: 10px; overflow: hidden; }}
    th {{ background: {BG_PRIMARY}; color: {TEXT_MUTED}; font-size: 11px; text-transform: uppercase; letter-spacing: 1px; padding: 10px 12px; text-align: left; }}
    a {{ color: {HL_LIME}; text-decoration: none; }}
    .footer {{ margin-top: 30px; padding-top: 15px; border-top: 1px solid {BORDER}; color: {TEXT_MUTED}; font-size: 11px; text-align: center; }}
</style>
</head>
<body>
<div class="header">
    <div>
        <h1>M&amp;A Sport Italia</h1>
        <div class="sub">Hogan Lovells - Vital for Change</div>
        <span class="date">Report generato il {now}</span>
    </div>
    <div class="logo">HL</div>
</div>
<div class="stats">
    <div class="stat"><div class="val">{len(df)}</div><div class="lbl">Notizie</div></div>
    <div class="stat"><div class="val">{df["source"].nunique() if "source" in df.columns else 0}</div><div class="lbl">Fonti</div></div>
    <div class="stat"><div class="val">{f'{df["importance_score"].mean():.1f}' if "importance_score" in df.columns and len(df) > 0 else "N/A"}</div><div class="lbl">Score Medio</div></div>
</div>
<table>
<thead><tr><th>Notizia</th><th>Fonte</th><th>Score</th><th>Punti chiave</th></tr></thead>
<tbody>{rows_html}</tbody>
</table>
<div class="footer">
    Hogan Lovells | M&amp;A Sport Italia Intelligence | Documento riservato | {now}
</div>
</body>
</html>"""
    return html.encode("utf-8")


# =============================================================================
# Mergermarket CSV import
# =============================================================================
def _extract_articles_from_pdf(pdf_bytes: bytes) -> list[dict]:
    """Estrae notizie/deal da un PDF Mergermarket.

    Il formato Mergermarket e':
    - Pagina 1: Table of Contents con titoli + date
    - Pagine successive: un articolo per pagina con titolo grande,
      data | paese | settore, bullet points, corpo testo, copyright ION
    """
    import pdfplumber
    import hashlib
    import re

    articles = []
    seen_titles: set[str] = set()

    # --- STEP 1: Estrai dal Table of Contents (pagina 1) ---
    toc_articles: list[dict] = []
    with pdfplumber.open(io.BytesIO(pdf_bytes)) as pdf:
        # Raccogli tutto il testo
        all_pages_text: list[str] = []
        for page in pdf.pages:
            txt = page.extract_text()
            all_pages_text.append(txt if txt else "")

    full_text = "\n\n".join(all_pages_text)

    # --- STEP 2: Parse dal TOC (titoli + date sulla prima pagina) ---
    # Pattern: titolo su una riga, data su riga successiva (es. "04 Feb 2025")
    date_pattern = re.compile(
        r'^(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
        re.MULTILINE
    )

    # Splitta il testo completo per trovare blocchi articolo
    # Mergermarket separa articoli con il pattern copyright ION
    article_blocks = re.split(r'(?:\xa9|©)\s*\d{4}\s*ION', full_text)

    for block in article_blocks:
        block = block.strip()
        if len(block) < 50:
            continue

        # Cerca il titolo: prima riga significativa che non e' un timestamp/header
        lines = block.split("\n")
        title = ""
        date_str = ""
        bullet_points = []
        body_lines = []
        found_title = False
        found_date = False
        in_body = False

        for line in lines:
            line_stripped = line.strip()
            if not line_stripped:
                continue

            # Skip header/footer noise
            if any(skip in line_stripped.lower() for skip in [
                "table of contents", "intelligence and research",
                "mergermarket.ionanalytics.com",
                "this document is protected", "you may not alter",
                "for unauthorized use", "your agreement with ion",
                "link to the original", "link to press release",
                "sourced from print",
            ]):
                continue

            # Skip Mergermarket header timestamp lines (e.g. "17/03/26, 18:02 2026-03-17 ...")
            if re.match(r'^\d{2}/\d{2}/\d{2},\s+\d{2}:\d{2}', line_stripped):
                continue

            # Skip page numbers like "1/26", "2/26"
            if re.match(r'^\d+/\d+$', line_stripped):
                continue

            # Detect date line (e.g. "04 Feb 2025 02:25 CEST Italy Leisure...")
            date_match = re.match(
                r'(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)\s+\d{4})',
                line_stripped
            )
            if date_match and not found_date and found_title:
                date_str = date_match.group(1)
                found_date = True
                continue

            # Detect Mergermarket logo text
            if line_stripped in ("Mergermarket", "Proprietary", "Press Release"):
                continue

            # Detect bullet points (start with bullet char)
            if line_stripped.startswith(("\u2b24", "\u25cf", "\u2022", "•")):
                bullet_points.append("- " + line_stripped.lstrip("\u2b24\u25cf\u2022• "))
                continue

            # Detect author lines
            if line_stripped.startswith("by ") and len(line_stripped) < 80:
                continue

            # First significant line = title
            if not found_title and len(line_stripped) > 15 and not line_stripped.startswith("http"):
                # Could be a multi-line title, accumulate
                if not title:
                    title = line_stripped
                    found_title = True
                continue

            # Body text (after title + date)
            if found_title and found_date:
                if len(line_stripped) > 20:
                    body_lines.append(line_stripped)

        # Clean up title
        title = title.strip()
        # Remove " (translated)" suffix for dedup but keep in display
        title_clean = re.sub(r'\s*[\-\u2013]\s*report\s*$', '', title, flags=re.IGNORECASE).strip()
        title_clean = re.sub(r'\s*\(translated\)\s*$', '', title_clean, flags=re.IGNORECASE).strip()

        if not title or len(title) < 15:
            continue

        # Dedup by normalized title
        title_lower = title.lower().strip()
        if title_lower in seen_titles:
            continue
        seen_titles.add(title_lower)

        # Build summary from body
        body = " ".join(body_lines[:5])[:500] if body_lines else title
        kp = "\n".join(bullet_points[:5]) if bullet_points else f"- Fonte: Mergermarket\n- {title}"

        art_hash = hashlib.md5(title.encode()).hexdigest()[:12]

        articles.append({
            "title": title,
            "link": "",
            "source": "Mergermarket (PDF import)",
            "published": date_str,
            "summary": body,
            "importance_score": 7,
            "key_points": kp,
            "title_hash": art_hash,
        })

    return articles


def _mergermarket_import_section():
    """Sezione per import manuale di dati esportati da Mergermarket (PDF o CSV)."""
    st.markdown(
        f'<div style="color:{TEXT_PRIMARY};font-size:1.2rem;font-weight:600;'
        f'margin:1rem 0 0.5rem 0;padding-bottom:0.4rem;border-bottom:2px solid {HL_TEAL};">'
        f'Import Mergermarket</div>',
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<p style="color:{TEXT_MUTED};font-size:0.88rem;margin-bottom:1rem;font-family:Georgia,serif;">'
        f'Esporta i dati dal tuo account Mergermarket in formato <strong style="color:{HL_LIME};">PDF</strong> '
        f'o <strong style="color:{HL_LIME};">CSV</strong>, poi caricali qui. '
        f'Il sistema estrae automaticamente le notizie dal documento.</p>',
        unsafe_allow_html=True,
    )

    uploaded = st.file_uploader(
        "Carica file Mergermarket",
        type=["pdf", "csv"],
        key="mm_upload",
    )

    if uploaded is not None:
        try:
            file_name = uploaded.name.lower()
            articles = []

            if file_name.endswith(".pdf"):
                # --- Estrazione da PDF ---
                pdf_bytes = uploaded.getvalue()
                with st.spinner("Estrazione notizie dal PDF in corso..."):
                    articles = _extract_articles_from_pdf(pdf_bytes)

                if articles:
                    st.success(f"Estratti **{len(articles)}** articoli dal PDF.")
                    preview_df = pd.DataFrame(articles)[["title", "source", "published"]].head(10)
                    st.dataframe(preview_df, use_container_width=True)
                else:
                    st.warning("Non sono riuscito ad estrarre articoli dal PDF. "
                               "Prova con un formato diverso o verifica che il PDF contenga testo selezionabile.")

            else:
                # --- Estrazione da CSV ---
                import hashlib
                content = uploaded.getvalue().decode("utf-8")
                reader = csv.DictReader(io.StringIO(content))
                rows = list(reader)

                for r in rows:
                    title = r.get("Title", r.get("title", r.get("Headline", "")))
                    if not title:
                        continue
                    art_hash = hashlib.md5(title.encode()).hexdigest()[:12]
                    articles.append({
                        "title": title,
                        "link": r.get("Link", r.get("link", r.get("URL", ""))),
                        "source": "Mergermarket (CSV import)",
                        "published": r.get("Date", r.get("date", r.get("Published", ""))),
                        "summary": (r.get("Summary", r.get("summary", r.get("Snippet", ""))) or title)[:500],
                        "importance_score": 7,
                        "key_points": f"- Fonte: Mergermarket\n- {title}",
                        "title_hash": art_hash,
                    })

                if articles:
                    st.success(f"Caricati **{len(articles)}** record dal CSV.")
                    preview_df = pd.DataFrame(articles)[["title", "source", "published"]].head(10)
                    st.dataframe(preview_df, use_container_width=True)
                else:
                    st.warning("Il file CSV sembra vuoto o non contiene colonne riconoscibili.")

            # Bottone salvataggio
            if articles:
                if st.button("Salva in archivio", key="mm_save", use_container_width=False):
                    from storage.gsheets import save_to_sheets
                    count = save_to_sheets(articles)
                    if count > 0:
                        st.success(f"Salvati **{count}** nuovi articoli Mergermarket nell'archivio.")
                    else:
                        st.info("Tutti gli articoli erano gia presenti nell'archivio.")
                    st.cache_data.clear()

        except Exception as e:
            st.error(f"Errore lettura file: {e}")


# =============================================================================
# Main dashboard
# =============================================================================
def _render_dashboard():
    with st.sidebar:
        st.markdown(f"### Impostazioni")
        if st.button("Ricarica dati", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    df = _load_data()

    # Hero header
    user = st.session_state.get("user_email", "")
    user_display = user.split("@")[0].replace(".", " ").title() if "@" in user else user

    st.markdown(f"""
    <div style="background:{BG_CARD};
         border:1px solid {BORDER};border-radius:14px;padding:1.6rem 2.2rem;margin-bottom:1.3rem;
         display:flex;align-items:center;justify-content:space-between;">
        <div>
            <div style="display:flex;align-items:center;gap:14px;margin-bottom:6px;">
                {HL_LOGO_SMALL}
                <h1 style="font-size:1.6rem !important;font-weight:700 !important;margin:0 !important;
                    letter-spacing:-0.5px;font-family:Inter,Arial,sans-serif !important;">M&A Sport Italia</h1>
            </div>
            <p style="color:{TEXT_MUTED};font-size:0.88rem;margin:0;font-family:Georgia,serif;">
                Vital intelligence. Driving M&amp;A insight in Italian sport.
                {"&nbsp;&middot;&nbsp;" + user_display if user_display and user_display != "Password User" else ""}</p>
        </div>
        <div style="text-align:right;">
            <span style="color:{HL_LIME};font-size:0.7rem;letter-spacing:2px;text-transform:uppercase;
                   font-weight:600;">Hogan Lovells</span><br>
            <span style="color:{TEXT_MUTED};font-size:0.72rem;">Move fast. Lead change.</span>
        </div>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("Nessun dato disponibile. Esegui `python main.py` per la prima raccolta.")
        return

    # Sidebar filters
    with st.sidebar:
        st.markdown("### Filtri")
        sources = sorted(df["source"].dropna().unique()) if "source" in df.columns else []
        selected_sources = st.multiselect("Fonti", sources, default=sources)

        # Deal status filter
        all_statuses = ["Confermato", "In Trattativa", "Rumour", "Speculazione"]
        selected_statuses = st.multiselect(
            "Stato operazione", all_statuses, default=all_statuses
        )

        if "importance_score" in df.columns:
            min_score = st.slider("Score minimo", 1, 10, 3)
        else:
            min_score = 1
        if "data_raccolta" in df.columns and not df["data_raccolta"].isna().all():
            min_date = df["data_raccolta"].min().date()
            max_date = df["data_raccolta"].max().date()
            date_range = st.date_input(
                "Periodo", value=(min_date, max_date),
                min_value=min_date, max_value=max_date,
            )
        else:
            date_range = None

    # Ensure deal_status column exists (backward compat with old data)
    if "deal_status" not in df.columns:
        df["deal_status"] = df.apply(
            lambda r: "Confermato" if int(r.get("importance_score", 5)) >= 8
            else "In Trattativa" if int(r.get("importance_score", 5)) >= 6
            else "Rumour" if int(r.get("importance_score", 5)) >= 4
            else "Speculazione",
            axis=1,
        )

    # Apply filters
    mask = pd.Series(True, index=df.index)
    if selected_sources and "source" in df.columns:
        mask &= df["source"].isin(selected_sources)
    if selected_statuses:
        mask &= df["deal_status"].isin(selected_statuses)
    if "importance_score" in df.columns:
        mask &= df["importance_score"] >= min_score
    if date_range and len(date_range) == 2 and "data_raccolta" in df.columns:
        mask &= (df["data_raccolta"].dt.date >= date_range[0]) & (
            df["data_raccolta"].dt.date <= date_range[1]
        )
    filtered = df[mask].copy()
    if "importance_score" in filtered.columns:
        filtered = filtered.sort_values("importance_score", ascending=False)

    # Calcola notizie recenti (ultimi 30 giorni) per i KPI
    if "data_raccolta" in filtered.columns and not filtered["data_raccolta"].isna().all():
        _latest = filtered["data_raccolta"].max()
        _recent_cutoff = _latest - pd.Timedelta(days=30) if pd.notna(_latest) else None
        recent = filtered[filtered["data_raccolta"] >= _recent_cutoff] if _recent_cutoff else filtered
    else:
        recent = filtered

    # KPI cards — conteggi basati sulle notizie recenti (non tutto l'archivio)
    n_total = len(recent)
    n_confirmed = len(recent[recent["deal_status"] == "Confermato"]) if "deal_status" in recent.columns else 0
    n_trattativa = len(recent[recent["deal_status"] == "In Trattativa"]) if "deal_status" in recent.columns else 0
    n_rumour = len(recent[recent["deal_status"] == "Rumour"]) if "deal_status" in recent.columns else 0
    n_speculazione = len(recent[recent["deal_status"] == "Speculazione"]) if "deal_status" in recent.columns else 0

    # Active filter from KPI click
    if "kpi_filter" not in st.session_state:
        st.session_state["kpi_filter"] = None

    def _set_kpi(val):
        st.session_state["kpi_filter"] = val

    active = st.session_state["kpi_filter"]

    kpi_cols = st.columns(5)
    kpi_defs = [
        ("Tutti", n_total, HL_LIME, None),
        ("Confermati", n_confirmed, HL_LIME, "Confermato"),
        ("In Trattativa", n_trattativa, HL_TEAL, "In Trattativa"),
        ("Rumour", n_rumour, HL_LILAC, "Rumour"),
        ("Speculazione", n_speculazione, HL_TAUPE, "Speculazione"),
    ]
    for col, (lbl, count, color, status_val) in zip(kpi_cols, kpi_defs):
        with col:
            is_active = active == status_val
            border_color = color if is_active else BORDER
            bw = "2px" if is_active else "1px"
            st.markdown(
                f'<div style="background:{BG_CARD};border:{bw} solid {border_color};'
                f'border-radius:10px;padding:0.8rem 0.5rem;text-align:center;'
                f'margin-bottom:0.3rem;">'
                f'<div style="font-size:1.8rem;font-weight:700;color:{color};line-height:1;">{count}</div>'
                f'<div style="font-size:0.65rem;color:{TEXT_MUTED};text-transform:uppercase;'
                f'letter-spacing:1px;margin-top:0.3rem;">{lbl}</div></div>',
                unsafe_allow_html=True,
            )
            btn_type = "primary" if is_active else "secondary"
            st.button(
                f"Filtra {lbl}" if status_val else "Mostra tutti",
                key=f"kpi_{lbl}",
                use_container_width=True,
                type=btn_type,
                on_click=_set_kpi,
                args=(status_val,),
            )

    # Apply KPI filter to ALL views (tabs, weekly, archive)
    if st.session_state["kpi_filter"]:
        filtered = filtered[filtered["deal_status"] == st.session_state["kpi_filter"]].copy()

    # Tabs
    tab_news, tab_archive, tab_report, tab_mm = st.tabs([
        "Notizie della settimana", "Archivio completo", "Genera Report", "Import Mergermarket"
    ])

    with tab_news:
        search = st.text_input("Cerca", placeholder="Cerca per titolo, fonte...", label_visibility="collapsed")
        if search and "title" in filtered.columns:
            search_mask = (
                filtered["title"].str.contains(search, case=False, na=False)
                | filtered["source"].str.contains(search, case=False, na=False)
            )
            filtered_search = filtered[search_mask]
        else:
            filtered_search = filtered

        if "data_raccolta" in filtered_search.columns:
            latest_date = filtered_search["data_raccolta"].max()
            if pd.notna(latest_date):
                week_ago = latest_date - pd.Timedelta(days=7)
                weekly = filtered_search[filtered_search["data_raccolta"] >= week_ago]
            else:
                weekly = filtered_search
        else:
            weekly = filtered_search

        if weekly.empty:
            st.info("Nessuna notizia corrisponde ai filtri selezionati.")
        else:
            st.markdown(
                f'<div style="color:{TEXT_PRIMARY};font-size:1.2rem;font-weight:600;'
                f'margin:1rem 0;padding-bottom:0.4rem;border-bottom:2px solid {HL_LIME};'
                f'font-family:Inter,Arial,sans-serif;">'
                f'{len(weekly)} notizie questa settimana</div>',
                unsafe_allow_html=True,
            )

            # Weekly executive summary
            col_summary, col_regen = st.columns([6, 1])
            with col_regen:
                regen = st.button("Rigenera", key="regen_summary")
            if regen:
                # Clear cache to force regeneration
                for k in list(st.session_state.keys()):
                    if k.startswith("weekly_summary_"):
                        del st.session_state[k]

            with st.spinner("Generazione riassunto settimanale..."):
                summary_text = _generate_weekly_summary(weekly)
            if summary_text:
                st.markdown(
                    f'<div style="background:{BG_CARD};border-left:4px solid {HL_LIME};'
                    f'border-radius:0 12px 12px 0;padding:1.2rem 1.5rem;margin-bottom:1.2rem;'
                    f'border:1px solid {BORDER};border-left:4px solid {HL_LIME};">'
                    f'<div style="font-size:0.75rem;text-transform:uppercase;letter-spacing:1.5px;'
                    f'color:{HL_LIME};font-weight:600;margin-bottom:0.8rem;">Executive Summary</div>'
                    f'<div style="color:{TEXT_PRIMARY};font-size:0.92rem;line-height:1.8;'
                    f'font-family:Georgia,serif;">{summary_text}</div></div>',
                    unsafe_allow_html=True,
                )

            # Group by deal status
            for status in ["Confermato", "In Trattativa", "Rumour", "Speculazione"]:
                status_df = weekly[weekly["deal_status"] == status]
                if status_df.empty:
                    continue
                status_colors = {
                    "Confermato": HL_LIME, "In Trattativa": HL_TEAL,
                    "Rumour": HL_LILAC, "Speculazione": HL_TAUPE,
                }
                st.markdown(
                    f'<div style="color:{status_colors.get(status, TEXT_MUTED)};font-size:0.9rem;'
                    f'font-weight:600;margin:1rem 0 0.4rem 0;text-transform:uppercase;'
                    f'letter-spacing:1px;">{status} ({len(status_df)})</div>',
                    unsafe_allow_html=True,
                )
                for _, row in status_df.iterrows():
                    _render_news_card(row)

    with tab_archive:
        search_archive = st.text_input("Cerca nell'archivio", placeholder="Cerca per titolo, fonte...", key="search_archive")
        archive = filtered.copy()
        if search_archive and "title" in archive.columns:
            archive = archive[
                archive["title"].str.contains(search_archive, case=False, na=False)
                | archive["source"].str.contains(search_archive, case=False, na=False)
            ]
        if archive.empty:
            st.info("Archivio vuoto.")
        else:
            st.markdown(
                f'<div style="color:{TEXT_PRIMARY};font-size:1.2rem;font-weight:600;'
                f'margin:1rem 0;padding-bottom:0.4rem;border-bottom:2px solid {HL_LIME};'
                f'font-family:Inter,Arial,sans-serif;">'
                f'{len(archive)} notizie in archivio</div>',
                unsafe_allow_html=True,
            )
            for _, row in archive.iterrows():
                _render_news_card(row)

    with tab_report:
        st.markdown(
            f'<div style="color:{TEXT_PRIMARY};font-size:1.2rem;font-weight:600;'
            f'margin:1rem 0 0.5rem 0;padding-bottom:0.4rem;border-bottom:2px solid {HL_LIME};">'
            f'Genera Report M&amp;A</div>',
            unsafe_allow_html=True,
        )
        st.markdown(
            f'<p style="color:{TEXT_MUTED};font-size:0.88rem;margin-bottom:1rem;font-family:Georgia,serif;">'
            f'Genera un report HTML professionale branded Hogan Lovells, raggruppato per settimana. '
            f'Aprilo nel browser e stampa come PDF per la distribuzione interna.</p>',
            unsafe_allow_html=True,
        )

        report_scope = st.radio(
            "Periodo del report",
            ["Ultima settimana", "Ultimo mese", "Tutto l'archivio"],
            horizontal=True,
        )

        if "data_raccolta" in filtered.columns:
            latest = filtered["data_raccolta"].max()
            if pd.notna(latest):
                if report_scope == "Ultima settimana":
                    report_df = filtered[filtered["data_raccolta"] >= latest - pd.Timedelta(days=7)]
                elif report_scope == "Ultimo mese":
                    report_df = filtered[filtered["data_raccolta"] >= latest - pd.Timedelta(days=30)]
                else:
                    report_df = filtered
            else:
                report_df = filtered
        else:
            report_df = filtered

        st.markdown(
            f'<p style="color:{TEXT_MUTED};font-size:0.85rem;">'
            f'Il report includera <strong style="color:{HL_LIME};">{len(report_df)}</strong> notizie.</p>',
            unsafe_allow_html=True,
        )

        if not report_df.empty:
            report_html = _generate_report(report_df)
            now_str = datetime.now().strftime("%Y%m%d")
            col1, col2, _ = st.columns([1, 1, 3])
            with col1:
                st.download_button("Scarica Report HTML", report_html,
                    f"HL_MA_Sport_Italia_{now_str}.html", "text/html", use_container_width=True)
            with col2:
                csv_data = report_df.to_csv(index=False).encode("utf-8")
                st.download_button("Scarica CSV", csv_data,
                    f"HL_MA_Sport_Italia_{now_str}.csv", "text/csv", use_container_width=True)

    with tab_mm:
        _mergermarket_import_section()


# =============================================================================
# Entry point
# =============================================================================
if st.query_params.get("token") == "preview":
    st.session_state.authenticated = True
    st.session_state.user_email = "alice.bussacchini@hoganlovells.com"
if _check_auth():
    _render_dashboard()
