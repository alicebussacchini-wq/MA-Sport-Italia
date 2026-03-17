"""Gestione archivio storico su Google Sheets tramite gspread."""

from __future__ import annotations

import logging
from datetime import datetime, timezone

import gspread
from google.oauth2.service_account import Credentials

from config import GOOGLE_SHEETS_CREDENTIALS_JSON, GOOGLE_SHEETS_SPREADSHEET_NAME

logger = logging.getLogger(__name__)

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

HEADER_ROW = [
    "data_raccolta",
    "title",
    "source",
    "published",
    "link",
    "summary",
    "title_hash",
]


def _get_client() -> gspread.Client:
    creds = Credentials.from_service_account_file(
        GOOGLE_SHEETS_CREDENTIALS_JSON, scopes=SCOPES
    )
    return gspread.authorize(creds)


def _get_or_create_sheet(client: gspread.Client) -> gspread.Worksheet:
    """Apre o crea lo spreadsheet e il foglio 'Archivio'."""
    try:
        spreadsheet = client.open(GOOGLE_SHEETS_SPREADSHEET_NAME)
    except gspread.SpreadsheetNotFound:
        spreadsheet = client.create(GOOGLE_SHEETS_SPREADSHEET_NAME)
        logger.info("Creato nuovo spreadsheet: %s", GOOGLE_SHEETS_SPREADSHEET_NAME)

    try:
        worksheet = spreadsheet.worksheet("Archivio")
    except gspread.WorksheetNotFound:
        worksheet = spreadsheet.add_worksheet(
            title="Archivio", rows=1000, cols=len(HEADER_ROW)
        )
        worksheet.append_row(HEADER_ROW)
        logger.info("Creato foglio 'Archivio' con header")

    return worksheet


def _get_existing_hashes(worksheet: gspread.Worksheet) -> set[str]:
    """Recupera gli hash già presenti per evitare duplicati cross-settimana."""
    try:
        hash_col_idx = HEADER_ROW.index("title_hash") + 1
        values = worksheet.col_values(hash_col_idx)
        return set(values[1:])  # salta header
    except Exception:
        return set()


def save_to_sheets(articles: list[dict]) -> int:
    """Salva gli articoli su Google Sheets, evitando duplicati.

    Args:
        articles: Lista di articoli filtrati e deduplicati.

    Returns:
        Numero di nuovi articoli aggiunti.
    """
    if not articles:
        logger.info("Nessun articolo da salvare su Sheets")
        return 0

    try:
        client = _get_client()
        worksheet = _get_or_create_sheet(client)
    except Exception:
        logger.exception("Errore connessione Google Sheets")
        return 0

    existing_hashes = _get_existing_hashes(worksheet)
    now = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M")

    rows_to_add = []
    for art in articles:
        art_hash = art.get("title_hash", "")
        if art_hash in existing_hashes:
            continue
        rows_to_add.append(
            [
                now,
                art.get("title", ""),
                art.get("source", ""),
                art.get("published", ""),
                art.get("link", ""),
                art.get("summary", "")[:500],
                art_hash,
            ]
        )

    if rows_to_add:
        worksheet.append_rows(rows_to_add)
        logger.info("Salvati %d nuovi articoli su Sheets", len(rows_to_add))
    else:
        logger.info("Nessun nuovo articolo da aggiungere (tutti già presenti)")

    return len(rows_to_add)


def load_from_sheets() -> list[dict]:
    """Carica tutti gli articoli dall'archivio Google Sheets.

    Returns:
        Lista di dict con le colonne dell'archivio.
    """
    try:
        client = _get_client()
        worksheet = _get_or_create_sheet(client)
        records = worksheet.get_all_records()
        logger.info("Caricati %d record da Sheets", len(records))
        return records
    except Exception:
        logger.exception("Errore lettura Google Sheets")
        return []
