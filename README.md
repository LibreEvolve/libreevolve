# LibreEvolve

LibreEvolve is a Python research workbench for LLM-guided evolutionary program
discovery. Given a problem directory, it evaluates one or more seed programs,
asks configured LLM backends to propose code mutations, evaluates the resulting
candidates, and keeps retained programs in a small quality-diversity archive.

The project is inspired by AlphaEvolve, Karpathy's `autoresearch`, MAP-Elites,
and recent work on LLM-guided program search. It is an independent project and
is not affiliated with or endorsed by Google DeepMind or the authors of the
cited papers.

## Status

This is an alpha-stage research codebase. It is useful for local experiments and
for studying implementation boundaries, but it is not a production optimizer and
not a full AlphaEvolve reproduction.

This README is the practical entry point. The detailed implementation and
absence-boundary ledger lives in [docs/status.md](docs/status.md), paper-source
evidence lives in [papers/README.md](papers/README.md), and active backlog items
live under [docs/todo/](docs/todo/).

Implemented today:

- Python-primary candidate workspaces and seed programs.
- SEARCH/REPLACE diff mutations using the AlphaEvolve fence format, plus
  configurable full-code replacement mode.
- OpenAI, Anthropic, and Ollama backend adapters with heuristic UCB-style
  backend selection.
- Synchronous MAP-Elites and island archives, with five islands by default.
- Local subprocess evaluation with staged validator support.
- Optional critique, feedback, and plugin hooks.
- Run artifacts under `runs/`, including manifests, histories, prompts,
  failures, best candidates, evaluator artifacts, and plugin artifacts.

Important limits:

- Evaluators run in local subprocesses, not hardened security sandboxes.
- The controller, archive, migration, and evaluator flow are local and
  synchronous, not a distributed asynchronous AlphaEvolve-style service.
- Built-in provider adapters are OpenAI, Anthropic, and Ollama; Google/Gemini
  provider parity remains an explicit absence boundary.
- Backend selection is a local heuristic inspired by UCB-style routing, not a
  finite-time-regret UCB1 reproduction.
- MAP-Elites support is a local quality-diversity archive, not a paper-faithful
  illumination study with full map exports, coverage/reliability/precision
  reports, or domain reproductions.
- The examples are smoke fixtures and small demos unless a fixture documents
  stronger benchmark evidence.
- Systems-result schemas and readiness sidecars are report contracts only; they
  do not yet emit real scheduling, Pallas/kernel, compiler, or hardware fixture
  runs, deployment measurements, expert confirmations, or domain-specific
  result artifacts.
- Kernel report contracts do not yet prove AlphaEvolve-style Pallas/Gemini
  input-shape corpus provenance, deterministic train/eval split hashes, real
  TPU runtime artifacts, expert-baseline tiling heuristic identity, tiling-only
  candidate boundaries, unchanged-operation correctness, engineering-effort
  calibration, or production/workflow adoption.
- Pallas workflow documentation does not yet prove AlphaEvolve-style automation
  of search-based autotuning or manual tiling-heuristic work: baseline workflow
  class, retuning burden, manual review effort, hardware-expertise assumptions,
  and model-developer ergonomics remain active code and paper TODOs.
- Gemini self-training wording remains bounded: the docs do not yet prove that
  a deployed Pallas kernel optimization affected the same Gemini-family
  training workload that powered AlphaEvolve, nor before/after training metrics,
  rollout state, team-velocity evidence, or rollback/safety records.
- The docs do not yet reproduce AlphaEvolve Figure 6 or Figure 7 exhibits:
  scheduling heuristic source/heatmap provenance and Pallas tiling-problem
  diagram/source-data/render hashes remain active code and paper TODOs.
- Paper-result reproduction, benchmark-scale claims, release packaging, and
  broader CI/platform guarantees remain tracked in `docs/status.md`,
  `papers/README.md`, `ROADMAP.md`, and `docs/todo/` rather than promised here.

