# Development

This document covers the local contributor workflow for LibreEvolve as it exists
today.

## Python version

The project metadata requires Python 3.11+, and repository instructions for this
machine prefer `py -3.12`.

Examples in this repo should generally use:

```bash
py -3.12 -m ...
```

If `py -3.12` is not installed locally, use another supported interpreter, but
be aware that the project has been written and tested with 3.11+ semantics in
mind.

## Setup

```bash
py -3.12 -m pip install -e ".[dev]"
py -3.12 -m pre_commit install
```

The main runtime dependencies are:

- `numpy`
- `scikit-learn`
- `anthropic`
- `openai`
- `ollama`
- `pyyaml`
- `click`
- `python-dotenv`
- `packaging`
- `pypdf`

Development dependencies include:

- `pytest`
- `pytest-mock`
- `pre-commit`
- `detect-secrets`

## Environment Provenance Scope

Run manifests record a bounded runtime environment summary, not a full
development environment snapshot. The retained `pyproject.toml` package fields
are `project.name`, `project.version`, `project.requires-python`,
license, authors/maintainers, keywords, classifiers, project URLs, optional
dependency groups, scripts, arbitrary entry-point groups,
`build-system.build-backend`, and `build-system.requires`, plus installed
versions for declared runtime dependencies. It also records bounded installed
distribution name/version, `WHEEL`, `direct_url.json`, `INSTALLER`, and
hash-only `RECORD` metadata, known project-root lockfile hashes, bounded
`pip freeze --all` and `pip config list` evidence, NumPy config summaries,
provider SDK versions, and bounded accelerator hints. Arbitrary project
metadata, dev/test tool runtime state beyond declared optional groups, complete
private package-source interpretation, full transitive dependency
source/options, and release-artifact verification are outside the current
provenance contract.

## Environment variables

Create a `.env` file in the repository root for provider configuration:

```text
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
OLLAMA_HOST=http://localhost:11434
```

The `run` command loads `.env` during run setup with `override=True`, before
backend preflight. Values in the repository `.env` can replace same-named
variables already present in the parent process for evolution runs. Importing
`libreevolve.cli` and running `libreevolve show` do not load `.env`.

## Common commands

Run unit tests:

```bash
py -3.12 -m pytest tests/ -m "not integration" --tb=short
```

Run integration tests:

```bash
py -3.12 -m pytest tests/integration/ -m integration
```

Run the example problems:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "openai:<openai-model-id>"
py -3.12 -m libreevolve run libreevolve/problems/examples/circle_packing --max-generations 10 --backends "anthropic:<anthropic-model-id>"
py -3.12 -m libreevolve show runs/hello_world
```

Replace placeholder backend model ids with currently available provider/account
model ids before running.

Run pre-commit checks:

```bash
py -3.12 -m pre_commit run --all-files
```

The secret scan uses `.secrets.baseline`. If you intentionally add synthetic
provider-token strings for redaction tests or TODO evidence, prefer a narrow
test-fixture marker such as `# pragma: allowlist secret` where appropriate, or
regenerate the baseline and stage the resulting `.secrets.baseline` change. An
unstaged baseline update is a validation failure from the secret-scan workflow,
not a provider/API failure.

Check for whitespace problems before committing:

```bash
git diff --check
```

## CI coverage boundary

The GitHub Actions `Tests` workflow runs on manual dispatch and on path-scoped
`push` / `pull_request` events for source, tests, docs, TODO ledgers,
agent-facing instructions, workflow config, and paper-index files. It runs the
secret scan, non-integration unit tests on Python 3.11 and 3.12, and optional
integration tests when an Anthropic API key is available. A green `Tests` badge
means the last completed workflow passed for the paths that triggered it; local
commands are still the fastest validation path while working before a push or
PR. CI also runs a dedicated paper/docs job that validates the committed paper
manifest and focused docs/paper boundary tests; it does not run
`--require-local-pdfs` because the PDF cache is intentionally gitignored. The
release-artifact smoke job builds one wheel and one sdist, installs the wheel
into an isolated virtual environment, checks representative problem-data files
inside the wheel, and runs CLI help checks; it is not a complete package-data,
index-publish, or release-provenance certification.

For docs-only changes, run at least:

```bash
git diff --check
py -3.12 -m pre_commit run --all-files
py -3.12 -m pytest tests/ -m "not integration" --tb=short
```

For `papers/` or paper-index changes, also validate the local paper index:

- run `py -3.12 -m libreevolve.tools.paper_manifest --rehydrate` on a fresh
  checkout to restore the ignored local PDF cache from the committed manifests;
  the command downloads manifest URLs, verifies byte counts and SHA-256 hashes
  before installing files, and reports network or integrity failures explicitly
- run `py -3.12 -m libreevolve.tools.paper_manifest` to validate committed
  CSV/JSON schema, count agreement, and canonical SHA-256 format
- run `py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs` when
  the ignored local PDF cache is present and should be checked for existence,
  regular-file/link boundaries, `%PDF-` header shape, lightweight `pypdf` page
  readability, byte counts, and streaming digest equality
- use `--json` when auditing per-paper historical download status versus
  current local presence and Git-tracked status
- confirm paper status rows distinguish implemented behavior, inspired-only
  behavior, background-only papers, and benchmark coverage decisions

## Repository conventions

### Problem authoring

- keep seed programs intentionally improvable
- make validators defensive
- return the primary metric and `is_valid`

### Mutation output

- `diff` mode expects SEARCH/REPLACE edits
- `full` mode accepts full-code, full-block, or file-section replacements
- workspace topology commands use `<<<FILE DELETE ... >>>FILE`,
  `<<<FILE MOVE old -> new ... >>>FILE`, or `<<<FILE PRIMARY ... >>>FILE`
- the diff engine strips one outer markdown fence wrapper, but exact search matching still matters
- comments or formatting drift in the diff can break matching

### Logging

- `runs/` is gitignored for normal run output
- committed example histories live under `examples/runs/`
- JSONL histories are strict finite JSON but best-effort append logs; after a
  crash, inspect or repair any partial final line before treating a run history
  as complete

### Plugin design

- plugins are synchronous and lightweight
- prompt-building hooks should return plain text blocks
- score-changing hooks should be explicit about whether they transform or merely
  annotate evaluation results

## Suggested contributor docs to read first

1. [Architecture](./architecture.md)
2. [Problem Format](./problem-format.md)
3. [Configuration](./configuration.md)
4. [Plugins](./plugins.md)
