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
- Benchmark-hardening records and shipped-example scope validate smoke-scope
  anti-gaming metadata and `alphaevolve_comparable: false` boundaries, not
  benchmark-grade tensor/geometric/constructive-math runners, randomized or
  exhaustive anti-gaming evidence, executable construction/certificate
  validators, target/SOTA baselines, Colab-equivalent Appendix B construction
  data, or verifier-code artifacts.
- Matrix-publication evidence is one checked `mm_2x2x2` Strassen baseline
  bundle plus Appendix A registry/status metadata, not full-suite local target
  tensors, discovered decompositions, coefficient data, exactness
  certificates, notebooks, per-seed reports, or publication bundles for every
  registered Appendix A target.
- Appendix A matrix target-suite curation records the reported 54 sorted
  targets, rough paper selection wording, symmetry policy, and included-target
  rationales, not an exhaustive locally justified corpus for every excluded
  non-equivalent matrix size outside the reported suite.
- Appendix A matrix resource-frontier records preserve the paper-source
  statement about sizes beyond `<5,5,5>`, 1000 random seeds, single-GPU
  evaluators, frequent OOM, and further-optimization need, not local
  larger-target runs, measured accelerator-memory profiles, OOM artifacts,
  reduced-seed tradeoffs, or reproduced scaling evidence.
- Matrix per-seed reports validate declared seed rows, best rank, and hit
  fraction, and matrix cascade-run boundary records can link seed rows to stage
  traces, but local matrix runners do not yet emit AlphaEvolve Section
  3.1-style repeated-seed cascade traces, pruning decisions, or early-stop
  provenance.
- Matrix near-integrality records validate declared prompt instructions,
  integer/half-integer rounding policy, raw-versus-rounded coefficient
  diagnostics, and exactness-certificate links, not a local matrix runner that
  emits AlphaEvolve Section 3.1 near-integral prompt/evaluator evidence during
  search.
- Matrix sweep-space records validate declared Figure 9-style `sweep()`
  provenance, user-provided `hyper` ranges, sampled configurations, selected
  winners, final decompositions, and exactness-certificate links, not a local
  matrix runner that emits AlphaEvolve Figure 4/Figure 9 search-program sweep
  evidence during search.
- Appendix A Figure 9 matrix-diff records validate panel ids, pages, line
  spans, semantic components, source/diff hashes, rendered/OCR artifact
  metadata, and links to matrix result, sweep-space, certificate, and companion
  notebook evidence, not local report/export output that emits rendered panel
  images, OCR text, or source-diff artifacts for Figures 9a-9c.
- Figure 4 matrix-discovery records validate main-text exhibit metadata,
  caption linkage, the 15-mutation caption count, `mm_4x4x4` rank-48 target
  mapping, highlighted component categories, source/diff artifact metadata,
  and links to Figure 9, matrix-result, certificate, and notebook evidence, not
  local report/export output that emits rendered Figure 4 artifacts or accepted
  15-mutation lineage.
- Matrix baseline-component records validate Section 3.1 starting-algorithm
  provenance fields for baseline program ids, initializer, reconstruction
  loss, Adam optimizer metadata, mutable scopes, fixed hashes, generation-0
  metrics, mutation lineage, and matrix-result links, not local matrix-runner
  output that emits the initializer/loss/optimizer provenance during search.
- Matrix scalar-field records validate complex/finite-field metadata,
  characteristic and applicability claims, exact coefficient representation,
  algorithm and certificate refs, and matrix-result links, not local matrix
  runners that emit exact complex decomposition/certificate artifacts for
  AlphaEvolve Section 3.1 scalar-field claims.
- Matrix tensor-rank records validate tensor-decomposition versus non-tensor
  algorithm claims, rank, recursive applicability, certificate scope,
  tensor-identity status, target-tensor refs, exactness-certificate refs, and
  matrix-result links, not local matrix runners that emit AlphaEvolve Section
  3.1 target-tensor/certificate artifacts during search.
- Constructive-math heuristic-handoff records preserve the Section 3.2 claim
  that search-heuristic programs run under fixed budgets from strong
  previous-best construction inputs toward improved constructions, not local
  heuristic-program artifacts, incumbent or produced construction payloads,
  fixed-budget execution records, before/after metric rows, scores, or
  verifier evidence.
