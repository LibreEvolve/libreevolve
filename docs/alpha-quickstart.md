# Engineering preview quickstart

LibreEvolve runs bounded local optimization of a Python bin-packing heuristic.
The reference model lane is Codex OAuth with `gpt-5.6-luna` and `high` reasoning.
Earlier live validation used Linux/WSL, Python 3.12.13 and Codex CLI 0.153.4.
That evidence predates the branch cleanup; offline tests are not new live
model evidence. External usability remains unvalidated.

## Install and initialize

Use Python 3.12 and install from this checkout:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/python -m pip check
.venv/bin/libreevolve alpha init packing-task
.venv/bin/libreevolve alpha doctor packing-task --offline
```

On Windows, create the environment with `py -3.12 -m venv .venv` and use
`.venv\Scripts\python.exe` and `.venv\Scripts\libreevolve.exe`.
Native Windows Codex execution is not the validated live route.

For optimization, a working Codex CLI must be on PATH with an authorized
ChatGPT/OAuth login. Use `codex login`; API-key authentication is not the
supported lane. A saved login does not prove account-specific model access.
`alpha doctor packing-task` checks local executable/login status without
requesting a model response.

## Run, inspect and export

Review `packing-task/config.yaml` and authorize your subscription use before
running:

```bash
.venv/bin/libreevolve run packing-task --run-name packing-first --progress
.venv/bin/libreevolve show runs/packing-first
.venv/bin/libreevolve alpha report runs/packing-first --output packing-first.html
.venv/bin/libreevolve alpha export runs/packing-first verified-first
```

Open the HTML file in your browser. The export contains `solution.py` and
`verification.json`, which binds fresh training and held-out correctness
results to the candidate's SHA-256. Existing output files/directories are not
overwritten. Use fresh run, report and export names each time.

To exercise the pipeline without a model request, add `--max-generations 0`
to the run command. This evaluates only the seed: it is not optimization or
proof of provider access.

Defaults allow three CLI calls, four evaluations, 900 seconds per run and
180 seconds per CLI call, with no retries or fallback. Evaluations have a
10-second timeout. These are local work bounds. Subscription quota and charges
may be unknown; no dollar cap or hard token limit is claimed. Reported tokens
are observational, and interruption or timeout may leave usage incomplete.

## Results and cancellation

The report separates run status, candidate correctness, training quality,
held-out quality and recorded usage. Higher quality means fewer bins on the
same corpus. Compare within a split, not across training and held-out splits.
No improvement is a valid outcome; passing these cases does not prove
optimality or general performance.

Press Ctrl+C to cancel. The CLI exits with code 130 and points to saved state.
The engine attempts to finalize an aborted manifest and preserve the latest
retained candidate. Local cancellation does not prove remote provider
cancellation or that subscription usage stopped.

Persistence failure or forced termination can leave incomplete artifacts.
The report identifies missing state; inspection/export fail closed when
required validation metadata is absent. Do not edit metadata to force export.
When workspace and history candidates differ, export requires an explicit
`--source workspace` or `--source history`, then independently verifies that
choice.

## Task and execution boundary

The candidate implements `pack(items, capacity)` in
`packing-task/initial_programs/seed.py`. Each item must appear exactly once,
and each bin must fit. The evaluator and 30 held-out cases remain outside
the editable workspace; training uses 55 deterministic cases. Keep held-out
results out of prompts, tuning and stopping decisions.

Candidate Python executes in timed local subprocesses with host access.
This is not a security sandbox. Use trusted tasks and a suitable development
environment. Other providers, research features and examples belong on
`experimental`.
