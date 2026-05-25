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
- `pypdf`

Development dependencies include:

- `pytest`
- `pytest-mock`
- `pre-commit`
- `detect-secrets`

## Environment variables

Create a `.env` file in the repository root for provider configuration:

```text
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
OLLAMA_HOST=http://localhost:11434
```

The CLI loads `.env` with `override=True`.

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
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends openai:gpt-4o-mini
py -3.12 -m libreevolve run libreevolve/problems/examples/circle_packing --max-generations 10 --backends anthropic:claude-sonnet-4-6
py -3.12 -m libreevolve show runs/hello_world
```

Run pre-commit checks:

```bash
py -3.12 -m pre_commit run --all-files
```

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
- the diff engine strips markdown fences, but exact search matching still matters
- comments or formatting drift in the diff can break matching

### Logging

- `runs/` is gitignored for normal run output
- committed example histories live under `examples/runs/`

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
