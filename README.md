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

- There is no first-class Gemini provider yet; the absence boundary is tracked
  by `runtime.history.gemini_provider_parity_report` and
  `papers/gemini_provider_parity_boundary.json`.
- Evaluators run in local subprocesses, not hardened security sandboxes.
- The archive and controller are local and synchronous, not a distributed
  asynchronous AlphaEvolve-style service; parallel-evaluation readiness is
  tracked by `runtime.history.parallel_evaluation_readiness_report` and
  `papers/parallel_evaluation_readiness_boundary.json`, while topology parity
  is bounded by `papers/distributed_pipeline_topology_boundary.json`.
- Codebase-scale telemetry exists for current runs, but it is not
  AlphaEvolve Table 1 code-scale parity; the boundary is tracked by
  `runtime.history.codebase_scale_benchmark_report` and
  `papers/codebase_scale_benchmark_boundary.json`.
- Incorrect-suggestion filtering evidence is local execution/evaluator
  telemetry, not an independent audit; the boundary is tracked by
  `runtime.history.incorrect_suggestion_audit_report` and
  `papers/incorrect_suggestion_audit_boundary.json`.
- Benchmark-fixture readiness is smoke/example-scope telemetry until
  repeated-seed, baseline, emitted-artifact, and anti-gaming evidence exists;
  the boundary is tracked by `papers/benchmark_fixture_readiness_boundary.json`.
- Expert-guided problem formulation is a metadata/report contract until real
  benchmark fixtures carry populated review/signoff evidence; the boundary is
  tracked by `papers/problem_formulation_provenance_boundary.json`.
- Collaborator-feedback provenance is a metadata/report contract until
  representative fixtures carry reviewed multi-cohort feedback evidence; the
  boundary is tracked by `papers/collaborator_feedback_provenance_boundary.json`.
- The included examples are smoke fixtures and small demos unless explicitly
  documented otherwise.
- Paper and blog claims are tracked as source boundaries unless local benchmark
  evidence exists.

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

The table below is a curated subset for README context. `papers/README.md` is
the complete implementation-status index for all 53 manifest rows.

<details>
<summary>Curated source context</summary>

