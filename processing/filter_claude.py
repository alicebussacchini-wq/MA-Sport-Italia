"""Filtra le notizie tramite Claude API per rilevanza M&A Sport.

Due passaggi:
1. Filtro rilevanza (scarta il rumore)
2. Ranking + generazione riassunto bullet-point per le TOP notizie
"""

from __future__ import annotations

import json
import logging

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL, MAX_TOP_NEWS

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Prompt PASSAGGIO 1 — filtro severo
# ---------------------------------------------------------------------------
SYSTEM_FILTER = """\
Sei un analista senior specializzato in operazioni M&A (Mergers & Acquisitions) \
nel mondo dello sport italiano e internazionale.

Devi essere MOLTO SELETTIVO. Sono rilevanti SOLO notizie che riguardano:
- Acquisizioni / cessioni di club, societa sportive, franchigie
- Cambi di proprieta, ingresso di nuovi investitori, fondi PE/VC
- Trattative, rumour e negoziazioni societarie CONCRETE (non speculazioni vaghe)
- Ricapitalizzazioni, IPO, emissioni obbligazionarie di entita sportive
- Due diligence, closing, lettere di intenti, signing
- Accordi strategici di grandissima portata (diritti TV miliardari, naming rights)
- Ristrutturazioni aziendali di societa sportive

SCARTA senza esitazione:
- Risultati sportivi, calciomercato giocatori/allenatori, infortuni
- Tattiche, classifiche, allenamenti, conferenze stampa
- Sponsorizzazioni minori, merchandising ordinario
- Notizie generiche di business senza impatto M&A diretto
- Articoli duplicati o riformulazioni della stessa notizia
"""

USER_FILTER_TEMPLATE = """\
Analizza le seguenti notizie. Restituisci SOLO un array JSON con gli indici \
(0-based) delle notizie REALMENTE rilevanti per M&A Sport. Sii severo: \
seleziona solo quelle con valore informativo concreto per un avvocato M&A.

Rispondi SOLO con il JSON array, nessun altro testo.

Notizie:
{articles_text}
"""

# ---------------------------------------------------------------------------
# Prompt PASSAGGIO 2 — ranking + riassunto
# ---------------------------------------------------------------------------
SYSTEM_SUMMARIZE = """\
Sei un analista M&A senior. Per ogni notizia fornita, genera:
1. Un punteggio di importanza da 1 a 10 (10 = deal confermato, 1 = rumour vago)
2. Un riassunto strutturato in 2-4 bullet point dei fatti chiave (chi, cosa, \
quanto, stato dell'operazione)

Rispondi in italiano. Sii conciso e preciso.
"""

USER_SUMMARIZE_TEMPLATE = """\
Per ciascuna delle seguenti notizie, restituisci un JSON array di oggetti con:
- "index": indice 0-based della notizia
- "score": punteggio importanza 1-10
- "key_points": stringa con bullet points separati da "\\n" (usa "- " come prefisso)

Ordina per score decrescente. Rispondi SOLO con il JSON array.

Notizie:
{articles_text}
"""

FILTER_BATCH_SIZE = 25
SUMMARIZE_BATCH_SIZE = 15


def _build_articles_text(articles: list[dict]) -> str:
    lines = []
    for i, art in enumerate(articles):
        lines.append(
            f"[{i}] {art['title']}\n"
            f"    Fonte: {art['source']}\n"
            f"    {art.get('summary', '')[:300]}"
        )
    return "\n\n".join(lines)


