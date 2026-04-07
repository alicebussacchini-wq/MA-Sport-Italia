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
nel mondo dello sport, al servizio del team M&A di Hogan Lovells. \
Il tuo obiettivo e' selezionare SOLO notizie che genererebbero un'opportunita' \
di lavoro concreta per un team legale M&A specializzato in sport.

TIENI — notizie con valore diretto per un avvocato M&A sport:

1. OPERAZIONI SOCIETARIE CONCRETE:
   - Acquisizioni, cessioni, fusioni di club o societa sportive
   - Cambi di proprieta completati o in fase avanzata
   - Ingresso di fondi PE/VC, sovereign wealth fund in entita sportive
   - Closing, signing, lettere di intenti, accordi vincolanti

2. TRANSAZIONI FINANZIARIE RILEVANTI:
   - IPO, ricapitalizzazioni, emissioni obbligazionarie di entita sportive
   - Due diligence in corso, mandati conferiti ad advisor
   - Finanziamenti strutturati per acquisizioni sportive
   - Cessioni di quote societarie, operazioni su minoranze

3. SEGNALI PRE-DEAL AD ALTA CREDIBILITA':
   - Processi di vendita formalmente avviati con advisor nominato
   - Manifestazioni di interesse ufficiali da parte di investitori identificati
   - Crisi finanziarie gravi che rendono imminente una cessione
   - Fondi che raccolgono capitale specificamente per sport

SCARTA SENZA ESITAZIONE:
- Risultati sportivi, calciomercato giocatori/allenatori, infortuni, tattiche
- Classifiche, allenamenti, conferenze stampa tecniche, nomine di allenatori
- Sponsorizzazioni, merchandising, accordi commerciali minori
- Diritti TV e media rights (salvo che implichino cambio di proprieta/governance)
- Naming rights di stadi (salvo che il deal includa componente societaria)
- Notizie generiche di business/economia che citano lo sport solo di passaggio
- Articoli che menzionano "acquisizione" o "cessione" in contesto calciomercato giocatori
- Editoriali, opinioni, speculazioni giornalistiche senza fonti o dettagli concreti
- Notizie gia' note riformulate: tieni SOLO se c'e' un aggiornamento sostanziale
- Bilanci, risultati finanziari ordinari senza implicazioni M&A dirette
- Nomine di dirigenti/CEO salvo che siano legate a un cambio di proprieta
"""

USER_FILTER_TEMPLATE = """\
Analizza le seguenti notizie. Restituisci SOLO un array JSON con gli indici \
(0-based) delle notizie che rappresentano una REALE opportunita' M&A nel settore sport.

REGOLA CHIAVE: chiediti "un avvocato M&A sport di Hogan Lovells potrebbe \
lavorare su questa operazione?" Se la risposta e' no, SCARTA.

Sii MOLTO severo. Meglio perdere una notizia marginale che includere rumore. \
Rispondi SOLO con il JSON array, nessun altro testo.

Notizie:
{articles_text}
"""

# ---------------------------------------------------------------------------
# Prompt PASSAGGIO 2 — ranking + riassunto
# ---------------------------------------------------------------------------
SYSTEM_SUMMARIZE = """\
Sei un analista M&A senior al servizio di un team legale. Per ogni notizia genera:
1. Un punteggio di importanza da 1 a 10:
   - 9-10: Deal confermato/closing, operazione ufficiale
   - 7-8: Trattativa avanzata, due diligence in corso, rumour molto credibile
   - 5-6: Rumour di mercato, segnali preliminari, interesse manifestato
   - 3-4: Speculazione, segnale debole
2. Uno stato dell'operazione tra questi 4 valori ESATTI:
   - "Confermato": deal chiuso, closing completato, operazione ufficiale annunciata
   - "In Trattativa": due diligence in corso, negoziazione avanzata, mandato conferito, advisor nominato
   - "Rumour": indiscrezione di mercato, fonti anonime, interesse manifestato ma non confermato
   - "Speculazione": segnale debole, analisi speculativa, nessuna fonte diretta
3. Un riassunto strutturato in 2-4 bullet point:
   - Chi sono le parti coinvolte
   - Cosa: natura dell'operazione (acquisizione, cessione, ingresso investitore...)
   - Valore/dimensione se noto
   - Stato attuale dell'operazione

Rispondi in italiano. Sii conciso e preciso.
"""

USER_SUMMARIZE_TEMPLATE = """\
Per ciascuna delle seguenti notizie, restituisci un JSON array di oggetti con:
- "index": indice 0-based della notizia
- "score": punteggio importanza 1-10
- "deal_status": uno tra "Confermato", "In Trattativa", "Rumour", "Speculazione"
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
    scored: list[tuple[int, dict, str, str]] = []  # (score, article, key_points, deal_status)

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
                    ds = item.get("deal_status", "Rumour")
                    # Valida deal_status
                    if ds not in ("Confermato", "In Trattativa", "Rumour", "Speculazione"):
                        ds = "Rumour"
                    scored.append((score, batch[idx], kp, ds))
        except Exception:
            logger.exception("Errore riassunto batch %d", batch_start)
            for art in batch:
                scored.append((5, art, "- Riassunto non disponibile", "Rumour"))

    # Scarta articoli troppo speculativi (score < 3)
    scored = [(s, a, k, d) for s, a, k, d in scored if s >= 3]

    # Ordina per score decrescente e taglia
    scored.sort(key=lambda x: x[0], reverse=True)
    top = scored[:MAX_TOP_NEWS]

    enriched: list[dict] = []
    for score, art, kp, ds in top:
        art["importance_score"] = score
        art["key_points"] = kp
        art["deal_status"] = ds
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
