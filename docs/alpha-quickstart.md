# Local optimization alpha

LibreEvolve searches for better Python bin-packing heuristics and checks each
candidate against a deterministic evaluator. The local workflow is an engineering
preview. Real-model improvement trials and independent user trials are pending.
The reference environment is Windows with Python 3.12.

## Install the candidate

Obtain the candidate wheel and its release_artifact_provenance.json together.
Verify the wheel's SHA-256 against that file before installing it. In PowerShell,
from the directory containing the wheel:

```powershell
Get-FileHash .\libreevolve-0.1.0-py3-none-any.whl -Algorithm SHA256
py -3.12 -m venv .venv
.\.venv\Scripts\python.exe -m pip install .\libreevolve-0.1.0-py3-none-any.whl
.\.venv\Scripts\libreevolve.exe --help
```

The commands below use that environment's executable directly, so PowerShell
activation policy does not affect the example. Installation requires registry
access to download dependencies. No provider request occurs during installation.

## Configure and check

Choose an OpenAI model available to your account. Check its current official
input/output token prices and use at least the higher price as TOKEN_PRICE, in
USD per million tokens. Substitute actual values for MODEL_ID and TOKEN_PRICE:

```powershell
.\.venv\Scripts\libreevolve.exe alpha init packing-task --model MODEL_ID --token-price TOKEN_PRICE --budget-usd 1
.\.venv\Scripts\libreevolve.exe alpha doctor packing-task --offline
```

Set OPENAI_API_KEY locally before the real run. For example, avoid echoing or
putting the key directly into shell history:

```powershell
$alphaKey = Read-Host "OpenAI API key" -AsSecureString
$env:OPENAI_API_KEY = [System.Net.NetworkCredential]::new("", $alphaKey).Password
.\.venv\Scripts\libreevolve.exe alpha doctor packing-task
```

Do not store the key in task files or version control. Existing `.env` values
override shell values in the normal CLI, so review which credential source you
intend to use. Doctor checks local setup; only a real request can confirm model
access. If mutation is disabled by a zero budget, provider checks are labelled
skipped. Review packing-task/config.yaml before starting.

Default limits: 10 generations, 11 evaluations, 10 provider attempts, 60,000
reported tokens, a 900-second run threshold, and your estimated dollar threshold.
Retries and fallback are disabled. Evaluations have 10-second timeouts; provider
calls have 60-second timeouts. Framework thresholds are checked between work
units. An in-flight request can exceed a threshold, failed requests may omit
usage, and actual billing can differ. The estimated dollar limit is not a hard
billing cap. Repeated runs each receive their own limits; budget for their total.

## Run and understand the result

```powershell
.\.venv\Scripts\libreevolve.exe run packing-task --run-name packing-first --progress
.\.venv\Scripts\libreevolve.exe show runs/packing-first
.\.venv\Scripts\libreevolve.exe alpha report runs/packing-first --output packing-first.html
.\.venv\Scripts\libreevolve.exe alpha export runs/packing-first verified-first
Start-Process packing-first.html
```

Each run and output needs a new name. The report shows the baseline and selected
candidate, training and held-out correctness, quality change, source diff,
termination state, model, reported tokens and estimated cost. Missing usage is
shown as unknown/partial. Higher quality means fewer bins on the same corpus;
compare within a split, not scores across different splits. No improvement is a
valid result. A passing correctness check does not promise optimality or general
performance beyond these cases.

The explicit export writes verified-first/solution.py and verification.json.
The latter binds fresh training and held-out results to the exported code's
SHA-256. The report examines best_workspace/seed.py. If that file differs from
saved history, export requires --source workspace or --source history so it
cannot silently switch the candidate you reviewed. Both choices are verified
again before export. Existing output files/directories are never overwritten.

To check the complete local pipeline without spending on a model, run with
--max-generations 0 and a fresh name, then use the same report/export commands.
This evaluates only the seed and is not evidence of model-guided improvement.

## Cancellation and recovery

Press Ctrl+C to cancel. The CLI exits with code 130 and points to saved state.
The engine attempts to write an aborted manifest and export the latest retained
candidate. If persistence fails or the process is forcibly terminated, the latest
work can remain partial. The report distinguishes run status from candidate
verification and identifies missing artifacts. Saved history may still support
an explicit verified export even if the ordinary best export is missing.

Advanced restore composes saved RNG, scheduler, archive and budget state when
the required artifacts validate. It does not resume pending provider/evaluator
work or promise identical model responses. Use a new output directory; consult
`libreevolve run --help` and the run-artifact guide before restoring.

## Adapt the task

The candidate implements `pack(items, capacity)` in initial_programs/seed.py.
Each input item must appear exactly once in the output, and every bin must fit.
The evaluator and held-out cases live outside that editable workspace. Keep
held-out results out of prompts, tuning and stopping decisions. Report/export
commands currently verify this bin-packing interface; a different task needs
its own independent verifier before these commands can support it.

Candidate Python runs in timed local subprocesses with host access. Use a trusted
local task and a suitable development environment; this is not a hostile-code
security sandbox. Paper downloads and hosted execution are outside this workflow.
