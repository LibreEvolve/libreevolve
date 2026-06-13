# LibreEvolve

LibreEvolve is a Python research workbench for LLM-guided evolutionary program
discovery. It loads a problem directory, evaluates seed programs, asks
configured LLM backends for mutations, scores the candidates, and keeps useful
programs in local quality-diversity archives.

The project is inspired by AlphaEvolve, Karpathy's `autoresearch`, MAP-Elites,
and related LLM-guided program-search work. It is independent research code and
is not affiliated with or endorsed by Google DeepMind or the authors of the
cited papers.

## Current Status

LibreEvolve is alpha-stage software. The honest current shape is a local,
Python-first evolutionary-programming workbench with extensive artifact and
absence-boundary reporting. It is useful for local experiments, implementation
audits, and building small fixtures. It is not a production optimizer, not a
distributed service, and not a full AlphaEvolve reproduction.

Runnable today:

- Python-primary seed programs and bounded text workspaces.
- Opt-in strict initial-program validity reports for runs that require every
  selected seed to be evaluator-valid before mutation; multi-seed,
  provider-startup, matrix, and constructive-math strict evidence remains
  open work.
- SEARCH/REPLACE mutation diffs using canonical AlphaEvolve-style fences, plus
  configurable full-code replacement mode.
- OpenAI, Anthropic, Ollama, and custom import-path backend support.
- Heuristic UCB-style backend selection.
- Local MAP-Elites and island archives, with five islands by default.
- Local subprocess evaluation with optional staged validators.
- Optional critique, feedback, and plugin hooks.
- Gitignored run artifacts under `runs/`.

Important limits:

- No checked-in run reproduces AlphaEvolve's published benchmark results,
  scale, model mix, asynchronous topology, or systems/compiler/hardware
  application evidence.
- LibreEvolve is not the Google Cloud AlphaEvolve Service API, not a Gemini
  Enterprise managed agent, and not evidence of access to AlphaEvolve private
  preview or Pre-GA product surfaces.
- Many AlphaEvolve-facing JSON sidecars are validators or absence-boundary
  records. They are evidence that a claim is tracked conservatively, not proof
  that the underlying feature or benchmark has been reproduced.
- The local paper cache is source inventory. A cached paper or `papers/README.md`
  row does not mean the paper's method or results are implemented.
- Evaluators run in local subprocesses, not hardened security sandboxes.
- The controller, archive, migration, and evaluator flow are local and
  synchronous, not a distributed Python `asyncio` AlphaEvolve service.
- Candidate execution is Python-primary. Non-Python files can be workspace
  members, metadata-only runner/build declarations can be recorded, and the
  current Python runner links to bounded environment provenance, but
  arbitrary-language runners and build-system runners are not implemented.
- Candidate abstractions are code-file/workspace based; problem-defined direct
  solution objects, constructor-function search, bespoke search-algorithm
  candidates, paired solution/search representations, abstraction-specific
  prompts/validators/archive descriptors, migration policies, and equal-budget
  cross-abstraction reports are tracked as missing AlphaEvolve-style work.
- Built-in provider adapters are OpenAI, Anthropic, and Ollama. Google/Gemini
  parity is tracked as missing work.
- The included examples are smoke fixtures unless they explicitly document
  stronger benchmark evidence.
- The default initial-program policy is permissive; AlphaEvolve-style complete
  initial-solution parity requires explicit strict-mode evidence.
- Human-seeded initial-program claims require exact prompt/context linkage,
  seed workspace hashes, replicate protocols, equal-budget seed-variant
  tables, and contribution review evidence; current reports are metadata
  contracts only.
- Expert-guided mathematical benchmark formulation claims require populated
  expert/owner identity, evaluator/report artifact linkage, signoff versions,
  background-reference artifacts, and anti-gaming review evidence; current
  formulation reports are metadata contracts only.
- Collaborator-feedback robustness claims require multi-cohort source
  artifacts, workflow diffs, validation reruns, privacy/redaction artifacts,
  review versions, follow-up, and claim-to-feedback traces; current feedback
  reports are metadata contracts only.
- Paper-derived claims are tracked conservatively in `papers/README.md`,
  sidecar JSON records, `ROADMAP.md`, and `docs/todo/`; the TODO ledgers are
  active work queues, not just historical notes.

For the full implemented-versus-missing ledger, read
[docs/status.md](docs/status.md). For paper/source coverage, read
[papers/README.md](papers/README.md).

## Requirements

- Python 3.11 or newer.
- On this Windows machine, use `py -3.12`, not `python`.
- Optional provider credentials in `.env` for provider-backed runs.

Install for local development:

```bash
py -3.12 -m pip install -e ".[dev]"
```

## Quick Start

