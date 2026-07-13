# AGENTS.md

## Project Overview

LibreEvolve is a Python research platform for LLM-guided evolutionary program discovery, inspired by AlphaEvolve, Andrej Karpathy's autoresearch, and related research. It uses SEARCH/REPLACE diffs, a cascade evaluator, configurable MAP-Elites island archives with five islands by default, and a heuristic UCB-style LLM ensemble.

## Tech Stack

- Python 3.11+ (use `py -3.12` on this machine, not `python`)
- Dependencies: numpy, scikit-learn, anthropic, openai, google-genai, ollama, pyyaml, click, python-dotenv, packaging, pypdf
- Testing: pytest, pytest-mock
- No framework — pure Python with dataclasses

## Architecture

```
libreevolve/
  core/       loop.py (evolve orchestration), async_sampler.py, async_evaluator.py,
              prompt.py (PromptSampler), evaluator.py, diff.py, database.py, config.py
  llm/        ensemble.py (UCB-style heuristic), anthropic.py, gemini.py (GenerateContent), openai.py (Responses API when configured), ollama.py
  population/ program.py, map_elites.py (3D TF-IDF), islands.py (ring migration, explore/exploit)
  plugins/    base.py (ABC), causal.py, deep_research.py, modular.py, ttt_rl.py
  problems/   loader.py, examples/{hello_world,circle_packing,sorting,
              matrix_multiplication,workspace_math,candidate_runner_expression,
              candidate_runner_c,candidate_runner_python_oci}/
  cli.py      Click CLI with run/show commands
```

## Key Conventions

- `.env` file at project root for API keys (loaded via python-dotenv with override=True)
- `runs/` directory is gitignored — contains manifest.json, history.jsonl,
  failure/quarantine JSONL streams, archive_events.jsonl, llm_calls.jsonl,
  prompt_history.jsonl, duplicate_work_cache_index.jsonl, best.py,
  best_workspace/, evaluator_artifacts/, and plugin_artifacts/ per problem
- Validator execution and CLI/direct contract preflight run in temporary local
  subprocesses, not security sandboxes; validator modules are not imported in
  the parent CLI/runtime process during preflight
- `eval_stages[].mode: candidate_runner` can execute a task-declared language
  command and optional build command without a shell. Host execution inherits
  host network and is not sandboxed. An OCI build execution environment uses a
  digest-pinned image, disables candidate build/run network, makes the image
  root filesystem read-only, drops capabilities, and applies bounded resource
  flags; an optional missing-image pull still uses host registry access. This
  is process isolation, not a hostile-code security sandbox. The problem-owned
  Python validator remains metrics authority and receives only the bounded/
  redacted runner record.
- Candidate build declarations may name ordered `toolchain_candidates`, a
  `{toolchain}` version probe, optional executable/version-output SHA-256 pins,
  candidate lock-file hashes, and an `execution_environment`. The default
  `host_subprocess_v1` identity is same-host evidence. The optional
  `oci_container_v1` path accepts Docker/Podman, requires an immutable image
  digest, verifies observed image/runtime identity, and retains ordered
  in-image probe and provisioning evidence; it does not certify daemon
  locality, platform parity, package restoration, or cross-host replay.
  `candidate_runner_python_oci` is the smoke fixture; its live daemon test is
  opt-in with `LIBREEVOLVE_RUN_OCI_FIXTURE=1`.
- `initial_programs/seed_policy.yaml` may set `primary_file` for every seed
  workspace. Without it, seed-workspace primary selection remains `main.py`,
  then `seed.py`, then the first Python path.
- SEARCH/REPLACE diff format: use canonical AlphaEvolve fences
  `<<<<<<< SEARCH\n...\n=======\n...\n>>>>>>> REPLACE`; the compact
  `<<<SEARCH\n...\n===\n...\n>>>REPLACE` spelling remains accepted as
  compatibility input.
- Diff engine strips a single outer markdown fence wrapper automatically
- `mutation_mode: adaptive` selects `full` for threshold-eligible short,
  single-file workspaces and `diff` otherwise, unless task preference or recent
  same-parent selected-mode failures override the shape decision. Opposite-
  format responses can use the configured parser fallback. Runtime evidence is
  under `runtime.history.adaptive_mutation_mode_report`; benchmark-calibrated
  thresholds and equal-budget diff/full/adaptive evidence remain open.
