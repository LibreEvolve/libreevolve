# Engineering-preview quickstart

This page is the canonical command source for the public engineering preview.
It describes a source checkout and keeps offline setup separate from the
optional Codex OAuth route. The preview searches bounded changes to a small
Python bin-packing heuristic; it does not promise improvement.

## Support matrix

| Environment | What is declared or documented | Evidence boundary |
| --- | --- | --- |
| Python `>=3.11` | Declared in `pyproject.toml` as the package compatibility floor. | Metadata allowance, not a complete validation matrix. |
| Python 3.12 on Linux/WSL | Reference installation and command route below. | Earlier live model evidence used this family before the current cleanup; the commands below are not a new live run. |
| Windows with Python 3.12 | Installation and offline preflight are documented with PowerShell paths. | Native Windows Codex execution and external usability remain unvalidated. |
| Other Python/OS combinations | Not the documented reference route. | Validate separately before treating them as supported. |

No public package-registry install is advertised. Install from the checked-out
source tree. Use a fresh clone, virtual environment, task directory and output
names; the commands protect existing destinations rather than overwriting them.

## 1. Clone and install from source

The public repository target is
`https://github.com/LibreEvolve/libreevolve`. The commands below use the
repository's source packaging; they do not claim a PyPI release.

### Linux or WSL

```bash
git clone https://github.com/LibreEvolve/libreevolve.git
cd libreevolve
python3.12 -m venv .venv
.venv/bin/python -m pip install -e '.[dev]'
.venv/bin/python -m pip check
```

### Windows PowerShell

```powershell
git clone https://github.com/LibreEvolve/libreevolve.git
Set-Location libreevolve
py -3.12 -m venv .venv
& .\.venv\Scripts\python.exe -m pip install -e ".[dev]"
& .\.venv\Scripts\python.exe -m pip check
```

The examples below use the Linux/WSL executable paths. On Windows, replace
`.venv/bin/python` and `.venv/bin/libreevolve` with
`.venv\Scripts\python.exe` and `.venv\Scripts\libreevolve.exe`.

## 2. Initialize and run the offline preflight

Initialization copies the checked-in bin-packing task into a new directory and
makes no provider call. The offline doctor checks the task and evaluator
contract, skips credential checks, and still does not request a model response.

```bash
.venv/bin/libreevolve alpha init packing-task
.venv/bin/libreevolve alpha doctor packing-task --offline
```

The initializer writes `packing-task/config.yaml` with the validated
Codex OAuth lane (`gpt-5.6-luna`, high reasoning), bounded local call,
evaluation and runtime settings, and no token or dollar cap. Review the file
before any live request. A login or offline pass does not establish model
access, optimization, billing, or external usability.

## 3. Exercise the seed-only path

Use a new run name. `--max-generations 0` evaluates only the seed and makes no
model request; it is an offline pipeline check, not optimization or evidence
of provider access.

```bash
.venv/bin/libreevolve run packing-task --max-generations 0 --run-name seed-check --progress
.venv/bin/libreevolve show runs/seed-check
.venv/bin/libreevolve alpha report runs/seed-check --output seed-check.html
.venv/bin/libreevolve alpha export runs/seed-check verified-seed
```

The inspection reads the saved run. The report writes a new local HTML file
after reevaluating the on-disk `runs/seed-check/best_workspace/seed.py` in
timed local subprocesses; it does not make a provider call or substitute a
history candidate. The export creates `verified-seed/solution.py` and
`verified-seed/verification.json` after fresh training and held-out checks,
including the candidate SHA-256 and source-selection evidence. These outputs
are local artifacts, not a published example.

The report has no source selector: it always checks the on-disk workspace when
that artifact is available and surfaces missing, corrupt or mismatched state.
Only `alpha export` supports an explicit `--source history` or
`--source workspace` choice when the saved history and workspace differ.

## 4. Optional live Codex route

Only continue after reviewing the limits and explicitly authorizing your own
subscription use. The supported public lane requires a Codex CLI on `PATH` and
an authorized ChatGPT/OAuth login; API-key authentication is not this lane.

First check local setup without requesting a model response:

```bash
codex login
.venv/bin/libreevolve alpha doctor packing-task
```

Then review `packing-task/config.yaml` and choose a fresh run name before the
bounded request:

```bash
.venv/bin/libreevolve run packing-task --run-name live-check --progress
```

The initialized defaults allow three CLI calls, four evaluations, 900 seconds
per run, 180 seconds per CLI call, 10-second evaluator timeouts, and no retry
or fallback. These are local work bounds, not hard token or dollar limits.
Subscription charges, quota, and in-flight usage may remain unknown. A real
request is live product use; this document does not claim that it succeeds.

## Output collisions and source selection

The CLI fails closed rather than overwriting existing output:

- `alpha init DESTINATION` requires a new task directory.
- `--run-name NAME` requires a new `runs/NAME` directory.
- `alpha report ... --output FILE.html` requires a new, non-symlink file.
- `alpha export RUN DESTINATION` requires a new destination directory.

Export normally selects the saved candidate and checks a matching
`best_workspace/` copy. If the workspace bytes differ from saved history, the
command requires an explicit source choice:

```bash
.venv/bin/libreevolve alpha export RUN DESTINATION --source workspace
.venv/bin/libreevolve alpha export RUN DESTINATION --source history
```

Choose the source deliberately; do not edit metadata to bypass a failed
validation. Export records the selected source and its identity; the report
records the on-disk workspace it checked and never selects history.
See [saved artifacts](run-artifacts.md) for the artifact contract and
[reading results](results.md) for interpretation.

## Cancellation and incomplete state

Press Ctrl+C during a run. The CLI exits with code 130 and attempts to preserve
an aborted manifest and best-so-far artifacts. Local process cleanup does not
prove remote provider cancellation or that subscription usage stopped. Forced
termination or persistence failure can leave incomplete artifacts; inspection
and export fail closed when required state is absent.

## Candidate and evaluator boundary

The candidate implements `pack(items, capacity)` in
`packing-task/initial_programs/seed.py`. Training and held-out cases are
separate; holdout results must not drive prompts, selection, tuning or stopping.
Quality is a bin-packing measure for a named corpus, not accuracy or speed.

Candidate and validator Python execute in timed local subprocesses with host
access. This is not a security sandbox. Use trusted tasks and an appropriately
isolated development environment. Review [safety and scope](safety.md) before
sharing source, logs or HTML.
