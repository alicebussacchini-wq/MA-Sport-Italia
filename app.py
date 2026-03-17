"""Dashboard Streamlit – M&A Sport Italia Newsletter."""

from __future__ import annotations

import streamlit as st
import pandas as pd
import plotly.express as px

from config import WHITELIST_EMAILS, DASHBOARD_PASSWORD

# ── Page config ─────────────────────────────────────────────
st.set_page_config(
    page_title="M&A Sport Italia",
    page_icon="⚽",
    layout="wide",
)


# ── Auth ────────────────────────────────────────────────────
def _check_auth() -> bool:
    """Verifica accesso tramite email whitelist o password."""
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False

    if st.session_state.authenticated:
        return True

    st.title("🔒 M&A Sport Italia – Accesso")
    st.markdown("Inserisci le tue credenziali per accedere alla dashboard.")

    tab_email, tab_pwd = st.tabs(["Email", "Password"])

    with tab_email:
        email = st.text_input("Email", key="auth_email")
        if st.button("Accedi con email", key="btn_email"):
            if email.strip().lower() in [e.lower() for e in WHITELIST_EMAILS]:
                st.session_state.authenticated = True
                st.session_state.user_email = email
                st.rerun()
            else:
                st.error("Email non autorizzata.")

    with tab_pwd:
        pwd = st.text_input("Password", type="password", key="auth_pwd")
        if st.button("Accedi con password", key="btn_pwd"):
            if pwd == DASHBOARD_PASSWORD:
                st.session_state.authenticated = True
                st.session_state.user_email = "password_user"
                st.rerun()
            else:
                st.error("Password errata.")

    return False


def _load_data() -> pd.DataFrame:
    """Carica dati da Google Sheets (con cache)."""
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
        return df
    except Exception as e:
        st.error(f"Errore caricamento dati: {e}")
        return pd.DataFrame()


def _render_dashboard():
    """Render principale della dashboard."""
    st.title("📊 M&A Sport Italia – Dashboard")
    st.caption(f"Utente: {st.session_state.get('user_email', 'N/A')}")

    if st.button("🔄 Ricarica dati"):
        st.cache_data.clear()

    if st.sidebar.button("🚪 Logout"):
        st.session_state.authenticated = False
        st.rerun()

    df = _load_data()

    if df.empty:
        st.warning("Nessun dato disponibile. Eseguire prima la raccolta dati.")
        st.info("Esegui `python main.py` per avviare la prima raccolta.")
        return

    # ── Sidebar filtri ──────────────────────────────────────
    st.sidebar.header("Filtri")

    sources = sorted(df["source"].dropna().unique()) if "source" in df.columns else []
    selected_sources = st.sidebar.multiselect(
        "Fonti", sources, default=sources
    )

    if "data_raccolta" in df.columns and not df["data_raccolta"].isna().all():
        min_date = df["data_raccolta"].min().date()
        max_date = df["data_raccolta"].max().date()
        date_range = st.sidebar.date_input(
            "Periodo",
            value=(min_date, max_date),
            min_value=min_date,
            max_value=max_date,
        )
    else:
        date_range = None

    # Applica filtri
    mask = pd.Series(True, index=df.index)
    if selected_sources and "source" in df.columns:
        mask &= df["source"].isin(selected_sources)
    if date_range and len(date_range) == 2 and "data_raccolta" in df.columns:
        mask &= (df["data_raccolta"].dt.date >= date_range[0]) & (
            df["data_raccolta"].dt.date <= date_range[1]
        )

    filtered = df[mask]

    # ── KPI ─────────────────────────────────────────────────
    col1, col2, col3 = st.columns(3)
    col1.metric("Notizie totali", len(filtered))
    col2.metric("Fonti", filtered["source"].nunique() if "source" in filtered.columns else 0)

    if "data_raccolta" in filtered.columns and not filtered["data_raccolta"].isna().all():
        weeks = filtered["data_raccolta"].dt.isocalendar().week.nunique()
        col3.metric("Settimane coperte", weeks)
    else:
        col3.metric("Settimane coperte", "N/A")

    # ── Grafico notizie per settimana ───────────────────────
    st.subheader("📈 Notizie per settimana")
    if "data_raccolta" in filtered.columns and not filtered["data_raccolta"].isna().all():
        weekly = (
            filtered.set_index("data_raccolta")
            .resample("W")
            .size()
            .reset_index(name="count")
        )
        fig = px.bar(
            weekly,
            x="data_raccolta",
            y="count",
            labels={"data_raccolta": "Settimana", "count": "N. notizie"},
        )
        st.plotly_chart(fig, use_container_width=True)

    # ── Grafico per fonte ───────────────────────────────────
    st.subheader("📰 Distribuzione per fonte")
    if "source" in filtered.columns:
        source_counts = filtered["source"].value_counts().reset_index()
        source_counts.columns = ["source", "count"]
        fig2 = px.pie(source_counts, names="source", values="count")
        st.plotly_chart(fig2, use_container_width=True)

    # ── Tabella notizie ─────────────────────────────────────
    st.subheader("📋 Archivio notizie")

    search_term = st.text_input("🔍 Cerca nel titolo")
    if search_term and "title" in filtered.columns:
        filtered = filtered[
            filtered["title"].str.contains(search_term, case=False, na=False)
        ]

    display_cols = [c for c in ["data_raccolta", "title", "source", "published", "link"] if c in filtered.columns]
    st.dataframe(
        filtered[display_cols].sort_values(
            "data_raccolta", ascending=False
        )
        if "data_raccolta" in display_cols
        else filtered[display_cols],
        use_container_width=True,
        column_config={
            "link": st.column_config.LinkColumn("Link"),
        },
        height=500,
    )

    # ── Export CSV ──────────────────────────────────────────
    csv = filtered.to_csv(index=False).encode("utf-8")
    st.download_button(
        "⬇️ Scarica CSV",
        csv,
        "ma_sport_italia.csv",
        "text/csv",
    )


# ── Main ────────────────────────────────────────────────────
if _check_auth():
    _render_dashboard()
