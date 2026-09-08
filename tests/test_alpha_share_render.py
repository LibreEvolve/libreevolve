import socket
import subprocess
import xml.etree.ElementTree as ET

import pytest

from libreevolve.alpha_share_record import payload_sha256
from libreevolve.alpha_share_render import render_public
from tests.test_alpha_share_record import record


def render(data):
    return render_public(data, approved_sha256=payload_sha256(data), approved_by="private-reviewer")


def test_static_deterministic_public_files_and_private_receipt(monkeypatch):
    def forbidden(*args, **kwargs):
        raise AssertionError("public rendering must not execute or connect")
    monkeypatch.setattr(subprocess, "Popen", forbidden)
    monkeypatch.setattr(socket, "socket", forbidden)
    data = record()
    first, receipt = render(data)
    assert render(data)[0] == first
    assert set(first) == {"index.html", "card.svg", "result.txt", "result.json"}
    assert receipt["approved_by"] == "private-reviewer"
    for content in first.values():
        assert "private-reviewer" not in content
        assert "<script" not in content
    assert "SYNTHETIC FIXTURE" in first["index.html"]
    assert "SYNTHETIC FIXTURE" in first["card.svg"]
    assert "unknown" in first["result.txt"]
    assert "Run: aborted" in first["index.html"]
    ET.fromstring(first["card.svg"])


def test_hostile_text_stays_text():
    data = record()
    data["limitations"] = ['</pre><script>alert("x")</script>']
    files, _ = render(data)
    assert "<script>" not in files["index.html"]
    assert "&lt;script&gt;" in files["index.html"]
    assert data["limitations"][0] in files["result.txt"]


def test_missing_approval_rejected():
    with pytest.raises(ValueError):
        render_public(record(), approved_sha256="", approved_by="reviewer")