## Install

Use Python 3.11 or newer. On this Windows machine, use `py -3.12`.

```bash
py -3.12 -m pip install -e ".[dev]"
```

Create a `.env` file at the project root for provider keys you plan to use:

```dotenv
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_HOST=http://localhost:11434
```

`.env` is loaded for `libreevolve run` with `override=True`. Do not commit API
keys.

## Quick Start

First verify the CLI and artifact writer without making any provider calls:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --run-name readme_smoke_sorting --max-llm-calls 0 --overwrite
py -3.12 -m libreevolve show runs/readme_smoke_sorting
```

That command evaluates the bundled sorting seed, writes the normal run
artifacts, and stops before constructing LLM providers. It is a smoke check, not
an evolution run.

To run evolution, choose a backend that is actually available in your
environment and account:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "openai:<openai-model-id>"
```

For Anthropic:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --max-generations 10 --backends "anthropic:<anthropic-model-id>"
```

For a local Ollama model:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "ollama:<installed-ollama-model>"
```

Inspect a run:

```bash
py -3.12 -m libreevolve show runs/hello_world
```

Use a fresh `--run-name` for repeat runs, or pass `--overwrite` when you
intentionally want to replace the existing run directory.

Provider-backed runs can spend API credits and may fail during backend preflight
if credentials, model ids, local Ollama state, or account access are not
available.

## Run Artifacts

Runs write to `runs/<run-name>/`, which is gitignored. The main outputs are
`manifest.json`, `best.py`, `best_workspace/`, evaluator/plugin artifact
folders, and the current JSONL streams:

- `archive_events.jsonl`
- `controller_budget_events.jsonl`
- `evaluator_results.jsonl`
- `failure_history.jsonl`
- `history.jsonl`
- `llm_calls.jsonl`
- `prompt_current_binding_table.jsonl`
- `prompt_history.jsonl`
- `prompt_prior_score_table.jsonl`

See [docs/run-artifacts.md](docs/run-artifacts.md) for schemas, invalid-record
quarantine streams, restore behavior, and inspection details. Archive restore
is split between cursor/counter resume via
`--restore-archive-cursor-from-manifest` and checked full archive cell/elite
snapshot restore via `--restore-archive-from-manifest`; neither path replays
`archive_events.jsonl` as an ordered MAP-Elites migration engine. Whole-run
source/workspace integrity is bounded by
`papers/whole_run_source_workspace_integrity_boundary.json`.

## How It Works

1. Load a problem directory with seed code, objective text, optional config, and
   a validator.
2. Evaluate the seed candidate.
3. Select parent programs from the archive.
4. Render a mutation prompt and call an LLM backend.
5. Parse the response as SEARCH/REPLACE diffs or full replacement code.
6. Evaluate the candidate in a subprocess and apply any configured stages.
7. Admit valid finite-scoring candidates into the program database and
   MAP-Elites archive.
8. Persist run artifacts for inspection and later analysis.

## Problem Layout

Problem directories live under `libreevolve/problems/examples/`. A minimal
problem usually includes:

- `seed.py`: initial program to evolve.
- `evaluator.py`: validator entrypoint.
- `prompt.txt` or problem metadata: task instructions for the LLM.
- optional `config.yaml`: backend, archive, prompt, and evaluator settings.

See [docs/problem-format.md](docs/problem-format.md) for the full contract.

## CLI

```bash
py -3.12 -m libreevolve --help
py -3.12 -m libreevolve run --help
py -3.12 -m libreevolve show --help
```

Common run options:

- `--max-generations`
- `--max-evaluations`
- `--max-runtime-seconds`
- `--backends`
- `--plugins`
- `--mutation-mode diff|full`
- `--parent-selection-strategy`
- `--overwrite`

## Where To Read Next