Verify the CLI and artifact writer without making provider calls:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --run-name readme_smoke_sorting --max-llm-calls 0 --overwrite
py -3.12 -m libreevolve show runs/readme_smoke_sorting
```

That evaluates the bundled sorting seed, writes normal run artifacts, and stops
before constructing LLM providers. It is a smoke check, not an evolution run.

Run a provider-backed evolution after choosing a model that is available in
your account or local Ollama install:

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "openai:<openai-model-id>"
py -3.12 -m libreevolve run libreevolve/problems/examples/sorting --max-generations 10 --backends "anthropic:<anthropic-model-id>"
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "ollama:<installed-ollama-model>"
```

Provider-backed runs can spend API credits and may fail during preflight if
credentials, model IDs, local Ollama state, or account access are unavailable.

Use a fresh `--run-name` for repeat runs, or pass `--overwrite` when replacing
an existing run directory intentionally.

## Problem Layout

Problem directories live under `libreevolve/problems/examples/`. A minimal
problem usually contains:

- `initial_programs/`: one or more seed programs.
- `validate.py`: evaluator entrypoint.
- `metrics.yaml`: metric names, directions, bounds, and primary metric.
- `task_description.txt`: task instructions for the mutation prompt.
- optional `config.yaml`: backend, archive, prompt, and evaluator settings.

See [docs/problem-format.md](docs/problem-format.md) for the full contract.

## Example Scope

The bundled examples are intentionally small:

- Optimization-pressure seeds may be valid-but-weak or intentionally invalid
  baselines that leave room for measurable improvement.
- Neutral plateau/diversity fixtures mainly exercise loading, validation,
  artifact writing, or archive behavior.
- `sorting_network_8` and `sorting_network_9` are bounded benchmark candidates
  with exhaustive zero-one validation and known comparator targets, but they
  are not paper-comparable evidence until repeated runs, source citations, and
  certification are added. Their hardening bundle helper emits generic
  negative-fixture, inventory, summary, and scope-validation evidence; it is
  not a certified rediscovery result.

Treat an example as benchmark evidence only when its own docs or paper sidecar
says so.

## Run Artifacts

Runs write to `runs/<run-name>/`, which is gitignored. Common outputs include:

- `manifest.json`
- `archive_events.jsonl`
- `controller_budget_events.jsonl`
- `evaluator_results.jsonl`
- `failure_history.jsonl`
- `history.jsonl`
- `llm_calls.jsonl`
- `prompt_current_binding_table.jsonl`
- `prompt_history.jsonl`
- `prompt_prior_score_table.jsonl`
- `best.py`
- `best_workspace/`
- `evaluator_artifacts/`
- `plugin_artifacts/`

See [docs/run-artifacts.md](docs/run-artifacts.md) for schemas, quarantine
streams, restore behavior, and inspection details.

## Documentation Map

- [docs/README.md](docs/README.md): reader paths and documentation boundaries.
- [docs/architecture.md](docs/architecture.md): runtime architecture.
- [docs/configuration.md](docs/configuration.md): config fields and CLI
  overrides.
- [docs/backends.md](docs/backends.md): provider adapters and custom backends.
- [docs/plugins.md](docs/plugins.md): plugin hooks and built-in plugins.
- [docs/run-artifacts.md](docs/run-artifacts.md): files written under `runs/`.
- [docs/status.md](docs/status.md): detailed implementation and absence ledger.
- [ROADMAP.md](ROADMAP.md): practical implementation priorities.
- [papers/README.md](papers/README.md): paper cache, status rows, and claim
  boundaries.
- [docs/todo/](docs/todo/): active and completed gap ledgers.

The docs are split by purpose. Setup and first-run usage belongs here;
operational details belong in `docs/`; paper-derived claim evidence belongs in
`papers/`; active and completed gap tracking belongs in `docs/todo/` and
`ROADMAP.md`.

## Research Sources

The local paper cache contains 53 PDFs on LLM-guided evolution, program
synthesis, quality-diversity optimization, and related benchmarks. The PDFs are
gitignored; committed manifests record download URLs, byte counts, and SHA-256
hashes.

Rehydrate the ignored PDF cache on a fresh checkout:

```bash
py -3.12 -m libreevolve.tools.paper_manifest --rehydrate
```

Validate the committed paper index:

```bash
py -3.12 -m libreevolve.tools.paper_manifest
py -3.12 -m libreevolve.tools.paper_manifest --require-local-pdfs
```

Manifest `title` values are inventory/display slugs derived from local cache
names, not authoritative bibliographic titles. Use `papers/README.md` for
paper-facing titles, implementation status, and benchmark coverage decisions.

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

Keep the root README practical and short. Detailed behavior belongs in `docs/`,
paper-boundary evidence belongs in `papers/README.md` and JSON sidecars, and
long-term implementation status belongs in `ROADMAP.md` or `docs/todo/`.

Before opening a change, run focused tests for touched code and the paper
manifest check when source-boundary files change.
The secret scan uses `.secrets.baseline`; intentional synthetic provider/API failure
examples should use `# pragma: allowlist secret`, and regenerated baselines
must be staged with the code that needs them rather than left unstaged.

## License

MIT. See [LICENSE](LICENSE).