def _call_claude_json(system: str, user: str, max_tokens: int = 2048) -> str:
    """Chiama Claude e restituisce il testo di risposta."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)
    message = client.messages.create(
        model=CLAUDE_MODEL,
        max_tokens=max_tokens,
        system=system,
        messages=[{"role": "user", "content": user}],
    )
    return message.content[0].text.strip()


def _parse_json_array(text: str) -> list:
    """Estrae un array JSON dalla risposta di Claude."""
    if text.startswith("["):
        return json.loads(text)
    start = text.index("[")
    end = text.rindex("]") + 1
    return json.loads(text[start:end])


# ---------------------------------------------------------------------------
# PASSAGGIO 1: filtro rilevanza
# ---------------------------------------------------------------------------
def _filter_pass(articles: list[dict]) -> list[dict]:
    """Filtra per rilevanza M&A — scarta il rumore."""
    relevant: list[dict] = []

    for batch_start in range(0, len(articles), FILTER_BATCH_SIZE):
        batch = articles[batch_start: batch_start + FILTER_BATCH_SIZE]
        logger.info(
            "Filtro batch %d-%d di %d",
            batch_start, batch_start + len(batch), len(articles),
        )
        try:
            text = _build_articles_text(batch)
            prompt = USER_FILTER_TEMPLATE.format(articles_text=text)
            resp = _call_claude_json(SYSTEM_FILTER, prompt, max_tokens=1024)
            indices = _parse_json_array(resp)
            for i in indices:
                if isinstance(i, int) and 0 <= i < len(batch):
                    relevant.append(batch[i])
        except Exception:
            logger.exception("Errore filtro batch %d", batch_start)
            relevant.extend(batch)  # fail-open

    logger.info("Passaggio 1 (filtro): %d/%d rilevanti", len(relevant), len(articles))
    return relevant


# ---------------------------------------------------------------------------
# PASSAGGIO 2: ranking + riassunto
# ---------------------------------------------------------------------------
def _summarize_and_rank(articles: list[dict]) -> list[dict]:
    """Genera riassunti e punteggi, poi taglia alle TOP N."""
    scored: list[tuple[int, dict, str]] = []  # (score, article, key_points)

    for batch_start in range(0, len(articles), SUMMARIZE_BATCH_SIZE):
        batch = articles[batch_start: batch_start + SUMMARIZE_BATCH_SIZE]
        logger.info(
            "Riassunto batch %d-%d di %d",
            batch_start, batch_start + len(batch), len(articles),
        )
        try:
            text = _build_articles_text(batch)
            prompt = USER_SUMMARIZE_TEMPLATE.format(articles_text=text)
            resp = _call_claude_json(SYSTEM_SUMMARIZE, prompt, max_tokens=4096)
            results = _parse_json_array(resp)

            for item in results:
                idx = item.get("index", 0)
                if 0 <= idx < len(batch):
                    score = int(item.get("score", 5))
                    kp = item.get("key_points", "")
                    scored.append((score, batch[idx], kp))
        except Exception:
            logger.exception("Errore riassunto batch %d", batch_start)
            for art in batch:
                scored.append((5, art, "- Riassunto non disponibile"))

    # Ordina per score decrescente e taglia
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:MAX_TOP_NEWS]

    enriched: list[dict] = []
    for score, art, kp in top:
        art["importance_score"] = score
        art["key_points"] = kp
        enriched.append(art)

    logger.info(
        "Passaggio 2 (ranking): top %d notizie (score max=%d, min=%d)",
        len(enriched),
        enriched[0]["importance_score"] if enriched else 0,
        enriched[-1]["importance_score"] if enriched else 0,
    )
    return enriched


# ---------------------------------------------------------------------------
# Entry point
# ---------------------------------------------------------------------------
def filter_with_claude(articles: list[dict]) -> list[dict]:
    """Pipeline completa: filtro severo -> ranking + riassunto -> top N.

    Args:
        articles: Lista di articoli da filtrare.

    Returns:
        Lista delle TOP notizie M&A con key_points e importance_score.
    """
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY non configurata - skip filtro Claude")
        return articles

    if not articles:
        return []

    # Pass 1: filtro rilevanza
    relevant = _filter_pass(articles)

    if not relevant:
        logger.warning("Nessun articolo supera il filtro rilevanza")
        return []

    # Pass 2: ranking + riassunto
    top_news = _summarize_and_rank(relevant)

    return top_news
