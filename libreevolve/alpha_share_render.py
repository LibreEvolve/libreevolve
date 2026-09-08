"""Deterministic public text/HTML/SVG from approved frozen data; no I/O."""

from __future__ import annotations

import html

from libreevolve.alpha_share_metrics import compare_metrics
from libreevolve.alpha_share_record import approve_record, canonical_bytes


_SCOPE = "Named finite checks are not universal correctness, security certification or optimality."
_QUALITY = "Quality is not accuracy or speed. Compare only within the same corpus and split."
_USAGE = "Missing usage is unknown, not zero cost. Recorded cost is not provider billing."
_REASONS = {
    "candidate_missing": "No candidate result is available.",
    "candidate_invalid": "The candidate did not pass the named checks.",
    "candidate_validity_unknown": "Candidate validity is unknown.",
    "baseline_missing": "No baseline result is available.",
    "baseline_not_valid": "The baseline has not passed the named checks.",
    "corpus_or_split_mismatch": "The corpora or splits differ; no comparison is made.",
    "case_count_unknown": "The number of checked cases is unknown.",
    "case_count_mismatch": "The numbers of checked cases differ.",
    "empty_corpus": "An empty corpus has no meaningful reduction percentage.",
    "bin_count_unknown": "A required bin count is unknown.",
    "zero_baseline": "A zero-bin baseline has no reduction percentage.",
    "inconsistent_zero_candidate": "The zero-bin candidate conflicts with the positive baseline.",
    "valid_same_corpus": "Both solutions passed checks on the same corpus and split.",
}


def _display(value):
    if value is None:
        return "unknown"
    if type(value) is bool:
        return "passed" if value else "failed"
    if type(value) is float:
        return format(value, ".8g")
    return str(value)


