# LibreEvolve

LibreEvolve is a Python research prototype for LLM-guided evolutionary program
discovery. It takes a problem directory, asks configured LLM backends to propose
code mutations, evaluates the resulting candidates, and keeps the best programs
in a small quality-diversity archive.

It is inspired by AlphaEvolve, Karpathy's `autoresearch`, MAP-Elites, and recent
work on LLM-guided program search. It is an independent project and is not
affiliated with or endorsed by Google DeepMind or the authors of the cited
papers.

## Status

This is an alpha-stage research codebase, not a production optimizer and not a
full AlphaEvolve reproduction.

Implemented today:

- Python-primary candidate workspaces and seed programs.
- SEARCH/REPLACE diff mutations using the AlphaEvolve fence format.
- Full-code replacement mode when configured.
- OpenAI, Anthropic, and Ollama backend adapters.
- A heuristic UCB-style backend selector.
- Synchronous MAP-Elites and island archives, with five islands by default.
- Local subprocess evaluation with staged validator support.
- Optional critique, feedback, and plugin hooks.
- Run artifacts under `runs/`, including manifests, histories, prompts,
  failures, best candidates, and plugin/evaluator artifacts.

Important limits:

- Evaluators run in local subprocesses, not hardened security sandboxes.
- The controller, archive, migration, and evaluator flow are local and
  synchronous, not a distributed asynchronous AlphaEvolve-style service.
- Scientific-discovery scope is machine-gradeable local evaluator workflow
  scope; robust evaluator-environment fixtures, manual-to-code transition
  policies, and LLM-only idea-stage contracts are tracked by
  `papers/automated_evaluator_scope_boundary.json`.
- Natural-language proposal metadata is context around executable code
  candidates, not AI-Co-Scientist-style hypothesis representation or
  hallucination-resistance evidence; that boundary is tracked by
  `papers/programmatic_representation_boundary.json`.
- Natural-language preambles are bounded leading metadata before structured
  mutation markers, not complete freeform rationale handling; that boundary is
  tracked by `papers/natural_language_preamble_boundary.json`.
- Prompt example-copy reports are built-in exact/normalized/skeleton
  diagnostics, not hard rejection, semantic-copy detection, or custom-template
  inventory evidence; that boundary is tracked by
  `papers/prompt_example_copy_boundary.json`.
- Multi-edit consistency reports are current-run diagnostics, not proof that
  accepted edits are semantically coherent or that required companion edits are
  inferred; that boundary is tracked by
  `papers/mutation_consistency_boundary.json`.
- Initial-pool divergence reports are syntactic and shared-metric telemetry,
  not task-specific functional-distance proof or "substantially different"
  benchmark evidence; that boundary is tracked by
  `papers/initial_pool_divergence_boundary.json`.
- Duplicate-work reports are run-local exact-workspace cache diagnostics, not
  durable cross-run memory, semantic duplicate detection, or resume-spanning
  cache replay; that boundary is tracked by
  `papers/duplicate_work_policy_boundary.json`.
- Related Work positioning is not inferred from the bundled paper list; the
  missing taxonomy and claim gates are tracked by
  `papers/related_work_taxonomy_boundary.json`.
- Candidate execution is Python-primary. Arbitrary language/build runners and
  problem-defined candidate abstractions remain open work.
- Configuration validation is local effective-config validation; live
  provider/model API compatibility is tracked by
  `papers/config_validation_boundary.json`.
- Database sampling reports are local strategy/count telemetry, not calibrated
  AlphaEvolve-style exploration/exploitation evidence; that boundary is tracked
  by `papers/sampling_balance_boundary.json`.
- Multi-objective archive data is retained overlay and diagnostic frontier
  evidence, not primary Pareto/frontier archive replacement or durable
  cross-run metric optimization; that boundary is tracked by
  `papers/objective_archive_boundary.json`.
- Metric-diverse prompt evidence is current-run prompt-visible telemetry, not
  benchmark-required metric-diverse prompt policy, cross-run fixtures, or
  scalar/single-metric equal-budget comparisons; that boundary is tracked by
  `papers/metric_diverse_prompt_boundary.json`.
- MAP-Elites descriptor snapshots are insertion-time local descriptor metadata,
  not stable learned/evaluator-provided behavior descriptors or archive rebin
  semantics; that boundary is tracked by
  `papers/map_elites_descriptor_boundary.json`.
- The included examples are smoke fixtures and small demos unless a fixture
  explicitly documents stronger benchmark evidence.
- Gemini/provider parity, benchmark-scale claims, paper-result reproduction,
  release packaging, and broader CI/platform guarantees are tracked as
  boundaries in `papers/README.md` and `ROADMAP.md`, not promised here.

## Installation

Use Python 3.11 or newer. On this Windows machine, use `py -3.12`.

```bash
py -3.12 -m pip install -e ".[dev]"
```

Create a `.env` file at the project root for any provider keys you plan to use:

```dotenv
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-ant-...
OLLAMA_HOST=http://localhost:11434
```

`.env` is loaded for `libreevolve run` with `override=True`. Do not commit API
keys.

## Quick Start

Run one of the bundled examples with a backend available in your environment:

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
quarantine streams, restore behavior, and inspection details. Whole-run
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

## Documentation

- [docs/README.md](docs/README.md): documentation index.
- [docs/architecture.md](docs/architecture.md): runtime architecture.
- [docs/configuration.md](docs/configuration.md): config fields and CLI
  overrides.
- [docs/backends.md](docs/backends.md): OpenAI, Anthropic, and Ollama behavior.
- [docs/plugins.md](docs/plugins.md): plugin hooks and built-in plugins.
- [docs/run-artifacts.md](docs/run-artifacts.md): files written under `runs/`.
- [ROADMAP.md](ROADMAP.md): implementation status and remaining work.
- [papers/README.md](papers/README.md): source papers, status rows, and
  claim-boundary records.

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
