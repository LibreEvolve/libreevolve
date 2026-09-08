"""Deterministic local static build. No candidate execution or network access."""

from __future__ import annotations

import argparse
import hashlib
import html
import json
from pathlib import Path, PurePosixPath
import re
import sys
from urllib.parse import unquote, urlsplit

from markdown_it import MarkdownIt


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from examples import PreparedExample, prepare_example, receipt_destination, write_private_receipt, validate_example
from libreevolve.alpha_share_io import checked_path
from publication import Publication, load_publication, validate_publication, metadata, discovery_files
SOURCE_URL = "https://github.com/LibreEvolve/libreevolve/blob/fa8ee2769a6e141b95d93043265a5e90c978f26d/"
PLACEHOLDER_ORIGIN = "https://example.invalid"


def base_path(value: str) -> str:
    if not re.fullmatch(r"/(?:[a-zA-Z0-9_-]+/)*", value):
        raise ValueError("Base path must be / or slash-delimited simple path segments ending in /.")
    return value


def read_source(root: Path, relative: str) -> str:
    path = PurePosixPath(relative)
    if path.is_absolute() or ".." in path.parts or not path.parts:
        raise ValueError("Source must be a repository-relative path.")
    target = root.joinpath(*path.parts)
    if any(p.is_symlink() for p in (target, *target.parents)):
        raise ValueError("Symlink source is not allowed.")
    if not target.is_file() or target.stat().st_size > 1_048_576:
        raise ValueError(f"Missing or overlarge source: {relative}")
    return target.read_text(encoding="utf-8")


def load_routes(root: Path) -> list[dict]:
    routes = json.loads(read_source(root, "site/routes.json"))
    seen, sources = set(), set()
    for row in routes:
        if set(row) != {"route", "title", "source"}:
            raise ValueError("Unexpected route fields.")
        if not re.fullmatch(r"[a-z][a-z0-9-]*", row["route"]) or row["route"] in seen:
            raise ValueError("Invalid or duplicate route.")
        if row["source"] in sources or not row["source"].endswith(".md"):
            raise ValueError("Invalid or duplicate Markdown source.")
        read_source(root, row["source"])
        seen.add(row["route"])
        sources.add(row["source"])
    return routes


def render_markdown(text: str, source: str, routes: list[dict], root: Path, base: str) -> str:
    parser = MarkdownIt("commonmark", {"html": False}).enable("table")
    parser.renderer.rules["table_open"] = lambda tokens, idx, options, env: '<div class="table-scroll" role="region" aria-label="Scrollable documentation table" tabindex="0"><table>\n'
    parser.renderer.rules["table_close"] = lambda tokens, idx, options, env: '</table></div>\n'
    tokens = parser.parse(text)
    mapping = {row["source"]: base + row["route"] + "/" for row in routes}
    slug_counts = {}
    for index, token in enumerate(tokens):
        if token.type == "th_open":
            token.attrSet("scope", "col")
        if token.type == "heading_open":
            title = tokens[index + 1].content
            slug = re.sub(r"\s+", "-", re.sub(r"[^\w\s-]", "", title.lower()).strip()) or "section"
            count = slug_counts.get(slug, 0)
            slug_counts[slug] = count + 1
            token.attrSet("id", slug + (f"-{count}" if count else ""))
        for child in token.children or []:
            if child.type == "image":
                raise ValueError("Embedded Markdown images require a separate reviewed asset integration.")
            if child.type != "link_open":
                continue
            href = child.attrGet("href") or ""
            parsed = urlsplit(href)
            if parsed.scheme:
                if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
                    raise ValueError("Only HTTPS external links are permitted.")
                child.attrSet("rel", "noreferrer")
                continue
            if parsed.netloc or href.startswith("/") or parsed.query:
                raise ValueError("Unexpected absolute or query-bearing documentation link.")
            if not parsed.path:
                continue
            target = (root / source).parent.joinpath(unquote(parsed.path)).resolve()
            try:
                relative = target.relative_to(root.resolve()).as_posix()
            except ValueError as exc:
                raise ValueError("Documentation link escapes the repository.") from exc
            if not target.is_file():
                raise ValueError(f"Broken source link in {source}: {href}")
            destination = mapping.get(relative, SOURCE_URL + relative)
            child.attrSet("href", destination + ("#" + parsed.fragment if parsed.fragment else ""))
    return parser.renderer.render(tokens, parser.options, {})


