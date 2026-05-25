from unittest.mock import MagicMock, patch
from libreevolve.plugins.deep_research import (
    DeepResearchPlugin,
    arxiv_search,
    arxiv_search_result,
)
from libreevolve.population.program import Program

def _p(): return Program(code="x=1", fitness=0.5)

def test_empty_before_search():
    assert DeepResearchPlugin().build_extra_context(_p(), []) == ""

def test_calls_at_multiples_of_10():
    calls = []
    plugin = DeepResearchPlugin(search_fn=lambda q: (calls.append(q) or "r"))
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    plugin.on_generation_start(5, db)
    plugin.on_generation_start(10, db)
    assert len(calls) == 2

def test_context_shows_synthesis():
    plugin = DeepResearchPlugin(search_fn=lambda q: "test synthesis")
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    ctx = plugin.build_extra_context(_p(), [])
    assert "DEEP RESEARCH" in ctx and "test synthesis" in ctx
    event = plugin.prompt_context_metadata()["retrieval_events"][-1]
    assert event["provider"] == "custom"
    assert event["status"] == "ok"
    assert event["query"].startswith("evolutionary algorithm optimization")
    assert event["best_id"] == db.best.return_value.id
    assert event["result_chars"] == len("test synthesis")
    assert event["synthesis_sha256"]


def test_records_empty_retrieval_event():
    plugin = DeepResearchPlugin(search_fn=lambda q: None)
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    event = plugin.prompt_context_metadata()["retrieval_events"][-1]
    assert event["status"] == "empty"
    assert event["result_chars"] == 0
    assert plugin.build_extra_context(_p(), []) == ""


def test_records_failed_retrieval_event():
    def fail(_query):
        raise RuntimeError("offline")

    plugin = DeepResearchPlugin(search_fn=fail)
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    event = plugin.prompt_context_metadata()["retrieval_events"][-1]
    assert event["status"] == "error"
    assert event["error_type"] == "provider_exception"
    assert event["error"] == "offline"
    assert event["result_chars"] == 0

def test_default_uses_structured_arxiv_search():
    """Default search_fn should preserve arXiv source metadata, not be a no-op."""
    plugin = DeepResearchPlugin()
    assert plugin._search_fn is arxiv_search_result

def test_arxiv_search_parses_xml():
    """arxiv_search should parse Atom XML into a summary string."""
    fake_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/1234.56789v1</id>
        <title>Evolutionary Optimization of Things</title>
        <summary>We optimize things with evolution.</summary>
        <published>2026-01-02T00:00:00Z</published>
        <updated>2026-01-03T00:00:00Z</updated>
        <author><name>Ada Lovelace</name></author>
        <link href="http://arxiv.org/abs/1234.56789v1" rel="alternate" />
      </entry>
    </feed>"""
    with patch("libreevolve.plugins.deep_research.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_xml
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = arxiv_search("test query")
    assert result is not None
    assert "Evolutionary Optimization" in result
    assert "http://arxiv.org/abs/1234.56789v1" in result


def test_arxiv_search_result_preserves_source_metadata():
    fake_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/1234.56789v1</id>
        <title>Evolutionary Optimization of Things</title>
        <summary>We optimize things with evolution.</summary>
        <published>2026-01-02T00:00:00Z</published>
        <updated>2026-01-03T00:00:00Z</updated>
        <author><name>Ada Lovelace</name></author>
        <link href="http://arxiv.org/abs/1234.56789v1" rel="alternate" />
      </entry>
    </feed>"""
    with patch("libreevolve.plugins.deep_research.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_xml
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = arxiv_search_result("test query")
    assert result["status"] == "ok"
    assert result["query_url"].startswith("http://export.arxiv.org/api/query?")
    assert result["sources"][0]["id"] == "http://arxiv.org/abs/1234.56789v1"
    assert result["sources"][0]["url"] == "http://arxiv.org/abs/1234.56789v1"
    assert result["sources"][0]["authors"] == ["Ada Lovelace"]
    assert result["sources"][0]["published"] == "2026-01-02T00:00:00Z"
    assert result["sources"][0]["updated"] == "2026-01-03T00:00:00Z"
    assert result["sources"][0]["summary_sha256"]


def test_default_plugin_records_arxiv_sources():
    fake_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom">
      <entry>
        <id>http://arxiv.org/abs/1234.56789v1</id>
        <title>Evolutionary Optimization of Things</title>
        <summary>We optimize things with evolution.</summary>
        <link href="http://arxiv.org/abs/1234.56789v1" rel="alternate" />
      </entry>
    </feed>"""
    plugin = DeepResearchPlugin()
    db = MagicMock(); db.best.return_value = _p()
    with patch("libreevolve.plugins.deep_research.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = fake_xml
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        plugin.on_generation_start(0, db)
    event = plugin.prompt_context_metadata()["retrieval_events"][-1]
    assert event["provider"] == "arxiv"
    assert event["query_url"].startswith("http://export.arxiv.org/api/query?")
    assert event["sources"][0]["id"] == "http://arxiv.org/abs/1234.56789v1"
    assert "http://arxiv.org/abs/1234.56789v1" in plugin.build_extra_context(_p(), [])

def test_arxiv_search_returns_none_on_network_error():
    with patch("libreevolve.plugins.deep_research.urllib.request.urlopen",
               side_effect=ConnectionError("offline")):
        assert arxiv_search("test") is None


def test_arxiv_search_result_records_network_error_type():
    with patch(
        "libreevolve.plugins.deep_research.urllib.request.urlopen",
        side_effect=ConnectionError("offline"),
    ):
        result = arxiv_search_result("test")
    assert result["status"] == "error"
    assert result["error_type"] == "network_error"
    assert result["error"] == "offline"


def test_arxiv_search_result_records_parse_error_type():
    with patch("libreevolve.plugins.deep_research.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = b"<not valid"
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        result = arxiv_search_result("test")
    assert result["status"] == "error"
    assert result["error_type"] == "parse_error"
    assert result["error"]

def test_arxiv_search_returns_none_on_empty_results():
    empty_xml = b"""<?xml version="1.0" encoding="UTF-8"?>
    <feed xmlns="http://www.w3.org/2005/Atom"></feed>"""
    with patch("libreevolve.plugins.deep_research.urllib.request.urlopen") as mock_open:
        mock_resp = MagicMock()
        mock_resp.read.return_value = empty_xml
        mock_resp.__enter__ = lambda s: s
        mock_resp.__exit__ = MagicMock(return_value=False)
        mock_open.return_value = mock_resp
        assert arxiv_search("nonsense query xyz") is None

def test_custom_search_fn_overrides_default():
    plugin = DeepResearchPlugin(search_fn=lambda q: "custom")
    db = MagicMock(); db.best.return_value = _p()
    plugin.on_generation_start(0, db)
    assert "custom" in plugin.build_extra_context(_p(), [])


def test_no_metadata_before_search():
    assert DeepResearchPlugin().prompt_context_metadata() == {}
