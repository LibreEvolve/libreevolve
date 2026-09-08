# AGENTS.md

## Engineering-preview scope

This branch supports installation, bin-packing initialization and preflight,
bounded Codex OAuth Luna/high optimization, progress and cancellation,
saved-result inspection, HTML reporting, and independently validated export.
Research features and their history belong on `experimental`.
Keep the product labeled **engineering preview**.

## Development

Use Python 3.12; on this Windows machine use `py -3.12`, not `python`.
The implementation uses dataclasses, Click, PyYAML, NumPy and scikit-learn.
Run the retained offline suite:

```bash
py -3.12 -m pytest tests/ --tb=short
py -3.12 -m build --wheel --sdist
```

See [development](docs/development.md) and
[release checks](docs/release-checklist.md). Never make model requests as an
incidental test. Do not restore automatic CI triggers or repair account billing
without authorization.

## Runtime ownership and safeguards

- `core/loop.py` coordinates PromptSampler, the evaluator, ProgramDatabase
  and the bounded LLM adapter. Shared archive and accounting mutations are ordered.
- `llm/codex_cli.py` owns the OAuth subprocess and local process cancellation.
  The validated lane is `gpt-5.6-luna` with `high` reasoning.
- `alpha_report.py` owns reporting and verified export;
  `alpha_verify_worker.py` verifies candidates in a fresh local subprocess.
- `runs/` is ignored. Keep `manifest.json`, history, failure/quarantine JSONL
  streams, `archive_events.jsonl`, `llm_calls.jsonl`, `best_workspace/`
  and evaluator evidence consistent. See [artifact details](docs/run-artifacts.md).
- VALID_THRESHOLD = 0.0 is the pre-admission eligibility gate. A valid finite
  score at or above zero reaches ProgramDatabase.admit(), but MAP-Elites
  retention can still reject it with reason="not_improving_cell".
  Admission and sampling_eligible are distinct.
- Preserve original cancellation exceptions even when saving partial state fails.
  A fresh candidate check, not old metadata, is export authority.
- `config.seed` uses run-local random state, not process-global reseeding.
- Local subprocess execution is not a security sandbox. Keep held-out cases
  outside the editable workspace and out of prompts and stopping decisions.
- Subscription charges may be unknown; do not claim dollar caps, stopped remote
  billing, external usability, or fresh live evidence from offline tests.

Preserve dirty shared checkouts and unrelated work. Use isolated worktrees,
explicit staging, and exact-head verification for Git changes.