def shell(title: str, content: str, routes: list[dict], base: str, route: str = "", publication: Publication | None = None) -> str:
    esc = html.escape
    discoverability = metadata(publication, title, route) if publication else '<meta name="robots" content="noindex,nofollow">'
    deployment_label = "Release candidate · no analytics · deployment not verified by this build" if publication else "Local preview · no analytics · no approved deployment origin"
    navigation = "".join(
        f'<a href="{base}{r["route"]}/"' + (' aria-current="page"' if r["route"] == route else '')
        + f'>{esc(r["title"])}</a>' for r in routes
    )
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
{discoverability}<meta name="description" content="{esc(title)} — LibreEvolve engineering preview: bounded Python bin-packing optimization with Codex OAuth.">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; style-src 'self'; script-src 'self'; img-src 'self'; base-uri 'none'; form-action 'none'">
<title>{esc(title)} · LibreEvolve</title><link rel="stylesheet" href="{base}assets/site.css">
<script defer src="{base}assets/site.js"></script></head><body>
<a class="skip" href="#main">Skip to content</a>
<header class="masthead"><a class="wordmark" href="{base}">LibreEvolve</a>
<nav aria-label="Primary"><a href="{base}getting-started/">Run the preview</a><a href="{base}results/">Evidence</a>
<details><summary>Explore</summary><div class="menu">{navigation}</div></details></nav>
<button class="theme" type="button" hidden aria-label="Switch color theme">Theme</button></header>
<main id="main" tabindex="-1">{content}</main>
<footer><p>Engineering preview. Evolve code. Show the evidence.</p>
<p><a href="{base}safety/">Safety and scope</a> · <a href="{base}contributing/">Contribute</a> ·
<a href="https://github.com/LibreEvolve/libreevolve" rel="noreferrer">Public source</a></p>
<p class="muted">{deployment_label}</p></footer></body></html>'''


def homepage(base: str) -> str:
    return f'''<section class="hero"><div class="hero-inner">
