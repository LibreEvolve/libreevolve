# LibreEvolve

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-mark.svg">
  <img src="assets/logo-mark-light.svg" alt="LibreEvolve" width="80" height="80">
</picture>

**Evolve code. Show the evidence.**

LibreEvolve is an **open-source workbench for inspectable code-evolution
experiments**. **Engineering preview: bounded Python bin-packing optimization
with Codex OAuth.**

It starts from a deliberately simple Python bin-packing heuristic, searches a
bounded local space of changes, and saves every candidate workspace and
evaluation so you can read the evidence yourself — before a fresh export check
re-runs the candidate you chose.

The product is an experiment you can examine, not a promise that every search
improves code. No improvement is a valid result. A successful named check is
not proof of universal correctness, optimality, security, or performance.

## What makes it worth inspecting

| | |
| --- | --- |
| **Bounded by design** | Local call, evaluation and runtime limits keep a run small enough to follow. They are not token or dollar caps, and subscription usage may stay unknown. |
| **Saved, not summarized** | Candidate workspaces, evaluations, archive events and LLM calls land in a run directory you can read. |
| **Honest by construction** | Run status, validity, quality, retention and usage stay separate, so a finished run is never mistaken for a win. |
| **Checked again before use** | Reports and exports re-run the selected candidate in fresh local subprocesses instead of trusting old metadata. |

## What is available today

- A source install for the public engineering-preview checkout.
- Local initialization and an offline task/evaluator preflight that makes no
  provider request.
- One documented model lane: Codex OAuth with `gpt-5.6-luna` and high
  reasoning. A local login does not prove account-specific model access.
- Bounded runs whose saved artifacts can be inspected with their status,
  validity, quality, retention and usage kept distinct.
- A local HTML report and an export that freshly checks the selected candidate
  on named training and held-out cases.

An approved inspectable example viewer is not included in this branch. The
seed-only flow in the quickstart is an onboarding check, not an optimization
result or live-model demonstration.

Research features, additional providers, plugins, papers and experimental tools
are out of scope for this checkout; they are not capabilities of this public engineering preview.

## How a run moves

1. **Seed.** Initialize the bundled bin-packing task and inspect its
   intentionally simple heuristic.
2. **Change.** Propose and evaluate bounded local changes — optionally through
   the Codex OAuth lane, after you authorize your own subscription use.
3. **Inspect.** Read the saved run. Completion, validity, training quality,
   retention and recorded usage are separate dimensions, so a finished run is
   not the same as a retained win.
4. **Verify.** Freeze your selection, then let a fresh export check it on named
   training and held-out cases and record its identity.

**Run the preview** through the [canonical quickstart](docs/alpha-quickstart.md).

## Start with the canonical quickstart

The complete clone, source-install, offline, seed-only and live authorization
path is maintained in [the engineering-preview quickstart](docs/alpha-quickstart.md).
It is the command source for the other docs; use a fresh destination whenever
the CLI says an output already exists.

Before authorizing subscription use, read [safety and scope](docs/safety.md)
and [how to read a result](docs/results.md). Candidate execution has host
access and is not a security sandbox. Local call and runtime bounds are not
dollar or hard-token limits; subscription charges and quota may remain unknown.

## Support boundary

The package metadata declares Python `>=3.11`. The documented reference route
uses Python 3.12 on Linux/WSL. Windows installation and offline checks are
documented, while native Windows Codex execution and external usability remain
unvalidated. See the support matrix in the [quickstart](docs/alpha-quickstart.md)
for the evidence boundary.

## Read, contribute and release

- [Documentation index](docs/README.md)
- [Quickstart and command reference](docs/alpha-quickstart.md)
- [Reading saved results](docs/results.md)
- [Safety and scope](docs/safety.md)
- [Saved artifact contract](docs/run-artifacts.md)
- [Contributing](docs/contributing.md)
- [Development checks](docs/development.md)
- [Roadmap and present/future boundary](docs/roadmap.md)
- [Release checklist](docs/release-checklist.md)

Contributions should preserve the engineering-preview scope, keep training and
held-out evaluation separate, and include focused offline tests. The project
does not advertise a public package-registry install; install from a checked-out
source tree as described in the quickstart.

## Project links

- [Source repository](https://github.com/LibreEvolve/libreevolve)
- [Issues and requests](https://github.com/LibreEvolve/libreevolve/issues)
- [Documentation in the repository](https://github.com/LibreEvolve/libreevolve/tree/main/docs)

[MIT license](LICENSE).
