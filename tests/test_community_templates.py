"""Local form contracts; not proof of GitHub activation or moderation readiness."""

from pathlib import Path
import re
from urllib.parse import urlsplit

import pytest
import yaml


ROOT = Path(__file__).resolve().parents[1]
FORMS = ROOT / ".github/ISSUE_TEMPLATE"


def form(name):
    return yaml.safe_load((FORMS / f"{name}.yml").read_text(encoding="utf-8"))


@pytest.mark.parametrize("name", ["bug", "experiment", "question"])
def test_form_structure_and_disclosure(name):
    data = form(name)
    assert set(data) == {"name", "description", "title", "body"}
    assert all(isinstance(data[key], str) and data[key].strip()
               for key in ("name", "description", "title"))
    assert isinstance(data["body"], list) and data["body"]
    ids = []
    for field in data["body"]:
        kind = field["type"]
        assert kind in {"markdown", "input", "textarea", "dropdown", "checkboxes"}
        attrs = field["attributes"]
        if kind == "markdown":
            assert isinstance(attrs["value"], str)
            continue
        ids.append(field["id"])
        assert re.fullmatch(r"[a-z][a-z0-9-]*", field["id"])
        assert isinstance(attrs["label"], str) and attrs["label"].strip()
        if kind == "dropdown":
            assert len(attrs["options"]) == len(set(attrs["options"])) >= 2
            assert all(isinstance(value, str) for value in attrs["options"])
        if "validations" in field:
            assert type(field["validations"]["required"]) is bool
    assert len(ids) == len(set(ids))
    disclosure = next(f for f in data["body"] if f.get("id") == "disclosure")
    assert disclosure["type"] == "checkboxes"
    assert all(o["required"] is True for o in disclosure["attributes"]["options"])
    text = (FORMS / f"{name}.yml").read_text(encoding="utf-8")
    assert "OAuth" in text and "private" in text and "prompts" in text
    assert "account details" in text and "home paths" in text


def test_experiment_preserves_distinct_outcomes_and_unknowns():
    fields = {f["id"]: f for f in form("experiment")["body"] if "id" in f}
    assert {"version", "evidence-kind", "reproduction", "outcome", "checks", "usage", "disclosure"} <= fields.keys()
    for key in ("version", "evidence-kind", "reproduction", "outcome", "checks", "usage"):
        assert fields[key]["validations"]["required"] is True
    outcome = fields["outcome"]["attributes"]["description"]
    assert all(term in outcome for term in ("cancelled", "validity", "retention", "unchanged", "worse", "unknown"))
    checks = fields["checks"]["attributes"]["description"]
    assert "identical cases within one split" in checks and "freeze selection" in checks
    assert "unknown" in fields["usage"]["attributes"]["description"]


def test_chooser_has_real_scoped_destinations_without_activation_claims():
    data = yaml.safe_load((FORMS / "config.yml").read_text(encoding="utf-8"))
    assert data["blank_issues_enabled"] is True
    assert len(data["contact_links"]) == 2
    for link in data["contact_links"]:
        assert set(link) == {"name", "url", "about"}
        parsed = urlsplit(link["url"])
        assert parsed.scheme == "https" and parsed.netloc == "github.com"
        prefix = "/LibreEvolve/libreevolve/blob/main/"
        assert parsed.path.startswith(prefix)
        assert (ROOT / parsed.path.removeprefix(prefix)).is_file()


def test_community_doc_local_links_and_activation_boundary():
    path = ROOT / "docs/community.md"
    text = path.read_text(encoding="utf-8")
    for target in re.findall(r"\]\(([^)]+)\)", text):
        if not target.startswith("https://"):
            assert (path.parent / target).is_file()
    assert "draft pull\nrequest does not activate" in text
    assert "not a private security" in text
    assert "No response deadline" in text


def test_pr_template_keeps_evidence_and_disclosure_distinct():
    text = (ROOT / ".github/PULL_REQUEST_TEMPLATE.md").read_text(encoding="utf-8")
    for term in ("offline tests", "live model", "hosted CI", "credentials", "OAuth", "private source", "authorization"):
        assert term in text