<p class="eyebrow">Engineering preview · Bounded Python bin packing · Codex OAuth</p>
<h1>LibreEvolve</h1><h2>Evolve code.<br>Show the evidence.</h2>
<p class="intro">An open-source workbench for inspectable code-evolution experiments.</p>
<div class="actions"><a class="button" href="{base}results/">Read the evidence guide <span aria-hidden="true">↗</span></a>
<a href="{base}getting-started/">Run the preview <span aria-hidden="true">→</span></a></div>
</div></section>
<section class="section evidence"><p class="eyebrow">Start with what the result actually says</p>
<h2>A finished run is not<br>a proven improvement.</h2><p>Inspect validity, retention, named checks and missing usage separately. Unchanged and unsuccessful outcomes belong in the record.</p>
<p><a href="{base}experiments/">Experiment requirements</a> — no approved live experiment is published in this local build.</p></section>
<section class="section workflow"><p class="eyebrow">A bounded workflow</p><h2>Small changes.<br>Inspectable consequences.</h2>
<ol><li><span>01</span><h3>Start with a seed</h3><p>Read the task and run offline preflight before choosing live subscription use.</p></li>
<li><span>02</span><h3>Search for changes</h3><p>Authorize a bounded Codex run. Improvement is not guaranteed.</p></li>
<li><span>03</span><h3>Inspect the evidence</h3><p>Keep run status, validity, retention and corpus-specific quality distinct.</p></li>
<li><span>04</span><h3>Check before use</h3><p>Fresh export checks are separate from permission to publish source or results.</p></li></ol>
<a href="{base}how-it-works/">How the preview works <span aria-hidden="true">→</span></a></section>
<section class="section start"><p class="eyebrow">Run the preview</p><h2>Begin offline.<br>Choose what comes next.</h2>
<p>The canonical quickstart separates installation and seed-only checks from a live model request.</p>
<a class="button" href="{base}getting-started/">Open the quickstart <span aria-hidden="true">↗</span></a>
<p class="muted">Candidate Python has host access, not a security sandbox. Subscription usage may be unknown; local limits are not hard spending caps.</p></section>
<section class="section closing"><h2>Help make experiments easier to inspect.</h2><p>Read the <a href="{base}roadmap/">roadmap</a>, check the <a href="{base}safety/">scope and limits</a>, or <a href="{base}contributing/">contribute a focused change</a>.</p></section>'''


def build(destination: Path, *, root: Path = ROOT, base: str = "/", example: PreparedExample | None = None, publication: Publication | None = None) -> dict:
    base = base_path(base)
    if publication is not None:
        validate_publication(publication)
        if publication.base != base:
            raise ValueError("Publication and site base paths must match")
    if example is not None:
        validate_example(example)
    if publication is not None and publication.public_example_sha256 != (example.public_identity["payload_sha256"] if example else None):
        raise ValueError("Release configuration must bind the exact publicly approved example or null")
    destination = checked_path(destination, must_exist=False)
    if destination.exists() or destination.is_symlink():
        raise ValueError("Build destination already exists; choose a new directory.")
    if not destination.parent.is_dir() or any(p.is_symlink() for p in destination.parents):
        raise ValueError("Build destination requires an existing non-symlink parent.")
    routes = load_routes(root)
    prefix = base.lstrip("/")
    files = {prefix + "index.html": shell("Evolve code. Show the evidence.", homepage(base), routes, base, publication=publication)}
    inputs = {}
    for row in routes:
        source = read_source(root, row["source"])
        inputs[row["source"]] = hashlib.sha256((root / row["source"]).read_bytes()).hexdigest()
        body = render_markdown(source, row["source"], routes, root, base)
        if row["route"] == "experiments" and example is not None:
            body += example.summary_html
        files[prefix + row["route"] + "/index.html"] = shell(row["title"], '<article class="document">' + body + '</article>', routes, base, row["route"], publication)
    for name in ("site.css", "site.js"):
        files[prefix + "assets/" + name] = read_source(root, "site/assets/" + name)
    files["robots.txt"] = "User-agent: *\nDisallow: /\n"
    if publication is not None:
        files.update(discovery_files(publication, routes))
    for relative in ("site/build.py", "site/examples.py", "site/publication.py", "site/routes.json", "site/requirements.txt", "site/assets/site.css", "site/assets/site.js"):
        read_source(root, relative)
        inputs[relative] = hashlib.sha256((root / relative).read_bytes()).hexdigest()
    if example is not None:
        if example.base != base:
            raise ValueError("Example and site base paths must match")
        for path in example.files:
            relative = PurePosixPath(path)
            if relative.is_absolute() or ".." in relative.parts or not path.startswith(prefix + "examples/"):
                raise ValueError("Unsafe example output path")
        if files.keys() & example.files.keys():
            raise ValueError("Example route collides with site output")
        files.update(example.files)
    manifest = {"schema_version": "1.0", "mode": "release_candidate" if publication else "local_preview", "placeholder_origin": None if publication else PLACEHOLDER_ORIGIN,
                "publication": {"origin": publication.origin, "configuration_sha256": publication.approval_sha256} if publication else None,
                "base_path": base, "input_sha256": inputs, "example": example.public_identity if example else None,
                "output_sha256": {name: hashlib.sha256(data.encode()).hexdigest() for name, data in sorted(files.items())}}
    files["build-manifest.json"] = json.dumps(manifest, indent=2, sort_keys=True) + "\n"
    destination.mkdir(mode=0o700)
    for relative, data in files.items():
        target = destination / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        with target.open("x", encoding="utf-8", newline="\n") as stream:
            stream.write(data)
    return manifest


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--base-path", default="/")
    parser.add_argument("--example-record", type=Path)
    parser.add_argument("--example-sha256")
    parser.add_argument("--approved-by")
    parser.add_argument("--example-receipt", type=Path)
    parser.add_argument("--approve-source-link", action="store_true")
    parser.add_argument("--publication-config", type=Path)
    parser.add_argument("--publication-sha256")
    parser.add_argument("--publication-approved-by")
    parser.add_argument("--publication-receipt", type=Path)
    args = parser.parse_args()
    example = None
    publication = None
    if args.publication_config:
        if not all((args.publication_sha256, args.publication_approved_by, args.publication_receipt)):
            parser.error("Publication input requires exact configuration SHA-256, approver and private receipt.")
        publication_receipt = receipt_destination(args.publication_receipt, args.output)
        if args.example_receipt and publication_receipt == checked_path(args.example_receipt, must_exist=False):
            parser.error("Publication and example receipts must use separate paths.")
        publication = load_publication(args.publication_config, approved_sha256=args.publication_sha256,
                                       approved_by=args.publication_approved_by)
    elif any((args.publication_sha256, args.publication_approved_by, args.publication_receipt)):
        parser.error("Publication approval options require --publication-config.")
    if args.example_record:
        if not all((args.example_sha256, args.approved_by, args.example_receipt)):
            parser.error("Example input requires exact SHA-256, named local reviewer and separate private receipt.")
        receipt_destination(args.example_receipt, args.output)
        example = prepare_example(args.example_record, approved_sha256=args.example_sha256,
                                  approved_by=args.approved_by, base=args.base_path,
                                  approve_source_link=args.approve_source_link)
    elif any((args.example_sha256, args.approved_by, args.example_receipt, args.approve_source_link)):
        parser.error("Example approval options require --example-record.")
    if example is not None:
        write_private_receipt(args.example_receipt, args.output, example.private_receipt)
        print("Private example approval receipt written outside site output; do not publish it.")
    if publication is not None:
        write_private_receipt(args.publication_receipt, args.output, publication.private_receipt)
        print("Private publication receipt written outside output; ownership and deployment were not verified by this build.")
    result = build(args.output, base=args.base_path, example=example, publication=publication)
    print(f"Built {len(result['output_sha256'])} {result['mode']} files. Nothing deployed.")
