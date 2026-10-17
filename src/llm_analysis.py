"""
LLM-powered analysis generation using Groq.

Produces query-aware analytical report content grounded in web-search evidence,
so the generated report reflects the user's actual research prompt rather than
static, topic-agnostic boilerplate.

Public API:
  - generate_analysis(query, evidence_items) -> dict with statistical_data,
    key_themes, synthesis, strategic_implications, recommendations, limitations
  - generate_fallback_evidence_raw(query) -> list of evidence dicts (fact,
    source_title, source_url, snippet, confidence) for when live search fails
  - build_fallback_analysis(query, evidence_items) -> same dict shape as
    generate_analysis, used if the Groq call itself fails
"""
import json
import re
from typing import List, Dict, Any

from groq import Groq

from src.config import settings


# --------------------------------------------------------------------------- #
# Internal helpers
# --------------------------------------------------------------------------- #
def _model_name() -> str:
    """Strip the CrewAI 'groq/' prefix to get the raw model id for the SDK."""
    return settings.GROQ_MODEL.replace("groq/", "", 1).strip()


def _client() -> Groq:
    return Groq(api_key=settings.GROQ_API_KEY)


def _evidence_context(evidence_items: List[Dict[str, Any]]) -> str:
    lines = []
    for e in evidence_items:
        url = e.get("source_url", "")
        src = e.get("source_title", "Web Source")
        if url:
            src = f"{src} — {url}"
        lines.append(
            f"{e.get('id', '[E?]')} {e.get('fact', '')}\n"
            f"   Source: {src}\n"
            f"   Snippet: {e.get('snippet', '')}"
        )
    return "\n".join(lines)


def _strip_fence(text: str) -> str:
    """Remove markdown code fences if the model wrapped its JSON output."""
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```(?:json)?\s*", "", text, flags=re.IGNORECASE)
        text = re.sub(r"\s*```$", "", text)
    return text.strip()


def _chat_json(messages: List[Dict[str, str]], temperature: float = 0.3) -> dict:
    """Call Groq with JSON mode and parse the response."""
    resp = _client().chat.completions.create(
        model=_model_name(),
        messages=messages,
        temperature=temperature,
        response_format={"type": "json_object"},
    )
    raw = resp.choices[0].message.content or "{}"
    return json.loads(_strip_fence(raw))


_SYSTEM = "You are a precise research analyst that returns only valid JSON."


