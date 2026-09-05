# Bounded secret-scan review

Approved scope: exactly 3,005 new findings from the coordinator's all-files scan.
This review does not exempt files, disable detectors in the baseline, or certify
checksum integrity. No potential secret values are reproduced here.

Classification:

- 3,000 complete 64-character hex values in explicit SHA-256 JSON fields.
- Two `baseline_head` fields resolving locally to Git commit objects:
  `planning/maintainability_pass/refactors/FILE_MATRIX.json:5` and
  `planning/maintainability_pass/OWNERSHIP_MATRIX.json:4`.
- Three synthetic redaction-test findings in `tests/core/test_feedback.py`:
  Secret Keyword at lines 1920 and 1975; Base64 at line 2070. The first two
  define test inputs; assertions at 1930 and 2069 check their absence from
  retained/persisted text. Line 2070 checks absence of the synthetic marker.

The per-file and per-field counts and exact test finding fingerprints are
asserted below. Only new records receive `is_secret: false`. All 2,809 prior
records (including scanner-updated line metadata), paths, settings, and metadata
are preserved structurally. The result contains 5,814 records with LF endings.
Formatting is a mechanical JSON rewrite. Baseline path normalization is not
needed: the scanner loader handles platform paths.

Subsequent configured all-files hook runs found no new secrets and refreshed
line metadata. The hook removed two stale Hex records in
papers/status_claim_inventory.json (original lines 2190 and 2713), leaving
5,812 records including all 3,005 reviewed additions. Detector/filter settings
remain equal to the original committed baseline. This scanner trimming is
separate from the preservation assertions at the initial update below.

## Replay

Run from the alpha worktree under Windows Python 3.12 with detect-secrets 1.5.0.
The script deliberately requires the reviewed pre-update baseline byte hash;
it refuses a changed or already-updated baseline. Replay against that snapshot,
not by rolling back a shared checkout. Omit `--apply` for a dry run.

```bash
/mnt/c/Windows/py.exe -3.12 -c 'import pathlib; s=pathlib.Path("planning/early_alpha/SECRET_REVIEW.md").read_text(); exec(compile(s.split("```python\n",1)[1].split("\n```",1)[0],"<secret-review>","exec"))' --apply
```

This reproduces the exact finding set using the three reported detector types
and existing local filters. Remote verification is omitted in this classification
pass; the baseline settings remain unchanged. This is not the required full
scanner gate. The coordinator stages the baseline and all release files, then
runs the configured all-files hook. No hook, staging, or commit is performed here.
Four exact fingerprint literals below have line-local allowlist comments: one
baseline-file digest and three scanner finding hashes, not credential values.

