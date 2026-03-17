"""Dashboard Streamlit - M&A Sport Italia Newsletter."""

from __future__ import annotations

import streamlit as st
import pandas as pd

from config import WHITELIST_EMAILS, DASHBOARD_PASSWORD

# -- Page config ---------------------------------------------------------------
st.set_page_config(
    page_title="M&A Sport Italia",
    page_icon="https://em-content.zobj.net/source/twitter/408/soccer-ball_26bd.png",
    layout="wide",
    initial_sidebar_state="collapsed",
)

# -- Custom CSS ----------------------------------------------------------------
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background: linear-gradient(135deg, #0a0e27 0%, #1a1f3a 50%, #0d1117 100%);
    }

    /* Hide default streamlit elements */
    #MainMenu {visibility: hidden;}
    header {visibility: hidden;}
    footer {visibility: hidden;}

    /* Sidebar */
    section[data-testid="stSidebar"] {
        background: #111827;
        border-right: 1px solid #1e3a5f;
    }
    section[data-testid="stSidebar"] .stMarkdown p,
    section[data-testid="stSidebar"] .stMarkdown label,
    section[data-testid="stSidebar"] .stMarkdown span {
        color: #94a3b8 !important;
    }

    /* Typography */
    h1, h2, h3 { color: #f1f5f9 !important; }

    /* Hero header */
    .hero-header {
        background: linear-gradient(135deg, #1e3a5f 0%, #2d1b69 100%);
        border: 1px solid #334155;
        border-radius: 16px;
        padding: 2rem 2.5rem;
        margin-bottom: 1.5rem;
    }
    .hero-header h1 {
        font-size: 2rem !important;
        font-weight: 700 !important;
        margin: 0 !important;
        letter-spacing: -0.5px;
    }
    .hero-header .subtitle {
        color: #94a3b8;
        font-size: 1rem;
        margin-top: 0.3rem;
    }

    /* KPI cards */
    .kpi-row {
        display: flex;
        gap: 1rem;
        margin-bottom: 1.5rem;
    }
    .kpi-card {
        background: linear-gradient(135deg, #111827, #1e293b);
        border: 1px solid #334155;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        flex: 1;
        text-align: center;
    }
    .kpi-value {
        font-size: 2.2rem;
        font-weight: 700;
        color: #60a5fa;
        line-height: 1;
    }
    .kpi-label {
        font-size: 0.8rem;
        color: #64748b;
        text-transform: uppercase;
        letter-spacing: 1px;
        margin-top: 0.4rem;
    }
    .kpi-card.gold .kpi-value { color: #fbbf24; }
    .kpi-card.green .kpi-value { color: #34d399; }
    .kpi-card.purple .kpi-value { color: #a78bfa; }

    /* News card */
    .news-card {
        background: #111827;
        border: 1px solid #1e3a5f;
        border-radius: 12px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        transition: border-color 0.2s;
    }
    .news-card:hover {
        border-color: #3b82f6;
    }
    .news-card .card-header {
        display: flex;
        justify-content: space-between;
        align-items: flex-start;
        margin-bottom: 0.8rem;
    }
    .news-card .card-title {
        font-size: 1.1rem;
        font-weight: 600;
        color: #f1f5f9;
        margin: 0;
        line-height: 1.4;
    }
    .news-card .card-title a {
        color: #60a5fa !important;
        text-decoration: none !important;
    }
    .news-card .card-title a:hover {
        color: #93c5fd !important;
        text-decoration: underline !important;
    }
    .news-card .card-meta {
        display: flex;
        gap: 1rem;
        margin-bottom: 0.8rem;
        flex-wrap: wrap;
    }
    .news-card .meta-tag {
        font-size: 0.75rem;
        padding: 0.2rem 0.6rem;
        border-radius: 6px;
        font-weight: 500;
    }
    .source-tag {
        background: #1e3a5f;
        color: #93c5fd;
    }
    .date-tag {
        background: #1a2332;
        color: #64748b;
    }
    .news-card .key-points {
        background: #0d1117;
        border-left: 3px solid #3b82f6;
        border-radius: 0 8px 8px 0;
        padding: 0.8rem 1rem;
        margin-top: 0.5rem;
        color: #cbd5e1;
        font-size: 0.9rem;
        line-height: 1.6;
    }

    /* Score badge */
    .score-badge {
        display: inline-flex;
        align-items: center;
        justify-content: center;
        min-width: 36px;
        height: 36px;
        border-radius: 10px;
        font-weight: 700;
        font-size: 0.95rem;
        flex-shrink: 0;
    }
    .score-high { background: #065f46; color: #34d399; }
    .score-mid  { background: #713f12; color: #fbbf24; }
    .score-low  { background: #7f1d1d; color: #fca5a5; }

    /* Section header */
    .section-header {
        color: #f1f5f9;
        font-size: 1.3rem;
        font-weight: 600;
        margin: 1.5rem 0 1rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid #1e3a5f;
    }

    /* Login page */
    .login-box {
        max-width: 420px;
        margin: 8vh auto;
        background: #111827;
        border: 1px solid #1e3a5f;
        border-radius: 16px;
        padding: 2.5rem;
    }
    .login-box h2 {
        text-align: center;
        margin-bottom: 0.3rem;
    }
    .login-subtitle {
        text-align: center;
        color: #64748b;
        margin-bottom: 1.5rem;
        font-size: 0.9rem;
    }

    /* Search box */
    .stTextInput input {
        background: #1e293b !important;
        border: 1px solid #334155 !important;
        color: #f1f5f9 !important;
        border-radius: 10px !important;
    }

    /* Buttons */
    .stButton > button {
        background: linear-gradient(135deg, #2563eb, #4f46e5) !important;
        color: white !important;
        border: none !important;
        border-radius: 10px !important;
        padding: 0.5rem 1.5rem !important;
        font-weight: 600 !important;
    }
    .stButton > button:hover {
        background: linear-gradient(135deg, #3b82f6, #6366f1) !important;
    }

    /* Download button */
    .stDownloadButton > button {
        background: #111827 !important;
        border: 1px solid #334155 !important;
        color: #94a3b8 !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        gap: 0;
        background: #111827;
        border-radius: 10px;
        padding: 4px;
    }
    .stTabs [data-baseweb="tab"] {
        border-radius: 8px;
        color: #94a3b8;
        padding: 0.5rem 1.2rem;
    }
    .stTabs [aria-selected="true"] {
        background: #1e3a5f !important;
        color: #f1f5f9 !important;
    }

    /* Expander */
    .streamlit-expanderHeader {
        background: #111827 !important;
        color: #94a3b8 !important;
    }
</style>
""", unsafe_allow_html=True)


# -- Auth ----------------------------------------------------------------------
def _check_auth() -> bool:
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.markdown("""
    <div class="login-box">
        <h2>M&A Sport Italia</h2>
        <p class="login-subtitle">Intelligence platform per operazioni M&A nel mondo dello sport</p>
    </div>
    """, unsafe_allow_html=True)

    col_left, col_center, col_right = st.columns([1, 1, 1])
    with col_center:
        tab_email, tab_pwd = st.tabs(["Email", "Password"])

        with tab_email:
            email = st.text_input("Email aziendale", key="auth_email",
                                  placeholder="nome@studio.com")
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


# -- Data loading --------------------------------------------------------------
@st.cache_data(ttl=300)
def _load_data() -> pd.DataFrame:
    try:
        from storage.gsheets import load_from_sheets
        records = load_from_sheets()
        if not records:
            return pd.DataFrame()
        df = pd.DataFrame(records)
        if "data_raccolta" in df.columns:
            df["data_raccolta"] = pd.to_datetime(df["data_raccolta"], errors="coerce")
        if "published" in df.columns:
            df["published"] = pd.to_datetime(df["published"], errors="coerce")
        if "importance_score" in df.columns:
            df["importance_score"] = pd.to_numeric(
                df["importance_score"], errors="coerce"
            ).fillna(5).astype(int)
        return df
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return pd.DataFrame()


# -- Rendering helpers ---------------------------------------------------------
def _score_badge(score: int) -> str:
    if score >= 8:
        cls = "score-high"
    elif score >= 5:
        cls = "score-mid"
    else:
        cls = "score-low"
    return f'<span class="score-badge {cls}">{score}</span>'


def _render_news_card(row: pd.Series):
    title = str(row.get("title", "Senza titolo")).replace("<", "&lt;").replace(">", "&gt;")
    link = str(row.get("link", ""))
    source = str(row.get("source", "N/A"))
    published = row.get("published", "")
    score = int(row.get("importance_score", 5))
    key_points = str(row.get("key_points", ""))

    # Format published date
    pub_str = ""
    if pd.notna(published) and str(published).strip():
        try:
            pub_str = pd.to_datetime(published).strftime("%d %b %Y")
        except Exception:
            pub_str = str(published)[:10]

    # Score color
    if score >= 8:
        score_bg, score_fg = "#065f46", "#34d399"
    elif score >= 5:
        score_bg, score_fg = "#713f12", "#fbbf24"
    else:
        score_bg, score_fg = "#7f1d1d", "#fca5a5"

    # Title with link
    if link and link != "nan" and link.startswith("http"):
        title_html = f'<a href="{link}" target="_blank" style="color:#60a5fa;text-decoration:none;">{title}</a>'
    else:
        title_html = title

    # Date tag
    date_html = (
        f'<span style="font-size:0.75rem;padding:0.2rem 0.6rem;border-radius:6px;'
        f'background:#1a2332;color:#64748b;">{pub_str}</span>'
        if pub_str else ""
    )

    # Key points
    kp_html = ""
    if key_points and key_points.strip() and key_points != "nan":
        kp_lines = key_points.replace("\\n", "\n").split("\n")
        kp_clean = [line.strip() for line in kp_lines if line.strip()]
        kp_text = "<br>".join(kp_clean)
        kp_html = (
            f'<div style="background:#0d1117;border-left:3px solid #3b82f6;'
            f'border-radius:0 8px 8px 0;padding:0.8rem 1rem;margin-top:0.5rem;'
            f'color:#cbd5e1;font-size:0.9rem;line-height:1.6;">{kp_text}</div>'
        )

    # Single markdown call with all inline styles
    st.markdown(
        f'<div style="background:#111827;border:1px solid #1e3a5f;border-radius:12px;'
        f'padding:1.5rem;margin-bottom:1rem;">'
        f'<div style="display:flex;justify-content:space-between;align-items:flex-start;margin-bottom:0.8rem;">'
        f'<p style="font-size:1.1rem;font-weight:600;color:#f1f5f9;margin:0;line-height:1.4;flex:1;margin-right:1rem;">{title_html}</p>'
        f'<span style="display:inline-flex;align-items:center;justify-content:center;min-width:36px;height:36px;'
        f'border-radius:10px;font-weight:700;font-size:0.95rem;flex-shrink:0;'
        f'background:{score_bg};color:{score_fg};">{score}</span>'
        f'</div>'
        f'<div style="display:flex;gap:1rem;margin-bottom:0.5rem;flex-wrap:wrap;">'
        f'<span style="font-size:0.75rem;padding:0.2rem 0.6rem;border-radius:6px;'
        f'font-weight:500;background:#1e3a5f;color:#93c5fd;">{source}</span>'
        f'{date_html}'
        f'</div>'
        f'{kp_html}'
        f'</div>',
        unsafe_allow_html=True,
    )


# -- Main dashboard ------------------------------------------------------------
def _render_dashboard():
    # Sidebar
    with st.sidebar:
        st.markdown("### Impostazioni")
        if st.button("Ricarica dati", use_container_width=True):
            st.cache_data.clear()
            st.rerun()
        st.divider()
        if st.button("Logout", use_container_width=True):
            st.session_state.authenticated = False
            st.rerun()

    # Load data
    df = _load_data()

    # Hero header
    user = st.session_state.get("user_email", "")
    user_display = user.split("@")[0].replace(".", " ").title() if "@" in user else user
    st.markdown(f"""
    <div class="hero-header">
        <h1>M&A Sport Italia</h1>
        <p class="subtitle">Intelligence settimanale su operazioni M&A nel mondo dello sport italiano
        {"&nbsp;&middot;&nbsp;" + user_display if user_display and user_display != "Password User" else ""}</p>
    </div>
    """, unsafe_allow_html=True)

    if df.empty:
        st.warning("Nessun dato disponibile. Esegui `python main.py` per la prima raccolta.")
        return

    # -- Sidebar filters -------------------------------------------------------
    with st.sidebar:
        st.markdown("### Filtri")

        sources = sorted(df["source"].dropna().unique()) if "source" in df.columns else []
        selected_sources = st.multiselect("Fonti", sources, default=sources)

        if "importance_score" in df.columns:
            min_score = st.slider("Score minimo", 1, 10, 6)
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

    # Apply filters
    mask = pd.Series(True, index=df.index)
    if selected_sources and "source" in df.columns:
        mask &= df["source"].isin(selected_sources)
    if "importance_score" in df.columns:
        mask &= df["importance_score"] >= min_score
    if date_range and len(date_range) == 2 and "data_raccolta" in df.columns:
        mask &= (df["data_raccolta"].dt.date >= date_range[0]) & (
            df["data_raccolta"].dt.date <= date_range[1]
        )

    filtered = df[mask].copy()
    if "importance_score" in filtered.columns:
        filtered = filtered.sort_values("importance_score", ascending=False)

    # -- KPI cards -------------------------------------------------------------
    n_total = len(filtered)
    n_sources = filtered["source"].nunique() if "source" in filtered.columns else 0
    avg_score = (
        filtered["importance_score"].mean()
        if "importance_score" in filtered.columns and n_total > 0
        else 0
    )
    n_high = (
        len(filtered[filtered["importance_score"] >= 8])
        if "importance_score" in filtered.columns
        else 0
    )

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card">
            <div class="kpi-value">{n_total}</div>
            <div class="kpi-label">Notizie totali</div>
        </div>
        <div class="kpi-card gold">
            <div class="kpi-value">{n_high}</div>
            <div class="kpi-label">Alta rilevanza</div>
        </div>
        <div class="kpi-card green">
            <div class="kpi-value">{avg_score:.1f}</div>
            <div class="kpi-label">Score medio</div>
        </div>
        <div class="kpi-card purple">
            <div class="kpi-value">{n_sources}</div>
            <div class="kpi-label">Fonti</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # -- Tabs ------------------------------------------------------------------
    tab_news, tab_archive = st.tabs(["Notizie della settimana", "Archivio completo"])

    with tab_news:
        # Search
        search = st.text_input(
            "Cerca", placeholder="Cerca per titolo, fonte...",
            label_visibility="collapsed",
        )
        if search and "title" in filtered.columns:
            search_mask = (
                filtered["title"].str.contains(search, case=False, na=False)
                | filtered["source"].str.contains(search, case=False, na=False)
            )
            filtered_search = filtered[search_mask]
        else:
            filtered_search = filtered

        # Last week only
        if "data_raccolta" in filtered_search.columns:
            latest_date = filtered_search["data_raccolta"].max()
            if pd.notna(latest_date):
                week_ago = latest_date - pd.Timedelta(days=7)
                weekly = filtered_search[
                    filtered_search["data_raccolta"] >= week_ago
                ]
            else:
                weekly = filtered_search
        else:
            weekly = filtered_search

        if weekly.empty:
            st.info("Nessuna notizia corrisponde ai filtri selezionati.")
        else:
            st.markdown(
                f'<div class="section-header">'
                f'{len(weekly)} notizie questa settimana</div>',
                unsafe_allow_html=True,
            )
            for _, row in weekly.iterrows():
                _render_news_card(row)

    with tab_archive:
        search_archive = st.text_input(
            "Cerca nell'archivio",
            placeholder="Cerca per titolo, fonte...",
            key="search_archive",
        )
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
                f'<div class="section-header">'
                f'{len(archive)} notizie in archivio</div>',
                unsafe_allow_html=True,
            )
            for _, row in archive.iterrows():
                _render_news_card(row)

    # -- Export ----------------------------------------------------------------
    st.divider()
    col_dl1, col_dl2, _ = st.columns([1, 1, 3])
    with col_dl1:
        csv = filtered.to_csv(index=False).encode("utf-8")
        st.download_button(
            "Scarica CSV", csv, "ma_sport_italia.csv", "text/csv",
            use_container_width=True,
        )


# -- Main ----------------------------------------------------------------------
if _check_auth():
    _render_dashboard()
