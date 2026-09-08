"""Presentation-only contracts for the private, offline local report."""

import copy
from html.parser import HTMLParser

from libreevolve.alpha_report import render_html


class Document(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


def test_local_report_preserves_escaped_evidence_without_mutation():
    report = {
        "status": "cancelled",
        "scope": "<script>alert(1)</script>",
        "best": {"code": "</pre><img src=https://example.test/leak>",
                 "training": {"status": "invalid", "correctness": False, "score": 0}},
        "usage": {"estimated_cost_usd": None},
        "issues": [{"detail": "private local evidence retained"}],
    }
    before = copy.deepcopy(report)
    page = render_html(report)
    assert report == before
    assert "cancelled" in page and "invalid" in page and "False" in page
    assert "Unknown / unavailable" in page
    assert "private local evidence retained" in page
    assert "&lt;script&gt;" in page and "&lt;img" in page
    assert "not a public share export" in page
    document = Document()
    document.feed(page)
    assert not any(tag in {"script", "img", "iframe", "link", "form"}
                   for tag, _ in document.tags)


def test_local_report_has_offline_responsive_keyboard_and_print_contracts():
    page = render_html({})
    document = Document()
    document.feed(page)
    regions = [attrs for tag, attrs in document.tags if attrs.get("role") == "region"]
    assert regions == [{"class": "table-scroll", "role": "region",
                        "aria-label": "Independent reevaluation table", "tabindex": "0"}]
    assert any(tag == "meta" and attrs.get("http-equiv") == "Content-Security-Policy"
               and "default-src 'none'" in attrs["content"] for tag, attrs in document.tags)
    assert "prefers-color-scheme:dark" in page
    assert "overflow-x:auto" in page and ":focus-visible" in page
    assert "@media print" in page
    assert "animation:" not in page and "transition:" not in page
    assert '<th scope="col">' in page and '<th scope="row">' in page
