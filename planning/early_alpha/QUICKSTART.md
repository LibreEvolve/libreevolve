# Local alpha quickstart draft

The maintained user guide is [docs/alpha-quickstart.md](../../docs/alpha-quickstart.md).
This planning draft is retained as historical scope, not the installation guide.

Status: engineering preview in development. Package, live-model, and independent
user gates are pending. Reference environment: Windows, Python 3.12.

## Install and prepare

The release candidate will supply a wheel and SHA-256. Install that wheel into
a new Python 3.12 virtual environment; confirm `libreevolve --help` works there.
The final install command and package hash will be recorded after packaging.

Set `OPENAI_API_KEY` in your shell using your provider credential. Keep it out
of task files and version control. Select a model your account can access and
check its current input/output token prices. The existing CLI also loads `.env`
with override enabled, so a matching `.env` value takes precedence over your shell.

Create a task, replacing MODEL_ID and TOKEN_PRICE with actual values:

```text
libreevolve alpha init packing-task --model MODEL_ID --token-price TOKEN_PRICE --budget-usd 1
libreevolve alpha doctor packing-task
libreevolve run packing-task --run-name packing-first --progress
libreevolve show runs/packing-first
libreevolve alpha report runs/packing-first --output packing-first.html
libreevolve alpha export runs/packing-first verified-first
```

`TOKEN_PRICE` is USD per million tokens. Use a conservative rate, at least the
higher input/output rate. The $1 example is a configurable per-run estimate,
not authorization for agent spending and not a provider billing guarantee.
An in-flight call can exceed a threshold; model pricing, missing usage and
provider billing may differ. Review config.yaml before running.

Defaults bound the run to 10 generations, 11 evaluations, 10 provider attempts,
60,000 reported tokens and 900 seconds, checked at framework boundaries.
Provider calls and evaluations also have individual timeouts. Retries and
fallback are disabled for this path. Give each run a new name; existing results
are protected by the collision check.

`alpha doctor --offline` checks task/configuration without requiring credentials.
Normal doctor checks local provider setup but does not establish model access;
only a real request can establish that. To test seed evaluation without spending:

```text
libreevolve run packing-task --max-generations 0 --run-name packing-seed-only --progress
```

## Understand the experiment

The candidate implements `pack(items, capacity)` in `initial_programs/seed.py`.
Correctness requires packing every item exactly once without exceeding capacity.
Higher quality means fewer bins on the same fixed corpus. The seed uses next-fit;
improvement is possible but is never guaranteed. Only candidate workspace files
are editable by evolution. The validator and held-out corpus stay outside that
workspace. Local execution inherits host access and is not a security sandbox.

Successful runs export `best_workspace/`; `best.py` is a compatibility copy.
The report and export commands independently verify the selected candidate on
held-out cases and bind results to its code hash. Open packing-first.html in your
browser. The explicit export writes solution.py and verification.json into a
new directory. Existing outputs are protected; choose a new name for each one.

Press Ctrl+C to cancel. Inspect `manifest.json`, `history.jsonl` and failure
artifacts in the run directory. Cancellation can leave saved candidate history
without a completed best-workspace export. Abrupt termination can also interrupt
the latest write. Do not treat a partial run as completed.

Advanced restore composes saved RNG, scheduler, archive and budget state when
the required artifacts validate. It does not resume pending provider/evaluator
work or promise bit-for-bit model replay. Use a new run directory and consult
`libreevolve run --help` before restoring.
