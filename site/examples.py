"""Read-only website projection of an explicitly approved W06 frozen record."""

from dataclasses import dataclass
import html
import json
import os
from pathlib import Path
import re

from libreevolve.alpha_share_io import PUBLIC_FILENAMES, checked_path, load_record
from libreevolve.alpha_share_record import payload_sha256
from libreevolve.alpha_share_render import render_public


@dataclass(frozen=True)
class PreparedExample:
    base: str
    files: dict[str, str]
    summary_html: str
    public_identity: dict
    private_receipt: dict


def prepare_example(path: Path, *, approved_sha256: str, approved_by: str,
                    base: str = "/", approve_source_link: bool = False) -> PreparedExample:
    if not re.fullmatch(r"/(?:[a-zA-Z0-9_-]+/)*", base):
        raise ValueError("Invalid site base path")
    record = load_record(path)
    return project_example(record, approved_sha256=approved_sha256, approved_by=approved_by,
                           base=base, approve_source_link=approve_source_link)


def project_example(record: dict, *, approved_sha256: str, approved_by: str,
                    base: str, approve_source_link: bool) -> PreparedExample:
    files, receipt = render_public(record, approved_sha256=approved_sha256,
                                   approved_by=approved_by, approve_source_link=approve_source_link)
    if set(files) != PUBLIC_FILENAMES:
        raise ValueError("Unexpected W06 public-file set")
    route = "examples/" + record["public_result_id"] + "/"
    synthetic = record["evidence_class"] == "synthetic_fixture"
    label = "SYNTHETIC FIXTURE — NOT A REAL EXPERIMENT" if synthetic else "Frozen local checks — not a live-model claim"
    action = "Inspect synthetic fixture" if synthetic else "Inspect frozen local checks"
    summary = f'<section aria-label="Included frozen record"><h2>{html.escape(label)}</h2><p><a href="{base}{route}">{action}</a></p><p>This record was explicitly selected for this local build. Rendering does not independently verify it or authorize publication.</p></section>'
    navigation = f'<nav aria-label="Evidence navigation"><a href="{base}experiments/">Back to experiments</a> · <a href="result.txt">Text</a> · <a href="result.json">Frozen JSON</a> · <a href="card.svg">Plain result card</a></nav>'
    page = files["index.html"]
    page = page.replace("</head>", '<meta name="robots" content="noindex,nofollow"></head>', 1)
    page = page.replace("<main>", "<main>" + navigation, 1)
    files = {**files, "index.html": page}
    return PreparedExample(
        base=base,
        files={base.lstrip("/") + route + name: content for name, content in files.items()},
        summary_html=summary,
        public_identity={"public_result_id": record["public_result_id"], "evidence_class": record["evidence_class"],
                         "payload_sha256": payload_sha256(record)},
        private_receipt=receipt,
    )


def validate_example(example: PreparedExample) -> None:
    """Reconstruct the exact public projection; reject modified bundles before writes."""
    try:
        route = example.base.lstrip("/") + "examples/" + example.public_identity["public_result_id"] + "/"
        record = json.loads(example.files[route + "result.json"])
        receipt = example.private_receipt
        expected = project_example(record, approved_sha256=receipt["payload_sha256"],
                                   approved_by=receipt["approved_by"], base=example.base,
                                   approve_source_link=receipt["source_link_approved"])
        if example != expected:
            raise ValueError("Example differs from its exact reviewed projection")
    except (KeyError, TypeError, json.JSONDecodeError) as exc:
        raise ValueError("Malformed example projection") from exc


def receipt_destination(path: Path, output: Path) -> Path:
    target = checked_path(path, must_exist=False)
    public = checked_path(output, must_exist=False)
    if target.exists() or target.is_relative_to(public):
        raise ValueError("Private receipt must be new and outside the site output")
    return target


def write_private_receipt(path: Path, output: Path, receipt: dict) -> None:
    target = receipt_destination(path, output)
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(target, flags, 0o600)
    with os.fdopen(descriptor, "w", encoding="utf-8") as stream:
        json.dump(receipt, stream, sort_keys=True)
        stream.write("\n")
