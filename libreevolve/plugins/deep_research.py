from __future__ import annotations
from datetime import datetime, timezone
import hashlib
import logging
import urllib.request
import urllib.parse
import xml.etree.ElementTree as ET
from libreevolve.plugins.base import PluginBase

_log = logging.getLogger(__name__)

# arXiv Atom namespace
_ATOM = "{http://www.w3.org/2005/Atom}"


def arxiv_search(query: str, max_results: int = 3) -> str | None:
    """Search arXiv for papers matching *query* and return a brief synthesis.

    Uses the free arXiv API (no key required). Returns None on network
    errors so evolution continues uninterrupted.
    """
    url = ("http://export.arxiv.org/api/query?"
           + urllib.parse.urlencode({"search_query": f"all:{query}",
                                     "max_results": max_results,
                                     "sortBy": "relevance"}))
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = resp.read()
    except Exception as exc:
        _log.debug("arXiv search failed: %s", exc)
        return None

    try:
        root = ET.fromstring(body)
    except ET.ParseError:
        return None

    entries = root.findall(f"{_ATOM}entry")
    if not entries:
        return None

    lines: list[str] = []
    for entry in entries:
        title   = (entry.findtext(f"{_ATOM}title") or "").strip().replace("\n", " ")
        summary = (entry.findtext(f"{_ATOM}summary") or "").strip().replace("\n", " ")[:200]
        if title:
            lines.append(f"- {title}: {summary}")
    return "\n".join(lines) if lines else None


class DeepResearchPlugin(PluginBase):
    """DeepEvolve-inspired web-search context before generation.

    This does not implement DeepEvolve's cross-file debug/refinement loop.
    Source: arXiv 2510.06056. Hook: on_generation_start.
    Default uses the free arXiv API. Pass search_fn=callable(query)->str
    to override with a custom search provider.
    """
    def __init__(self, search_fn=None, search_every: int = 10):
        self._search_fn    = search_fn or arxiv_search
        self._provider     = "arxiv" if search_fn is None else "custom"
        self._search_every = search_every
        self._synthesis    = ""
        self._events: list[dict] = []

    def on_generation_start(self, gen: int, db) -> None:
        if gen % self._search_every != 0: return
        best = db.best()
        if best is None: return
        query = f"evolutionary algorithm optimization fitness~{best.fitness:.3f}"
        event = {
            "provider": self._provider,
            "query": query,
            "generation": gen,
            "best_id": best.id,
            "best_fitness": best.fitness,
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
        try:
            result = self._search_fn(query)
        except Exception as exc:
            _log.debug("configured research search failed: %s", exc)
            event.update({"status": "error", "error": str(exc), "result_chars": 0})
            self._events.append(event)
            return
        if result:
            self._synthesis = str(result)
            event.update(
                {
                    "status": "ok",
                    "result_chars": len(self._synthesis),
                    "synthesis_sha256": hashlib.sha256(
                        self._synthesis.encode("utf-8")
                    ).hexdigest(),
                }
            )
        else:
            event.update({"status": "empty", "result_chars": 0})
        self._events.append(event)

    def build_extra_context(self, parent, inspirations) -> str:
        return f"[DEEP RESEARCH]\n{self._synthesis}\n" if self._synthesis else ""

    def prompt_context_metadata(self) -> dict:
        if not self._events:
            return {}
        return {"retrieval_events": list(self._events[-5:])}