| Source | Role in LibreEvolve |
| --- | --- |
| [AlphaEvolve](https://arxiv.org/abs/2506.13131) | Main architecture inspiration and comparison target. |
| [AlphaEvolve 2026 impact update](https://deepmind.google/blog/alphaevolve-impact/) | Official DeepMind impact-claim context only; `papers/alphaevolve_2026_impact_boundary.json` records missing local benchmark evidence for the named DeepConsensus, AC OPF, Earth AI, Willow, TPU, cache-policy, Spanner, compiler-storage, public-gallery, customer, UI, and API workflows. |
| [MAP-Elites](https://arxiv.org/abs/1504.04909) | Quality-diversity archive inspiration. |
| [Finite-time Analysis of the Multiarmed Bandit Problem](https://homes.di.unimi.it/~cesabian/Pubblicazioni/ml-02.pdf) | UCB1 background for backend-selection boundaries. |
| [CodeEvolve](https://arxiv.org/abs/2510.14150) | Related agentic code-evolution work. |
| [DeepEvolve](https://arxiv.org/abs/2510.06056) | Related evolutionary coding-agent work. |
| [FHE on TPU](https://arxiv.org/abs/2605.14718) | AlphaEvolve FHE/TPUv5e application context only; no local cryptographic-kernel or hardware-execution benchmark exists. |
| [Intentmaking and Sensemaking](https://arxiv.org/abs/2605.05921) | AlphaEvolve HCI/user-study context only; no local intentmaking/sensemaking session-trace workflow exists. |
| [Radar Power Allocation](https://arxiv.org/abs/2605.01794) | AlphaEvolve radar resource-allocation application context only; no local multi-target tracking or power-allocation benchmark exists. |
| [EvoX](https://arxiv.org/abs/2602.23413) | Adaptive meta-evolution context only; no local strategy-genome, strategy-credit, or dynamic search-policy benchmark exists. |
| [DeltaEvolve](https://arxiv.org/abs/2602.02919) | Semantic-delta context-memory inspiration only; no local semantic-delta store, progressive disclosure sampler, or token-efficiency benchmark exists. |
| [MLEvolve](https://arxiv.org/abs/2606.06473) | Long-horizon ML-engineering context only; no local MLE-Bench harness, Progressive MCGS controller, or 12-hour medal-rate report exists. |
| [LEVI](https://arxiv.org/abs/2605.09764) | Cost-aware search-architecture context only; no local large/small model mutation router, proxy benchmark, or cost-comparison report exists. |
| [PACEvolve](https://arxiv.org/abs/2601.10657) | Long-horizon consistency context only; no local hierarchical context-management, momentum-backtracking, or LLM-SR/KernelBench report exists. |
| [FlashEvolve](https://arxiv.org/abs/2605.08520) | Asynchronous-stage orchestration context only; no local async worker queue, artifact-version DAG, staleness repair, or throughput benchmark exists. |
| [What Do Evolutionary Coding Agents Evolve?](https://arxiv.org/abs/2605.20086) | Trace-diagnostic evaluation context only; no local EvoTrace edit taxonomy, EvoReplay intervention harness, or cycling/overfitting report exists. |
| [Zarankiewicz reinforced search](https://arxiv.org/abs/2605.01120) | Extremal-graph benchmark candidate only; no local Zarankiewicz fixture, `K_{s,t}` verifier, construction table, or sub-$30 cost report exists. |
| [CORAL](https://arxiv.org/abs/2604.01658) | Autonomous multi-agent evolution context only; no local long-running agent sessions, shared persistent memory, heartbeat interventions, or isolated multi-agent workspace runtime exists. |
| [AEvo](https://arxiv.org/abs/2605.13821) | Harnessed meta-editing context only; no local process-level state, meta-agent procedure editor, protected evaluator harness, or meta-edit benchmark report exists. |
| [G-Zero](https://arxiv.org/abs/2605.09959) | Verifier-free co-evolution context only; no local Hint-delta intrinsic reward, Proposer/Generator co-training loop, GRPO/DPO trainer, or verifier-free self-evolution report exists. |
| [GenEvolve](https://arxiv.org/abs/2605.21605) | Multimodal trajectory-distillation context only; no local image-generation tool pipeline, visual-reference trajectory store, Agentic Visual Experience Distillation, or GenEvolve-Bench report exists. |
| [EvoRubric](https://arxiv.org/abs/2605.29847) | Self-evolving reward-rubric context only; no local Reasoner/Rubric-Generator co-evolution, criteria verification, rubric memory pool, or reward-hacking report exists. |
| [LLM-ALSO](https://arxiv.org/abs/2605.29293) | Learning-signal optimization context only; no local sparse-reward MARL harness, Critic/Generator reward-shaping loop, branch-validation trace, or learning-efficiency report exists. |
| [MemEvolve](https://arxiv.org/abs/2512.18746) | Memory-architecture evolution context only; no local encode/store/retrieve/manage design space, memory-architecture mutation loop, EvolveLab benchmark mapping, or transfer report exists. |
| [ANCHOR healthy evolution](https://arxiv.org/abs/2606.06114) | Healthy-evolution oversight context only; no local human-like oversight agent, phase-specific norm-correction interface, safety-drift metric lineage, or supervision-cadence report exists. |
| [SIA](https://arxiv.org/abs/2605.27276) | Harness-plus-weight self-improvement context only; no local Feedback-Agent, editable task-agent harness inventory, online weight-update loop, adapter/checkpoint lifecycle, or harness-versus-weight ablation report exists. |
| [HarnessFix](https://arxiv.org/abs/2606.06324) | Trace-grounded harness repair context only; no local HTIR trace normalization, harness-layer failure attribution, recurring flaw record consolidation, scoped repair operator schema, or regression-bounded patch validation exists. |
| [RHO](https://arxiv.org/abs/2606.05922) | Retrospective harness optimization context only; no local hard/diverse trajectory coreset selector, parallel re-rollout workflow, self-validation/self-consistency analysis, pairwise self-preference harness ranking, or SWE-Bench Pro reproduction exists. |
| [Harness Updating Is Not Harness Benefit](https://arxiv.org/abs/2605.30621) | Harness-capability disentanglement context only; no local harness-updating versus harness-benefit metric schema, cross-model capability-tier experiment, activation/adherence failure audit, or benchmark reproduction exists. |
| [AHE](https://arxiv.org/abs/2604.25850) | Observability-driven harness-evolution context only; no local file-level harness component graph, layered trajectory evidence corpus, edit-prediction contract, falsification loop, or Terminal-Bench 2 reproduction exists. |
| [AI Harness Engineering](https://arxiv.org/abs/2605.13357) | Runtime-substrate context only; no complete eleven-responsibility harness contract, H0-H3 ladder, trace-based episode package, controlled validation task, or structured verification report exists. |
| [Inference-time trajectory alignment](https://arxiv.org/abs/2605.21516) | Harness design context only; no local decomposition/guidance parameter sweep, retry-budget study, over-decomposition/over-pruning/hallucinated-execution report, partial-harnessing benchmark, or terminal-agent reproduction exists. |
| [Adaptive Auto-Harness](https://arxiv.org/abs/2606.01770) | Open-ended task-stream deployment context only; no local chronological task stream, evolution/adaptation-loss decomposition, harness tree routing, human-steering hook, or prediction-market/security/event benchmark reproduction exists. |
| [Meta-Harness](https://arxiv.org/abs/2603.28052) | Outer-loop harness-code optimization context only; no local harness-code candidate schema, agentic proposer workspace, execution-trace feedback bundle, cross-task harness benchmark, or end-to-end harness optimization reproduction exists. |

</details>

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

The secret scan uses `.secrets.baseline`. If you intentionally add synthetic
provider-looking tokens in tests or TODO evidence, use a narrow fixture marker
such as `# pragma: allowlist secret` where appropriate, or regenerate and stage
the resulting `.secrets.baseline` change. A detect-secrets report about an
unstaged baseline is a validation issue to review and stage, not a
`provider/API failure`.

## License

MIT. See [LICENSE](LICENSE).
