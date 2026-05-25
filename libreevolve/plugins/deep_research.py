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


def arxiv_search_result(query: str, max_results: int = 3) -> dict:
    """Search arXiv and return synthesis plus bounded source provenance."""
    url = _arxiv_query_url(query, max_results=max_results)
    try:
        with urllib.request.urlopen(url, timeout=15) as resp:
            body = resp.read()
    except Exception as exc:
        _log.debug("arXiv search failed: %s", exc)
        return {
            "status": "error",
            "provider": "arxiv",
            "query_url": url,
            "error": str(exc),
            "sources": [],
        }

    try:
        root = ET.fromstring(body)
    except ET.ParseError as exc:
        return {
            "status": "error",
            "provider": "arxiv",
            "query_url": url,
            "error": f"parse_error:{exc}",
            "sources": [],
        }

    sources = [_arxiv_source_from_entry(entry) for entry in root.findall(f"{_ATOM}entry")]
    sources = [source for source in sources if source.get("title")]
    if not sources:
        return {
            "status": "empty",
            "provider": "arxiv",
            "query_url": url,
            "sources": [],
        }
    lines = []
    for source in sources:
        title = source["title"]
        url_text = source.get("url") or source.get("id") or ""
        summary = source.get("summary_excerpt", "")
        citation = f" ({url_text})" if url_text else ""
        lines.append(f"- {title}{citation}: {summary}")
    synthesis = "\n".join(lines)
    return {
        "status": "ok",
        "provider": "arxiv",
        "query_url": url,
        "synthesis": synthesis,
        "sources": sources,
    }


def arxiv_search(query: str, max_results: int = 3) -> str | None:
    """Search arXiv for papers matching *query* and return a brief synthesis.

    Uses the free arXiv API (no key required). Returns None on network
    errors so evolution continues uninterrupted.
    """
    result = arxiv_search_result(query, max_results=max_results)
    return result.get("synthesis") if result.get("status") == "ok" else None


def _arxiv_query_url(query: str, max_results: int = 3) -> str:
    return (
        "http://export.arxiv.org/api/query?"
        + urllib.parse.urlencode(
            {
                "search_query": f"all:{query}",
                "max_results": max_results,
                "sortBy": "relevance",
            }
        )
    )


def _arxiv_source_from_entry(entry: ET.Element) -> dict:
    title = _compact(entry.findtext(f"{_ATOM}title"))
    summary = _compact(entry.findtext(f"{_ATOM}summary"))
    source_id = _compact(entry.findtext(f"{_ATOM}id"))
    url = source_id
    for link in entry.findall(f"{_ATOM}link"):
        href = link.attrib.get("href")
        if href and link.attrib.get("rel", "alternate") == "alternate":
            url = href
            break
    authors = [
        _compact(author.findtext(f"{_ATOM}name"))
        for author in entry.findall(f"{_ATOM}author")
    ]
    authors = [author for author in authors if author]
    return {
        "id": source_id,
        "url": url,
        "title": title,
        "authors": authors,
        "published": _compact(entry.findtext(f"{_ATOM}published")),
        "updated": _compact(entry.findtext(f"{_ATOM}updated")),
        "summary_excerpt": summary[:200],
        "summary_sha256": hashlib.sha256(summary.encode("utf-8")).hexdigest()
        if summary
        else "",
    }


def _compact(value: str | None) -> str:
    return " ".join((value or "").split())


class DeepResearchPlugin(PluginBase):
    """DeepEvolve-inspired web-search context before generation.

    This does not implement DeepEvolve's cross-file debug/refinement loop.
    Source: arXiv 2510.06056. Hook: on_generation_start.
    Default uses the free arXiv API. Pass search_fn=callable(query)->str
    or callable(query)->dict to override with a custom search provider.
    """
    def __init__(self, search_fn=None, search_every: int = 10):
        self._search_fn    = search_fn or arxiv_search_result
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
        synthesis, result_metadata = _normalize_search_result(result)
        event.update(result_metadata)
        if synthesis:
            self._synthesis = synthesis
            event.update(
                {
                    "status": "ok",
                    "result_chars": len(self._synthesis),
                    "synthesis_sha256": hashlib.sha256(
                        self._synthesis.encode("utf-8")
                    ).hexdigest(),
                }
            )
        elif event.get("status") != "error":
            event.update({"status": "empty", "result_chars": 0})
        self._events.append(event)

    def build_extra_context(self, parent, inspirations) -> str:
        return f"[DEEP RESEARCH]\n{self._synthesis}\n" if self._synthesis else ""

    def prompt_context_metadata(self) -> dict:
        if not self._events:
            return {}
        return {"retrieval_events": list(self._events[-5:])}


def _normalize_search_result(result: object) -> tuple[str, dict]:
    if not isinstance(result, dict):
        return (str(result), {}) if result else ("", {})
    status = result.get("status")
    metadata: dict = {}
    for key in ("provider", "query_url", "sources", "error"):
        value = result.get(key)
        if value:
            metadata[key] = value
    if status == "error":
        metadata["status"] = "error"
        metadata["result_chars"] = 0
        return "", metadata
    if status == "empty":
        metadata["status"] = "empty"
        metadata["result_chars"] = 0
        return "", metadata
    synthesis = str(result.get("synthesis") or result.get("text") or "")
    return synthesis, metadata
