# Safety and scope

LibreEvolve is a local engineering preview. Read these boundaries before
initializing a task or authorizing subscription-backed Codex work.

## Scope

The public lane is bounded Python bin-packing optimization through Codex OAuth,
using the validated `gpt-5.6-luna` model with high reasoning. Other providers,
plugins, research features and broader repository optimization are not public
preview capabilities. The category language describes project direction; the
shipping qualifier describes what this checkout supports.

The implementation workforce's model settings do not change the product lane.
The package metadata's Python `>=3.11` declaration is not proof of live parity
on every operating system. The documented reference is Python 3.12 on
Linux/WSL; native Windows Codex execution and external usability remain
unvalidated.

## Code execution

Candidate and validator code runs in timed local subprocesses with host access.
This is not a security sandbox or a hostile-code isolation boundary. Use trusted
tasks and an appropriately isolated development machine. Do not run an
untrusted candidate or task merely because a local check passes.

The report command reevaluates candidate Python before writing its local HTML.
The pure HTML renderer escapes assembled values and has no active content, but
that rendering property does not make candidate execution safe.

## Credentials and subscription use

The public lane uses a local Codex CLI with a ChatGPT/OAuth login. API-key
authentication is not the documented lane. Keep credentials, auth homes and
raw provider traces outside the repository and never paste them into a task,
run artifact or issue.

Offline initialization, offline doctor checks and a zero-generation seed run
make no model request. A successful offline check is not model access evidence.
Before a live run, inspect the generated configuration and authorize your own
subscription use. The local limits bound calls, evaluations and runtime; they
are not hard token or dollar caps. Subscription charges, quota and interrupted
in-flight usage may remain unknown.

## Data and sharing

Runs, prompts, source, logs and HTML are local research data by default. Review
and sanitize an artifact before sharing it. Redaction reduces accidental
exposure; it does not guarantee that arbitrary candidate source is safe to
publish. A successful export is not publication approval.

Keep training selection separate from held-out results, and keep held-out
results out of prompts, tuning and stopping decisions. The bundled holdout is a
reporting split, not a secret challenge set. Do not use it to claim general
performance or to build an unapproved leaderboard.

## Cancellation and recovery

Ctrl+C attempts to preserve an aborted manifest and best-so-far artifacts. Local
process cleanup does not prove remote cancellation or stopped subscription
usage. Forced termination and persistence failures can leave incomplete state;
inspection and export should fail closed when required evidence is missing.

For the exact artifact names and source-history mismatch rules, see [saved
artifacts](run-artifacts.md) and [reading results](results.md).