- Constructive-math stage-sequence records preserve the Section 3.2 claim that
  final constructions often came from multiple specialized heuristics,
  including early broad-gain stages from random/simple starts and later
  fine-tuning near optimal configurations, not local per-stage heuristic
  artifacts, ordered construction transitions, stage-role rows, improvement
  deltas, budget rows, or verifier evidence.
- Constructive-math aggregate-outcome records preserve the Section 3.2 source
  claim of over 50 mathematical problems across more than five branches, about
  75% best-known rediscovery, about 20% SOTA improvement, and definition-based
  verification, not local per-problem rows, branch taxonomy rows, prior-best
  references, construction/verifier artifacts, aggregate counts, or percentage
  recomputation.
- Constructive-math starting-construction records preserve the Section 3.2
  source claim that the initial starting point was a simple or random
  construction, not local per-instance starting construction payloads,
  generator or random-seed records, baseline metric rows, prior-best visibility
  policy, or prior-best seeding policy evidence.
- Figure 5 constructive-math exhibit provenance remains absent: README
  describes Appendix B family/status coverage, smoke-fixture boundaries, and
  constructive-math absence boundaries, not main-text Figure 5 exhibit ids,
  selected result-row links, branch/problem label mappings, before/after metric
  values, previous-best sources, rendered visual artifact paths or hashes,
  rendering parameters, source Colab cells/artifacts, or verifier links.
- Figure 5 versus Appendix B.12 sum-of-radii precision remains unreconciled:
  the registry preserves Figure 5's `2.6340 -> 2.6358` display separately from
  the Appendix B.12/Figure 14 `2.634 -> 2.635` strings, not source-specific
  locators, Figure 5 panel artifacts, value-extraction certificates,
  normalized values, rounding or canonicalization policy, value-reconciliation
  certificate, recomputed sum, or companion Colab link.
- Appendix B Figures 10-14 figure-exhibit provenance remains absent: the
  registry names Erdos minimum overlap, regular-hexagon packing,
  maximum/minimum-distance point sets, Heilbronn variants, and
  circle/rectangle sum-of-radii packing figure scopes, not normalized
  figure-exhibit rows, subfigure ids, caption-value extraction,
  previous/current metric rows, construction payload artifacts, rendered panel
  artifacts, rendering parameters, source Colab cells/artifacts, or verifier
  links.
- Appendix B numeric-result provenance remains absent: the registry enumerates
  B.1-B.13 family/status metadata and the `19` expected future result ids,
  including the B.4 revision row, not normalized per-result metric/value rows,
  parameter tuples, inequality or optimization direction records, previous-best
  values/sources, AlphaEvolve reported-value rows, source locations,
  construction-representation schemas, construction/verifier artifact hashes,
  result-version status, recomputed values, or recomputation status.
- Appendix B.1-B.3 autocorrelation step-function provenance remains absent:
  the registry preserves the paper-facing C1-C3 labels, interval counts,
  shared `[-1/4, 1/4]` domain, sign policy, bound direction, previous
  bound/source, and reported bounds (`C1 <= 1.5053`, `0.8962 <= C2`, and
  `C3 <= 1.4557`), not local step-function payload hashes,
  domain/spacing/sign-policy certificates, verifier artifacts, recomputed
  bound rows, or recomputation certificates.
- Appendix B.8 max/min-distance point-set witness provenance remains absent:
  the registry preserves the squared-ratio convention, Figure 12 left/right
  linkage, 16-point/2D and 14-point/3D metadata, prior squared bounds
  (`12.890`, `4.168`), and reported squared ratios (`12.889266112`,
  `4.165849767`), not coordinate payload hashes, point-count/dimension
  certificates, all-pairs distance matrix artifacts, min/max pair-witness
  certificates, recomputed squared-ratio rows, or Figure 12 panel artifacts.
