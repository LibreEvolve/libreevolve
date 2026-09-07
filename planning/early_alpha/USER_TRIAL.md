# Independent developer trial

Status: prepared; no participants contacted and no results collected.
Recruit 3–5 developers who did not build LibreEvolve, after authorization to
contact them. Use participant IDs, not credentials or personal data, in records.

## Reference conditions

Record the candidate commit, wheel SHA-256, OS, Python version, model ID,
provider price source/date, and approved spending ceiling. Use a new virtual
environment and a fresh task/run directory. Do not silently substitute a source
checkout for the wheel. Record installation time separately from run time.

For the Codex OAuth reference route, record CLI version, ChatGPT-login route,
model and reasoning setting instead of inventing a token price. Record explicit
subscription-use authorization and per-run/aggregate call and runtime limits;
charges and remaining quota are unknown. The documented live route is
Linux/WSL Python 3.12 with Luna/high. Native Windows offline installation
evidence is separate from live-provider and cancellation evidence.

Each participant receives the quickstart, wheel, and an assigned per-run budget.
They supply their own credential locally. No credential values enter feedback,
screenshots, run bundles, or reports.

## Prepared candidate packet (2026-09-07)

- Package commit: `8fdbf5132ed24b2960bde4c9f7acf14b28aadf59`.
- Wheel: `dist/8fdbf513/libreevolve-0.1.0-py3-none-any.whl`.
- Wheel SHA-256: `b26f82c66b3397643cd0fc36e6318c6202797b561ac077e78c975031db18d999`.
- Send the wheel, matching provenance JSON, `docs/alpha-quickstart.md`, this
  protocol, and the final handoff together; no public package index is implied.
- Tested live reference: Linux/WSL, Python 3.12.13, Codex CLI 0.153.4,
  `gpt-5.6-luna`, explicit `high` reasoning, participant-owned ChatGPT login.
- Proposed allocation per participant, subject to that participant's approval:
  one default three-call/four-evaluation/900-second run, plus one cancellation
  exercise capped at one call/two evaluations/240 seconds; each CLI invocation
  has a 180-second deadline. For 3–5 participants this is at most 12–20 CLI
  invocations. It is not a subscription charge or token guarantee.
- Use a separately initialized task for the cancellation exercise and pass
  `--max-generations 1 --max-llm-calls 1 --max-llm-provider-attempts 1
  --max-evaluations 2 --max-runtime-seconds 240` to `run` before pressing Ctrl+C.
- No participant enrollment, contact, authorization, feedback or timing result
  has been recorded. Prepared materials do not prove unassisted completion.

## Tasks

1. Install the wheel and create the bin-packing experiment.
2. Explain the configured limits before starting. Identify which are estimates.
3. Run local preflight and resolve any reported setup problem.
4. Start a real-model experiment and locate progress information.
5. Inspect its report; explain whether it improved and whether correctness passed.
6. Locate/export the selected program and independently verify it.
7. Start a second run, cancel it, and explain what remains recoverable.

The observer logs every request for assistance and every intervention. Do not
repair the participant's environment silently. Stop when the approved budget
is reached. An unsuccessful optimization is still a valid usability observation.

## Per-participant record

- Participant ID and prior Python/CLI experience:
- Candidate commit / wheel hash / OS / Python / model:
- Approved maximum spend and actual/estimated spend:
- Installation start/end:
- First experiment start/end:
- Time to independently verified export:
- Setup failures (step, error, recovery):
- Assistance (step, question, intervention):
- Could explain baseline/best, correctness, stopping reason, cost uncertainty:
- Cancellation state and recovery understood:
- Completed within approximately 30 minutes:
- Most confusing step and requested improvement:

## Decision

Report every participant, completion rate, time range, failures, and interventions.
Any common blocker produces a concrete repair and a fresh trial of that step.
Synthetic tests and maintainer walkthroughs are separate evidence and do not fill
participant rows. The external trial gate remains pending until observed.