def render_public(value: object, *, approved_sha256: str, approved_by: str,
                  approve_source_link: bool = False) -> tuple[dict[str, str], dict]:
    """Return four public files and a SEPARATE PRIVATE operator receipt.

    This does not write, publish, independently verify or authenticate anything.
    The caller must preserve the fixed public-file allowlist and collision guards.
    """
    r, receipt = approve_record(value, approved_sha256=approved_sha256,
                               approved_by=approved_by, approve_source_link=approve_source_link)
    comparison = compare_metrics(r["baseline"], r["candidate"])
    reason = _REASONS[comparison["comparison_reason"]]
    evidence = ("SYNTHETIC FIXTURE — NOT A REAL EXPERIMENT" if r["evidence_class"] == "synthetic_fixture"
                else "Observed local checks — operator supplied")
    lines = ["LibreEvolve", "Engineering preview", evidence,
             f"Public result: {r['public_result_id']}", f"Run status: {r['run_status']}",
             f"Candidate outcome: {comparison['outcome']}",
             f"Bin reduction (%): {_display(comparison['bin_reduction_percent'])}",
             f"Comparison: {reason}"]
    lines.extend([f"Selected source: {r['selected_source']}", f"Candidate retention: {r['candidate_retention']}"])
    rows = []
    for label in ("baseline", "candidate"):
        metric = r[label]
        if metric is None:
            rows.append([label, "unknown", "unknown", "unknown", "unknown"])
            lines.append(f"{label}: unavailable")
            continue
        # Invalid placeholders must not look like a zero-bin solution.
        bins = _display(metric["total_bins"]) if metric["valid"] is True else "not valid / unknown"
        quality = _display(metric["quality"]) if metric["valid"] is True else "not valid / unknown"
        rows.append([label, metric["split"], _display(metric["valid"]), bins, quality])
        lines.extend([f"{label}: split={metric['split']}; validity={_display(metric['valid'])}; bins={bins}; quality={quality}",
                      f"{label} corpus: {metric['corpus_id']}; SHA-256={metric['corpus_sha256']}; cases={_display(metric['case_count'])}"])
    lines.extend(f"Check: {c['name']} / {c['split']} / {c['status']}" for c in r["checks"])
    lines.extend([f"Observed calls: {_display(r['observed_activity']['calls'])}",
                  f"Elapsed seconds: {_display(r['observed_activity']['elapsed_seconds'])}",
                  f"Usage status: {r['usage']['status']}", f"Tokens: {_display(r['usage']['tokens'])}",
                  f"Recorded cost USD: {_display(r['usage']['cost_usd'])}"])
    lines.extend(f"{key}: {_display(value)}" for key, value in r["public_provenance"].items())
    lines.extend([_SCOPE, _QUALITY, _USAGE, *r["limitations"]])
    if r["approved_source_url"] is not None:
        lines.append(f"Separately approved source: {r['approved_source_url']}")
    escape = lambda value: html.escape(str(value), quote=True)
    table = "".join("<tr>" + "".join(f"<{tag}" + (' scope="row"' if tag == 'th' else '') + f">{escape(cell)}</{tag}>" for tag, cell in
                                    zip(("th", "td", "td", "td", "td"), row)) + "</tr>" for row in rows)
    source = (f'<p><a href="{escape(r["approved_source_url"])}" rel="noreferrer">Separately approved source</a></p>'
              if r["approved_source_url"] else "")
    css = """html{color-scheme:light dark}body{font:1rem/1.6 system-ui,sans-serif;margin:0;background:#fff;color:#17231c}
main{max-width:68rem;margin:auto;padding:2rem 1.25rem}h1{font-size:2.5rem;margin:0}h2{font-size:1.3rem}
header{border-bottom:3px solid #007a3d;padding-bottom:1rem}section{margin-top:2rem}table{border-collapse:collapse;width:100%}
th,td{text-align:left;padding:.65rem;border-bottom:1px solid #7c8d82;white-space:nowrap}pre{white-space:pre-wrap;overflow-wrap:anywhere;font:inherit}
a{color:#007a3d}a:focus-visible{outline:3px solid currentColor;outline-offset:4px}
@media(prefers-color-scheme:dark){body{background:#0d1117;color:#e6edf3}a{color:#80e6a0}header{border-color:#80e6a0}}
@media(max-width:35rem){main{padding:1rem}.table-scroll{overflow-x:auto}table{min-width:30rem}}"""
    page = ('<!doctype html><html lang="en"><head><meta charset="utf-8">'
            '<meta name="viewport" content="width=device-width,initial-scale=1">'
            '<meta http-equiv="Content-Security-Policy" content="default-src \'none\'; style-src \'unsafe-inline\'; base-uri \'none\'; form-action \'none\'">'
            f'<title>LibreEvolve — {escape(r["public_result_id"])}</title><style>{css}</style></head>'
            f'<body><main><header><h1>LibreEvolve</h1><p>Engineering preview</p><p>{escape(evidence)}</p></header>'
            f'<section><h2>Outcome</h2><p>Run: {escape(r["run_status"])}. Candidate: {escape(comparison["outcome"])}.</p>'
            f'<p>Bin reduction (%): {escape(_display(comparison["bin_reduction_percent"]))}. {escape(reason)}</p></section>'
            '<section><h2>Same-corpus evidence</h2><div class="table-scroll" tabindex="0" role="region" aria-label="Metric comparison">'
            '<table><caption>Validity is required; incompatible data has no comparison.</caption><thead><tr>'
            '<th scope="col">Program</th><th scope="col">Split</th><th scope="col">Validity</th><th scope="col">Bins</th><th scope="col">Quality</th>'
            f'</tr></thead><tbody>{table}</tbody></table></div></section><section><h2>Evidence and limitations</h2>'
            f'<pre>{escape(chr(10).join(lines[3:]))}</pre>{source}</section></main></body></html>')
    # A fixed plain functional layout; no generated artwork, scripts or resources.
    card_lines = ["LibreEvolve · engineering preview", evidence,
                  f"Run: {r['run_status']} | Candidate: {comparison['outcome']}",
                  f"Source: {r['selected_source']} | Retention: {r['candidate_retention'].replace('_', ' ')}",
                  f"Bin reduction (%): {_display(comparison['bin_reduction_percent'])}",
                  f"Reason: {reason}",
                  f"Usage: {r['usage']['status']} | cost USD: {_display(r['usage']['cost_usd'])}",
                  "Finite checks only. Read the accompanying evidence and limitations."]
    svg = ('<svg xmlns="http://www.w3.org/2000/svg" width="1200" height="480" viewBox="0 0 1200 480" role="img" aria-labelledby="title desc">'
           f'<title id="title">LibreEvolve result: {escape(comparison["outcome"])}</title><desc id="desc">{escape(". ".join(card_lines))}</desc>'
           '<rect width="1200" height="480" fill="#0d1117"/>')
    svg += "".join(f'<text x="40" y="{60 + index * 55}" fill="#e6edf3" font-family="sans-serif" font-size="24">{escape(line)}</text>'
                   for index, line in enumerate(card_lines)) + '</svg>'
    return {"index.html": page, "card.svg": svg, "result.txt": "\n".join(lines) + "\n",
            "result.json": canonical_bytes(r).decode("utf-8") + "\n"}, receipt