```python
import collections
import copy
import hashlib
import json
import pathlib
import re
import subprocess
import sys

from detect_secrets.core.secrets_collection import SecretsCollection
from detect_secrets.settings import transient_settings

root = pathlib.Path.cwd()
path = root / ".secrets.baseline"
original = path.read_bytes()
assert hashlib.sha256(original).hexdigest() == "1c01289875dc5dbac1282a80659d9b706c4aa00fdd055ae339e2a5cf39575bf3", "Baseline changed; review again"  # pragma: allowlist secret
baseline = json.loads(original)
assert sum(map(len, baseline["results"].values())) == 2809
known = SecretsCollection.load_from_baseline(baseline)
settings = copy.deepcopy(baseline)
settings["plugins_used"] = [p for p in baseline["plugins_used"]
    if p["name"] in ("HexHighEntropyString", "KeywordDetector", "Base64HighEntropyString")]
# Classification only: these three local detectors need no remote verification.
settings["filters_used"] = [f for f in baseline["filters_used"]
    if not f["path"].endswith("is_ignored_due_to_verification_policies")]
expected = {
    "papers/alphaevolve_tex_proposition_inventory_boundary.json": 1432,
    "papers/alphaevolve_tex_prose_inventory_boundary.json": 558,
    "papers/alphaevolve_tex_math_inventory_boundary.json": 403,
    "papers/alphaevolve_tex_table_cell_inventory_boundary.json": 300,
    "papers/alphaevolve_tex_code_listing_inventory_boundary.json": 215,
    "papers/alphaevolve_tex_source_detail_inventory_boundary.json": 69,
    "papers/documentation_claim_inventory.json": 9,
    "papers/benchmark_coverage_inventory.json": 8,
    "papers/status_claim_inventory.json": 6,
    "tests/core/test_feedback.py": 3,
    "planning/maintainability_pass/refactors/FILE_MATRIX.json": 1,
    "planning/maintainability_pass/OWNERSHIP_MATRIX.json": 1,
}
test_hashes = {
    (1920, "Secret Keyword"): "fb2e6f0314ea2a5462658ef7026f505b2fc06ccc",  # pragma: allowlist secret
    (1975, "Secret Keyword"): "998c0774c46b0e84fb333080dca3a59e591e5b4c",  # pragma: allowlist secret
    (2070, "Base64 High Entropy String"): "2646c0b4bbf0770d52f4715009bffa2ad00b813e",  # pragma: allowlist secret
}
expected_fields = {
    "rendered_text_sha256": 186, "source_text_sha256": 1049,
    "source_quote_sha256": 960, "sha256": 56, "expected_sha256": 5,
    "source_line_sha256": 192, "text_sha256": 488, "command_sha256": 35,
    "begin_command_sha256": 7, "content_sha256": 8, "body_sha256": 4,
    "summary_sha256": 4, "block_sha256": 6,
}
matrix_lines = {
    "planning/maintainability_pass/refactors/FILE_MATRIX.json": 5,
    "planning/maintainability_pass/OWNERSHIP_MATRIX.json": 4,
}
# Windows Git cannot resolve the WSL-style gitdir in the worktree pointer.
gitdir = (root / ".git").read_text().strip().removeprefix("gitdir: ")
if sys.platform == "win32" and gitdir.startswith("/mnt/"):
    gitdir = gitdir[5].upper() + ":/" + gitdir[7:]
snapshots = {}
new = []
totals = collections.Counter()
fields = collections.Counter()
nonhex = set()
commits = 0
with transient_settings(settings):
    for name, count in expected.items():
        source = root / name
        snapshots[name] = source.read_bytes()
        lines = snapshots[name].decode("utf-8").splitlines()
        found = SecretsCollection()
        found.scan_file(name)
        local_name = str(pathlib.Path(name))
        fresh = found.data.get(local_name, set()) - known.data.get(local_name, set())
        assert len(fresh) == count, ("Unexpected finding count", name, len(fresh))
        for hit in fresh:
            totals[hit.type] += 1
            if hit.type != "Hex High Entropy String":
                assert name == "tests/core/test_feedback.py"
                key = (hit.line_number, hit.type)
                assert test_hashes.get(key) == hit.secret_hash, "Unapproved test finding"
                nonhex.add(key)
            else:
                field = json.loads("{" + lines[hit.line_number - 1].strip().rstrip(",") + "}")
                assert len(field) == 1
                key, value = next(iter(field.items()))
                assert value == hit.secret_value, "Finding must equal the complete field"
                if key == "sha256" or key.endswith("_sha256"):
                    assert re.fullmatch("[0-9a-fA-F]{64}", value)
                    fields[key] += 1
                else:
                    assert key == "baseline_head" and matrix_lines.get(name) == hit.line_number
                    assert re.fullmatch("[0-9a-fA-F]{40}", value)
                    kind = subprocess.check_output(
                        ["git", "--git-dir", gitdir, "cat-file", "-t", value],
                        stderr=subprocess.DEVNULL, text=True).strip()
                    assert kind == "commit"
                    commits += 1
            record = hit.json()
            record["is_secret"] = False
            new.append((local_name, record))

assert totals == {"Hex High Entropy String": 3002, "Secret Keyword": 2,
                  "Base64 High Entropy String": 1}
assert fields == expected_fields and sum(fields.values()) == 3000
assert nonhex == set(test_hashes) and commits == 2 and len(new) == 3005
updated = copy.deepcopy(baseline)
for name, record in sorted(new, key=lambda item: (
        item[0], item[1]["line_number"], item[1]["type"], item[1]["hashed_secret"])):
    updated["results"].setdefault(name, []).append(record)
assert sum(map(len, updated["results"].values())) == 5814
assert {k: v for k, v in updated.items() if k != "results"} == {
    k: v for k, v in baseline.items() if k != "results"}
for name, records in baseline["results"].items():
    assert updated["results"][name][:len(records)] == records
# Refuse concurrent scanner/source edits; no hooks or staging are invoked.
assert path.read_bytes() == original, "Concurrent baseline change"
assert all((root / name).read_bytes() == data for name, data in snapshots.items())
output = (json.dumps(updated, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
assert b"\r" not in output
if "--apply" in sys.argv:
    path.write_bytes(output)  # Authorized bulk mechanical JSON rewrite.
    assert path.read_bytes() == output
print(json.dumps({"mode": "applied" if "--apply" in sys.argv else "dry-run",
    "existing_preserved": 2809, "added_reviewed_false": 3005, "total": 5814,
    "explicit_sha256": 3000, "commit_references": 2, "synthetic_tests": 3,
    "output_sha256": hashlib.sha256(output).hexdigest()}, sort_keys=True))
```

## Single-process line metadata refresh

The coordinator subsequently supplied a 5,812-row baseline after hook passes.
This operation preserves that exact set; it does not restore removed rows from
the earlier 5,814-row snapshot. It scans each baseline-owned file once with
current baseline detector/filter settings. Remote verification is prevented;
the existing verification filter treats connection failures as unverified.
Only matching filepath/type/finding-hash records can receive a line-number
change. Settings, paths, row order, classifications, and all other fields stay
unchanged. Unmatched rows remain untouched; unbaselined findings are reported
without adding entries. Neither category expands this metadata-only operation.

Duplicate occurrences are detected before scanner collection deduplication.
For those identities, the selected location is the first scanner occurrence,
matching the hook's set insertion behavior. The output reports duplicate counts
and changed line locations without printing potential secret values.