- VALID_THRESHOLD = 0.0 is the pre-admission eligibility gate. A valid finite
  program with score >= 0 is passed to ProgramDatabase.admit(), but MAP-Elites
  cell replacement/elite retention can still reject it (for example
  reason="not_improving_cell"), and only retained/search-state entries become
  sampling_eligible.
- Default `mixed` parent sampling uses 30% explore / 70% exploit; explicit
  parent-selection strategies bypass that ratio
- `async_llm_sampling` is opt-in local proposal concurrency: sibling prompts are
  prepared from pre-batch archive state, worker-owned LLM ensembles run through
  a bounded Python `asyncio` queue, results merge in proposal order, and rewards
  are serialized through the owning worker. `async_candidate_evaluation` is the
  separate bounded local evaluation queue. Either or both can be enabled;
  shared archive/history/budget mutations remain main-thread ordered.
  `async_generation_window > 1` additionally permits bounded later-generation
  sampling from pre-drain archive, prompt-program/reward, and sampler-reward
  state while prior-generation evaluation is in flight; merged task intervals
  prove observed overlap and generation-grouped drains preserve admission/hook
  order. Finite cumulative evaluator limits other than `max_evaluations` retain
  the generation barrier because their pending cost cannot be reserved exactly.
  This is not distributed execution, a full dependency scheduler, or pending-
  work resume.
- The checked matrix cascade fixture executes four pinned seeds over known
  rank-7/rank-8 2x2 controls and emits per-seed traces; it is deterministic
  calibration, not Strassen rediscovery or AlphaEvolve-scale search evidence
- The checked matrix evolution fixture runs four independent run-local
  `evolve()` calls and records causal parent/lineage, budget, history, and
  cascade evidence under a scripted rank-7 mutation control; it is normal
  pipeline evidence, not stochastic LLM discovery or Section 3.1 scale
- Failed/rejected candidates are persisted to `failure_history.jsonl`, exact
  workspace duplicate/cache audit rows are persisted to
  `duplicate_work_cache_index.jsonl`, and
  prompts render bounded recent failure memory with configurable filters and
  limits; durable cross-run failure tables, semantic failed-proposal
  retrieval, learned repetition avoidance, replayable failed-mutation
  payloads, failure-aware sampling policy, and cross-run failure-index
  migrations remain open work and are tracked by
  `papers/failure_memory_boundary.json`

## Running Tests

Human-facing development workflow details live in `docs/development.md`.
Agent-doc invariants are checked by `tests/test_agents_docs.py` and the
`.github/workflows/tests.yml` paper/docs job.

```bash
py -3.12 -m pytest tests/ -m "not integration" --tb=short
py -3.12 -m pytest tests/integration/ -m integration          # needs ANTHROPIC_API_KEY
```

## Running the Tool

Backend details live in `docs/backends.md`, run artifacts in
`docs/run-artifacts.md`, and paper/source boundaries in `papers/README.md`.
The built-in backend families are OpenAI, Anthropic, Google Gemini, Ollama, and
custom import-path backends.

```bash
py -3.12 -m libreevolve run libreevolve/problems/examples/hello_world --max-generations 10 --backends "openai:<openai-model-id>"
py -3.12 -m libreevolve show runs/hello_world
```

Replace placeholder backend model ids with currently available provider/account
model ids before running.

## Common Pitfalls

- OpenAI uses Chat Completions by default; explicit `api_mode: responses` or
  configured `reasoning_effort` routes through the Responses API. `api_mode:
  auto` without reasoning preserves Chat Completions even for model strings
  that may support reasoning
- xhigh reasoning effort can consume entire token budget on thinking — use high or increase max_output_tokens
- Models add markdown fences around diffs — _strip_fences() handles one outer response wrapper
- Models add comments that break diff matching — prompt says "No comments"
- The seed program should be intentionally suboptimal to give evolution room to improve
- For non-Python primaries, `best_workspace/` is the authoritative export;
  `best.py` remains a legacy primary-text compatibility artifact.
- `config.seed` initializes the run-local framework `random.Random`; `evolve()`
  no longer reseeds Python's process-global `random` module
