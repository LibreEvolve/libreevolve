# Engineering-preview development

## Prerequisites

Use the [quickstart](alpha-quickstart.md) for the canonical clone, Python
version, `.venv`, editable `[dev]` install and offline command path. This page
covers checks for contributors after that environment is installed.

## Offline checks

Use Python 3.12 for the documented reference environment. Run focused tests
while iterating, then the retained suite from the repository root:

```bash
.venv/bin/python -m pytest tests/ --tb=short
.venv/bin/python -m build --wheel --sdist
```

On Windows PowerShell, use the matching executable explicitly:

```powershell
& .\.venv\Scripts\python.exe -m pytest tests/ --tb=short
& .\.venv\Scripts\python.exe -m build --wheel --sdist
```

These checks use local fixtures, fake provider processes or seed-only evaluation.
They must not load API-key files or initiate a model request. A green offline
test is not live model, hosted CI, browser, deployment or external-usability
evidence.

## What to test when behavior changes

Preserve tests for cancellation, invalid model output, evaluator timeout,
redaction, partial persistence, held-out verification, conflicting export
sources and existing-output protection when changing their dependency paths.
For docs or CLI changes, also check:

- local Markdown links and the support matrix;
- the `alpha init`, `alpha doctor`, `run`, `show`, `alpha report` and
  `alpha export` signatures against `--help`;
- seed-only versus live-provider wording;
- source/history mismatch and output-collision behavior; and
- the distinction between local reports and fresh candidate verification.

Do not treat a mocked provider as live end-to-end evidence. Do not alter the
Codex OAuth product lane, evaluator fitness, budgets, cancellation behavior or
holdout boundary as collateral to documentation work.

## Distribution checks

Build both a wheel and source archive. Install the wheel into a fresh
environment outside the checkout and follow the offline seed-only path in the
[quickstart](alpha-quickstart.md), including `pip check`, inspection, report
and verified export. Use new output names so collision protection is exercised.

Record exact source and distribution identities with:

```bash
.venv/bin/python -m libreevolve.tools.release_artifact_provenance
```

The command requires both a wheel and sdist in `dist/` and writes
`dist/release_artifact_provenance.json` by default. The provenance record is
build evidence, not a release or registry-publication claim.

## Repository and CI boundaries

Preserve unrelated changes in a dirty checkout. Do not reset, clean, stash,
broad-stage or overwrite another contributor's work. Use an isolated worktree
for scoped changes and stage only the paths that belong to that change.

GitHub workflows run on pull requests and pushes, with manual dispatch available
for additional verification. The offline test matrix covers Python 3.11 and 3.12
on Linux, Windows, and macOS. The installed-wheel workflow exercises Windows
onboarding, seed-only evaluation, reporting, and independently verified export
outside the checkout. These checks do not make live model requests. A local
pass does not mean hosted CI ran or passed; inspect the checks for the exact
candidate commit. Account-billing changes require separate authorization.