# --------------------------------------------------------------------------- #
# Primary: query-aware analysis from search evidence
# --------------------------------------------------------------------------- #
def generate_analysis(query: str, evidence_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Generate query-aware analytical report content from evidence via Groq."""
    ev_text = _evidence_context(evidence_items)

    prompt = (
        "You are a senior research analyst preparing an executive intelligence brief.\n"
        f"RESEARCH OBJECTIVE: {query}\n\n"
        f"VERIFIED EVIDENCE (each item has a citation tag like [E1]):\n{ev_text}\n\n"
        "Based ONLY on the evidence above, generate a JSON object with these fields:\n"
        '- "statistical_data": an array of 5 to 8 objects, each with keys "metric", '
        '"baseline", "result", "variance", "citation". Extract real numbers from the '
        "evidence wherever available and express comparative metrics as baseline vs. "
        "observed with a variance (e.g. \"+18%\" or \"-64%\"). Always cite the matching "
        "evidence tag such as [E1]. If the evidence lacks hard numbers, synthesize "
        "qualitative comparative metrics that are still grounded in the findings.\n"
        '- "key_themes": an array of 3 to 4 objects, each with "title" and "detail" '
        "(2 to 4 sentences), derived from the evidence.\n"
        '- "synthesis": a 350 to 550 word executive synthesis that references specific '
        "evidence by its [E1], [E2] citation tags.\n"
        '- "strategic_implications": a 120 to 250 word note on implications, grounded '
        "in the evidence.\n"
        '- "recommendations": an array of 5 to 6 actionable recommendation strings.\n'
        '- "limitations": an 80 to 180 word note on the limitations of this evidence '
        "base.\n\n"
        "Return ONLY valid JSON. No markdown fences, no commentary."
    )

    data = _chat_json([
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": prompt},
    ])

    return {
        "statistical_data": data.get("statistical_data", []),
        "key_themes": data.get("key_themes", []),
        "synthesis": data.get("synthesis", ""),
        "strategic_implications": data.get("strategic_implications", ""),
        "recommendations": data.get("recommendations", []),
        "limitations": data.get("limitations", ""),
    }


# --------------------------------------------------------------------------- #
# Fallback evidence when live search returns nothing
# --------------------------------------------------------------------------- #
def generate_fallback_evidence_raw(query: str) -> List[Dict[str, Any]]:
    """
    When live web search is unavailable, ask Groq to produce a small set of
    evidence items from its own knowledge so the report still reflects the
    query. Returns raw dicts (without ids) for registration via the ledger.
    """
    prompt = (
        "A live web search failed. Using your own knowledge, generate 4 to 5 concise, "
        "factual evidence items about this topic so a research brief can still be "
        "assembled.\n"
        f"TOPIC: {query}\n\n"
        'Return a JSON object with a single key "evidence": an array where each item '
        'has "fact", "source_title", "source_url" (a best-guess canonical URL, or an '
        'empty string if unsure), "snippet", and "confidence" (0.0 to 1.0). Keep facts '
        'specific and verifiable. Append " (model knowledge)" to each source_title so it '
        "is transparent these are not live-search results.\n"
        "Return ONLY valid JSON."
    )

    data = _chat_json([
        {"role": "system", "content": _SYSTEM},
        {"role": "user", "content": prompt},
    ], temperature=0.2)

    items = data.get("evidence", [])
    cleaned = []
    for it in items:
        if not isinstance(it, dict):
            continue
        cleaned.append({
            "fact": it.get("fact", ""),
            "source_title": it.get("source_title", "Model knowledge base"),
            "source_url": it.get("source_url", ""),
            "snippet": it.get("snippet", ""),
            "confidence": float(it.get("confidence", 0.8)),
        })
    return cleaned


# --------------------------------------------------------------------------- #
# Last-resort: assemble analysis from evidence without an LLM call
# (used only if the Groq call itself raises)
# --------------------------------------------------------------------------- #
def build_fallback_analysis(query: str, evidence_items: List[Dict[str, Any]]) -> Dict[str, Any]:
    facts = [f"{e.get('id', '')} {e.get('fact', '')}" for e in evidence_items]
    findings = "\n".join(f"• {f}" for f in facts) or "No evidence was gathered."
    count = len(evidence_items)
    avg_conf = (
        sum(e.get("confidence", 0.9) for e in evidence_items) / count if count else 0.0
    )

    return {
        "statistical_data": [
            {
                "metric": "Evidence Sources Gathered",
                "baseline": "0",
                "result": str(count),
                "variance": f"+{count}",
                "citation": "[E1]",
            },
            {
                "metric": "Average Evidence Confidence",
                "baseline": "—",
                "result": f"{avg_conf * 100:.0f}%",
                "variance": "—",
                "citation": "[E1]",
            },
        ],
        "key_themes": [
            {
                "title": e.get("source_title", "Source")[:50],
                "detail": e.get("fact", ""),
            }
            for e in evidence_items[:4]
        ],
        "synthesis": (
            f"Research into '{query}' surfaced {count} findings:\n{findings}\n\n"
            "Note: LLM synthesis was unavailable, so this summary is assembled directly "
            "from the gathered search evidence."
        ),
        "strategic_implications": (
            f"The {count} sources gathered on '{query}' indicate active developments in "
            "this area that merit closer review. (Generated without LLM analysis.)"
        ),
        "recommendations": [
            f"Review source {e.get('id', '')} ({e.get('source_title', '')}) for further detail."
            for e in evidence_items[:5]
        ],
        "limitations": (
            "LLM-based analysis was unavailable, so this report is limited to raw search "
            "evidence without deeper synthesis, thematic analysis, or generated benchmarks."
        ),
    }