The following script is the exact metadata operation (run from this worktree
with Windows Python 3.12). It performs one LF-only mechanical JSON write after
all assertions pass; no staging, hook, or commit is invoked.

Execution evidence: initial terminal session 48981 exited with assertion failure
before writing because the first guard rejected unmatched/unbaselined findings.
The revised metadata-only pass in session 52603 completed with exit code 0:
201 files scanned, 5,809 exact matches, all 5,812 rows preserved, and 436 line
updates. Updates by file: benchmark_coverage_inventory.json 358;
documentation_claim_inventory.json 50; tests/core/test_feedback.py 20;
tests/core/test_jsonl.py 7; tests/core/test_provenance.py 1. No other row fields
or settings changed. The previously reported readme/evaluator locations needed
no further update in the baseline snapshot used by this pass.

There were 745 identities with multiple scanner locations; the first occurrence
was used consistently with collection behavior. Three unmatched existing hex
records in papers/documentation_claim_inventory.json (stored lines 6592, 6633,
6651) were retained unchanged. Two unbaselined Slack Token detections in
tests/core/test_redaction.py at 119 and 125 were not added. These were observed
with remote verification prevented; they do not establish the hook's result
under its normal verification behavior. No further classification or inventory
repair is included. The coordinator owns the final staged all-files gate.

```python
import collections
import copy
import hashlib
import json
import pathlib
import requests
from detect_secrets.core import scan
from detect_secrets.settings import transient_settings

path = pathlib.Path(".secrets.baseline")
original = path.read_bytes()
before = json.loads(original)
assert sum(map(len, before["results"].values())) == 5812
after = copy.deepcopy(before)
changes, duplicates, unmatched, unexpected = [], [], [], []
snapshots = {}
matched = 0

def offline_request(*args, **kwargs):
    # The existing verification-policy filter handles this as UNVERIFIED.
    raise requests.exceptions.ConnectionError("Offline metadata refresh")

request = requests.sessions.Session.request
requests.sessions.Session.request = offline_request
try:
    with transient_settings(before):
        for index, (name, records) in enumerate(after["results"].items(), 1):
            source = pathlib.Path(name.replace("\\", "/"))
            snapshots[name] = source.read_bytes()
            owned = {}
            for record in records:
                assert record["filename"].replace("\\", "/") == source.as_posix()
                key = (record["type"], record["hashed_secret"])
                assert key not in owned, "Duplicate baseline identity; no write"
                owned[key] = record
            found = {}
            # One scan per owned file, before collection set deduplication.
            for hit in scan.scan_file(str(source)):
                key = (hit.type, hit.secret_hash)
                if key in owned:
                    found.setdefault(key, []).append(hit.line_number)
                else:
                    unexpected.append((source.as_posix(), hit.line_number, hit.type))
            for key, record in owned.items():
                lines = found.get(key, [])
                if not lines:
                    unmatched.append((source.as_posix(), record["line_number"], record["type"]))
                    continue
                matched += 1
                # Match SecretsCollection.scan_file: the first equal hit wins
                # when added to its set. Detect and report later occurrences.
                chosen = lines[0]
                distinct = sorted(set(lines))
                if len(distinct) > 1:
                    duplicates.append((source.as_posix(), record["type"], distinct, chosen))
                if record.get("line_number") and record["line_number"] != chosen:
                    changes.append((source.as_posix(), record["line_number"], chosen))
                    record["line_number"] = chosen
            if index % 25 == 0:
                print("scanned_files", index, flush=True)
finally:
    requests.sessions.Session.request = request

print("unmatched", unmatched, flush=True)
print("unexpected", unexpected, flush=True)
print("duplicate_identities", len(duplicates),
      "duplicate_files", dict(collections.Counter(row[0] for row in duplicates)), flush=True)
print("changes_by_file", dict(collections.Counter(row[0] for row in changes)), flush=True)
assert matched + len(unmatched) == 5812
assert set(after) == set(before)
assert {k: v for k, v in after.items() if k != "results"} == {
    k: v for k, v in before.items() if k != "results"}
assert list(after["results"]) == list(before["results"])
for name, old in before["results"].items():
    new = after["results"][name]
    assert len(old) == len(new)
    for a, b in zip(old, new):
        assert {k: v for k, v in a.items() if k != "line_number"} == {
            k: v for k, v in b.items() if k != "line_number"}
assert path.read_bytes() == original, "Concurrent baseline edit; no write"
assert all(pathlib.Path(name.replace("\\", "/")).read_bytes() == data
           for name, data in snapshots.items()), "Concurrent source edit; no write"
output = (json.dumps(after, indent=2, ensure_ascii=True) + "\n").encode("utf-8")
assert b"\r" not in output
path.write_bytes(output)
assert path.read_bytes() == output
print("metadata_refresh", json.dumps({
    "files": len(snapshots), "rows_preserved": 5812, "matched": matched,
    "line_updates": len(changes), "duplicate_identities": len(duplicates),
    "input_sha256": hashlib.sha256(original).hexdigest(),
    "output_sha256": hashlib.sha256(output).hexdigest()}), flush=True)

```