- Appendix B.5 Erdos minimum-overlap step-function provenance remains absent:
  the registry preserves the source formulation, `[40]` equivalence,
  normalized `[0, 2]` step-function reduction, Figure 10 result id, prior
  `0.379005 <= C5 <= 0.380927` bounds, and reported `C5 <= 0.380924` upper
  bound, not a step-function payload hash, original-formulation mapping
  certificate, `[40]` equivalence-reference artifact, shift-domain
  certificate, value-range or integral-normalization certificates,
  shift-objective recomputation, recomputed upper bound, or Figure 10 panel
  artifact.
- Appendix B.6 finite-set witness provenance remains absent: the registry
  preserves the `C6` theorem/admissibility statement, `U1`/`U2` witness labels,
  set sizes `2003` and `54265`, reported lower bounds `1.1479 <= C6` and
  `1.1584 <= C6`, and required future finite-set fields, not sorted integer
  payload hashes, contains-zero or non-negative certificates,
  `|U - U| <= 2 max(U) + 1` admissibility certificates, `|U-U|`/`|U+U|`
  cardinality certificates, max-element certificates, formula-substitution
  certificates, or recomputed lower-bound rows.
- Appendix B.7 regular-hexagon packing provenance remains absent: the registry
  preserves the unit-regular-hexagon objective, Figure 11 left/right linkage,
  prior `[29]` values, `n = 11` and `n = 12` witness summaries, and reported
  outer-side improvements (`3.943 -> 3.931` and `4.0 -> 3.942`), not placement
  payload hashes, pose/orientation schemas, inner/outer regular-hexagon
  geometry certificates, containment or non-overlap certificates, side-length
  recomputation certificates, recomputed side lengths, or Figure 11 panel
  artifacts.
- Follow-on problem-repository coverage records validate pinned snapshot
  problem-page, status-bucket, link, hash, notebook-link, absence-reason,
  notebook-hash, scoped artifact-flag, Appendix B crosswalk, and
  artifact-rights-template evidence, not live repository completeness, full
  notebook cell inventories, normalized result rows, construction payloads,
  verifier artifacts, recomputed values, or copied/adapted generated artifacts.
- Follow-on problem-count wording remains snapshot-scoped: the source
  README/paper declares 67 mathematical problems, pinned diagnostics observe
  68 numbered HTML pages, and page 68 is classified as an extra duplicate-title
  `Logic puzzles` page outside the declared navigation range with a generic
  Colab landing URL and placeholder paper link.
- Paper artifact-role records validate AlphaEvolve PDF page 23 figure-creator
  and companion Google Colab assembler attribution with stable artifact ids,
  exact contributor initials, source section/page metadata, and source phrases,
  not linked rendered figure files, caption/source maps, figure-region
  artifacts, companion notebook URLs or digests, retrieved notebook exports,
  cell maps, or source-to-artifact maps.
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
- Hardware RTL/EDA records validate metadata only: they do not yet provide real
  Verilog/RTL source, synthesis or PPA runs, verification logs, designer
  signoff, downstream-synthesis artifacts, upcoming-chip integration, or
  deployment/time-to-market evidence.
- Hardware rewrite records are also metadata only: they do not yet provide real
  before/after Verilog files, exact diff or AST artifacts, removed-bit
  inventories, component review files, or per-bit functional and PPA evidence
  for the TPU arithmetic-circuit rewrite.
- Hardware contribution records are metadata only: they do not yet provide real
  model/run/backend records, reviewed TPU/circuit identifiers,
  novelty/firstness evidence, integration records, hardware signoff files, or
  synthesis-rediscovery audit artifacts for the Gemini-to-TPU attribution claim.
- Compiler IR records validate metadata only: they do not yet provide real
  XLA/FlashAttention edit artifacts, randomized input coverage,
  reference-check outputs, tolerance/failure logs, or expert all-input signoff.
- Compiler stack records validate metadata only: they do not yet provide real
  Transformer/inference configuration records, Pallas source snapshots, JAX
  wrapper artifacts, XLA stage outputs, hardware-target records, lowered-IR
  files, or optimization-decision evidence.
- Compiler adoption records validate metadata only: they do not yet provide
  real compiler patch/pass artifacts, use-case integration records, reviewer
  signoff files, deployment or rollback logs, or AlphaEvolve-in-compiler-loop
  evidence.
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
