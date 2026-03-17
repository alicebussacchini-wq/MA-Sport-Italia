"""Filtra le notizie tramite Claude API per rilevanza M&A Sport."""

from __future__ import annotations

import json
import logging

import anthropic

from config import ANTHROPIC_API_KEY, CLAUDE_MODEL

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """\
Sei un analista specializzato in operazioni M&A (Mergers & Acquisitions) nel mondo \
dello sport italiano. Il tuo compito è valutare se una notizia è rilevante per:
- Acquisizioni / cessioni di club o società sportive
- Cambi di proprietà, ingresso di nuovi investitori o fondi
- Operazioni di private equity nello sport
- Trattative, rumour e negoziazioni societarie
- Ricapitalizzazioni, IPO, emissioni obbligazionarie di club
- Accordi commerciali strategici di grande portata (diritti TV, naming rights stadi)
- Due diligence, closing, lettere di intenti

NON sono rilevanti: risultati sportivi, calciomercato giocatori, infortuni, \
tattiche, classifiche, allenamenti, conferenze stampa tecniche.
"""

USER_PROMPT_TEMPLATE = """\
Analizza le seguenti notizie e restituisci SOLO un array JSON con gli indici \
(0-based) delle notizie rilevanti per M&A Sport. Rispondi SOLO con il JSON, \
nessun altro testo.

Notizie:
{articles_text}
"""

BATCH_SIZE = 20  # articoli per chiamata API


def _build_articles_text(articles: list[dict]) -> str:
    lines = []
    for i, art in enumerate(articles):
        lines.append(
            f"[{i}] {art['title']}\n    Fonte: {art['source']}\n    {art['summary'][:200]}"
        )
    return "\n\n".join(lines)


def _call_claude(articles: list[dict]) -> list[int]:
    """Chiama Claude per ottenere gli indici delle notizie rilevanti."""
    client = anthropic.Anthropic(api_key=ANTHROPIC_API_KEY)

    articles_text = _build_articles_text(articles)
    user_prompt = USER_PROMPT_TEMPLATE.format(articles_text=articles_text)

    try:
        message = client.messages.create(
            model=CLAUDE_MODEL,
            max_tokens=1024,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": user_prompt}],
        )
        response_text = message.content[0].text.strip()

        # Estrai il JSON dalla risposta
        if response_text.startswith("["):
            indices = json.loads(response_text)
        else:
            # Cerca un array JSON nella risposta
            start = response_text.index("[")
            end = response_text.rindex("]") + 1
            indices = json.loads(response_text[start:end])

        return [i for i in indices if isinstance(i, int) and 0 <= i < len(articles)]

    except Exception:
        logger.exception("Errore chiamata Claude API")
        # In caso di errore, ritorna tutti (fail-open)
        return list(range(len(articles)))


def filter_with_claude(articles: list[dict]) -> list[dict]:
    """Filtra le notizie usando Claude per determinare la rilevanza M&A.

    Args:
        articles: Lista di articoli da filtrare.

    Returns:
        Lista di articoli rilevanti per M&A Sport.
    """
    if not ANTHROPIC_API_KEY:
        logger.warning("ANTHROPIC_API_KEY non configurata – skip filtro Claude")
        return articles

    if not articles:
        return []

    relevant: list[dict] = []

    # Processa in batch
    for batch_start in range(0, len(articles), BATCH_SIZE):
        batch = articles[batch_start : batch_start + BATCH_SIZE]
        logger.info(
            "Claude filter batch %d-%d di %d",
            batch_start,
            batch_start + len(batch),
            len(articles),
        )
        indices = _call_claude(batch)
        for idx in indices:
            relevant.append(batch[idx])

    logger.info(
        "Claude filter: %d/%d articoli rilevanti", len(relevant), len(articles)
    )
    return relevant
