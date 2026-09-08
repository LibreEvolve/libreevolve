"""Explicit release-candidate metadata; no ownership verification or deployment."""

from dataclasses import dataclass
import hashlib
import html
import ipaddress
import json
from pathlib import Path
import re
from urllib.parse import urlsplit

from libreevolve.alpha_share_io import checked_path


@dataclass(frozen=True)
class Publication:
    origin: str
    base: str
    approval_sha256: str
    private_receipt: dict
    configuration_bytes: bytes
    public_example_sha256: str | None


def load_publication(path: Path, *, approved_sha256: str, approved_by: str) -> Publication:
    path = checked_path(path, must_exist=True)
    if not path.is_file() or path.stat().st_size > 8192:
        raise ValueError("Publication configuration must be a bounded JSON file")
    data = path.read_bytes()
    return parse_publication(data, approved_sha256=approved_sha256, approved_by=approved_by)


def unique_fields(pairs: list[tuple]) -> dict:
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("Duplicate publication configuration field")
        result[key] = value
    return result


def parse_publication(data: bytes, *, approved_sha256: str, approved_by: str) -> Publication:
    if type(data) is not bytes or len(data) > 8192:
        raise ValueError("Publication configuration must be bounded bytes")
    digest = hashlib.sha256(data).hexdigest()
    if approved_sha256 != digest:
        raise ValueError("Publication approval must match the exact configuration bytes")
    value = json.loads(data, object_pairs_hook=unique_fields)
    if type(value) is not dict or set(value) != {"origin", "base_path", "ownership_evidence", "authorization_reference", "public_example_sha256"}:
        raise ValueError("Unexpected publication configuration fields")
    for text in (value["origin"], value["base_path"], value["ownership_evidence"], value["authorization_reference"], approved_by):
        if not isinstance(text, str) or not text.strip() or len(text) > 2048 or any(ord(c) < 32 for c in text):
            raise ValueError("Publication values must be bounded nonempty text")
    example_digest = value["public_example_sha256"]
    if example_digest is not None and (type(example_digest) is not str or not re.fullmatch(r"[0-9a-f]{64}", example_digest)):
        raise ValueError("Public example approval must be null or an exact payload digest")
    origin = value["origin"]
    parsed = urlsplit(origin)
    if parsed.scheme != "https" or parsed.path or parsed.query or parsed.fragment or parsed.username or parsed.password:
        raise ValueError("Publication origin must be a bare HTTPS origin")
    host = parsed.hostname or ""
    labels = host.split(".")
    if (origin != "https://" + host or len(host) > 253 or len(labels) < 2
            or any(not re.fullmatch(r"[a-z0-9](?:[a-z0-9-]{0,61}[a-z0-9])?", label) for label in labels)):
        raise ValueError("Publication origin requires a normalized DNS name without a port")
    try:
        ipaddress.ip_address(host)
    except ValueError:
        pass
    else:
        raise ValueError("An IP address is not a publication identity")
    if host.endswith((".localhost", ".local", ".invalid")):
        raise ValueError("Local and invalid domains are not publication origins")
    base = value["base_path"]
    if not re.fullmatch(r"/(?:[a-zA-Z0-9_-]+/)*", base):
        raise ValueError("Invalid publication base path")
    receipt = {"configuration_sha256": digest, "approved_by": approved_by,
               "ownership_evidence": value["ownership_evidence"],
               "authorization_reference": value["authorization_reference"],
               "boundary": "Operator-supplied references; builder does not authenticate approval or verify ownership."}
    return Publication(origin, base, digest, receipt, data, example_digest)


def validate_publication(value: Publication) -> None:
    try:
        expected = parse_publication(value.configuration_bytes, approved_sha256=value.approval_sha256,
                                     approved_by=value.private_receipt["approved_by"])
        if value != expected:
            raise ValueError("Modified publication configuration")
    except (KeyError, TypeError, AttributeError) as exc:
        raise ValueError("Malformed publication configuration") from exc


def metadata(publication: Publication, title: str, route: str) -> str:
    url = publication.origin + publication.base + (route + "/" if route else "")
    esc = html.escape
    description = f"{title} — LibreEvolve engineering preview: bounded Python bin-packing optimization with Codex OAuth."
    organization = json.dumps({"@context": "https://schema.org", "@type": "Organization",
                               "name": "LibreEvolve", "url": publication.origin + publication.base},
                              sort_keys=True).replace("<", "\\u003c")
    return (f'<link rel="canonical" href="{esc(url, quote=True)}">'
            '<meta name="robots" content="index,follow">'
            f'<meta property="og:type" content="website"><meta property="og:site_name" content="LibreEvolve">'
            f'<meta property="og:title" content="{esc(title, quote=True)} · LibreEvolve">'
            f'<meta property="og:description" content="{esc(description, quote=True)}">'
            f'<meta property="og:url" content="{esc(url, quote=True)}">'
            f'<script type="application/ld+json">{organization}</script>')


def discovery_files(publication: Publication, routes: list[dict]) -> dict[str, str]:
    base_url = publication.origin + publication.base
    urls = [base_url] + [base_url + row["route"] + "/" for row in routes]
    sitemap = ('<?xml version="1.0" encoding="UTF-8"?>\n'
               '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">' +
               "".join("<url><loc>" + html.escape(url) + "</loc></url>" for url in urls) + '</urlset>\n')
    return {publication.base.lstrip("/") + "sitemap.xml": sitemap,
            "robots.txt": f"User-agent: *\nDisallow: {publication.base}examples/\nSitemap: {base_url}sitemap.xml\n"}
