# Engineering-preview development

Use Python 3.12. On Windows:

```powershell
py -3.12 -m venv .venv
.venv\Scripts\python.exe -m pip install -e ".[dev]"
.venv\Scripts\python.exe -m pytest tests/ --tb=short
.venv\Scripts\python.exe -m build --wheel --sdist
```

On Linux/WSL, create the environment with `python3.12` and use
`.venv/bin/python`. Run tests from the repository root.

Tests use fake provider processes or seed-only evaluation. Do not load API-key
files or initiate model calls during ordinary verification. A real Codex run
requires explicit authorization for subscription use.

Test cancellation, invalid model output, evaluator timeout, redaction, partial
persistence, held-out verification, conflicting export sources and existing
output protection when changing their dependency paths. Do not treat a mocked
provider as live end-to-end evidence.

Build both wheel and sdist. Install the wheel into a fresh environment, change
directory outside the checkout, and exercise the seed-only flow in the
[quickstart](alpha-quickstart.md), including report and verified export.
Run `pip check` in that environment.

GitHub workflows run on pull requests and pushes, with manual dispatch available
for additional verification. The offline test matrix covers Python 3.11 and 3.12
on Linux, Windows, and macOS. The installed-wheel workflow exercises Windows
onboarding, seed-only evaluation, reporting, and independently verified export
outside the checkout. These checks do not make live model requests. A local
pass does not mean hosted CI ran or passed; inspect the checks for the exact
candidate commit. Account-billing changes require separate authorization.

Preserve unrelated changes. Do not reset, clean or stash a shared checkout.