- [docs/README.md](docs/README.md): complete documentation map.
- [docs/architecture.md](docs/architecture.md): runtime architecture.
- [docs/configuration.md](docs/configuration.md): config fields and CLI
  overrides.
- [docs/backends.md](docs/backends.md): OpenAI, Anthropic, and Ollama behavior.
- [docs/plugins.md](docs/plugins.md): plugin hooks and built-in plugins.
- [docs/run-artifacts.md](docs/run-artifacts.md): files written under `runs/`.
- [docs/status.md](docs/status.md): detailed implementation and absence-boundary
  ledger.
- [ROADMAP.md](ROADMAP.md): implementation status and remaining work.
- [papers/README.md](papers/README.md): source papers, status rows, and
  claim-boundary records.

The docs are intentionally split by purpose. Setup and first-run usage belongs
here; operational details belong in `docs/`; paper-derived claim evidence
belongs in `papers/`; backlog and truthfulness checks belong in `docs/todo/`
and `ROADMAP.md`.

## Research Sources

LibreEvolve is informed by a local cache of 53 papers on LLM-guided evolution,
program synthesis, quality-diversity optimization, and related benchmarks. The
PDF cache lives locally under `papers/`, but the PDFs themselves are gitignored.
The committed repository tracks `papers/README.md`, download manifests, and
JSON source-boundary artifacts.

Manifest `title` fields are inventory/display slugs derived from cache names,
not authoritative bibliographic titles. Use `papers/README.md` for paper-facing
titles, implementation status, and benchmark coverage decisions.

`papers/README.md` is the complete implementation-status index for all 53
manifest rows. It separates implemented behavior, inspiration-only sources,
candidate benchmark ideas, and source-boundary records so the root README does
not have to carry the full research ledger.

Rehydrate the ignored local PDF cache on a fresh checkout:

```bash
py -3.12 -m libreevolve.tools.paper_manifest --rehydrate
```

Validate the paper index:

```bash
py -3.12 -m libreevolve.tools.paper_manifest
py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs
```

## Testing

Run the non-integration tests:

```bash
py -3.12 -m pytest tests/ -m "not integration" --tb=short
```

Run integration tests only when the required provider credentials are present:

```bash
py -3.12 -m pytest tests/integration/ -m integration --tb=short
```

## Repository Layout

```text
libreevolve/
  core/          orchestration, prompting, evaluation, diffing, database, config
  llm/           OpenAI, Anthropic, Ollama, and ensemble routing
  population/    program records, MAP-Elites, island migration
  plugins/       optional lifecycle hooks and paper-inspired plugins
  problems/      examples and problem loading
  tools/         paper/source manifest validation
docs/            architecture, configuration, backend, plugin, and artifact docs
papers/          tracked manifests plus ignored local PDF cache
runs/            gitignored run outputs
tests/           unit and integration tests
```

## Contributing

Keep root README changes practical and short. Detailed behavior belongs in
`docs/`, source-boundary evidence belongs in `papers/README.md` and JSON
sidecars, and long-term implementation status belongs in `ROADMAP.md` or
`docs/todo/`.

Before opening a change, run focused tests for touched code and the paper
manifest check when source-boundary files change.

GitHub Actions currently provide path-scoped Ubuntu validation for secret
scanning, Python 3.11/3.12 non-integration tests, and optional credential-gated
integration tests. Broader paper/docs CI, wheel/sdist smoke checks,
cross-platform matrices, and branch/notification policy are tracked by
`papers/ci_workflow_coverage_boundary.json`.

The secret scan uses `.secrets.baseline`. If you intentionally add synthetic
provider-looking tokens in tests or TODO evidence, use a narrow fixture marker
such as `# pragma: allowlist secret` where appropriate, or regenerate and stage
the resulting `.secrets.baseline` change. A detect-secrets report about an
unstaged baseline is a validation issue to review and stage, not a
`provider/API failure`.

## License

MIT. See [LICENSE](LICENSE).
