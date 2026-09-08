# LibreEvolve

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-mark.svg">
  <img src="assets/logo-mark-light.svg" alt="LibreEvolve" width="80" height="80">
</picture>

**Evolve code. Show the evidence.**

LibreEvolve is an open-source workbench for inspectable code-evolution
experiments. **Engineering preview: bounded Python bin-packing optimization
with Codex OAuth.** It starts from a small Python heuristic, searches a bounded
local space of changes, records candidate workspaces and evaluations, and lets
you inspect a saved run before a fresh export check.

The product is an experiment you can examine, not a promise that every search
improves code. No improvement is a valid result. A successful named check is
not proof of universal correctness, optimality, security, or performance.

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

The broader research platform, additional providers, plugins, examples, papers
and experimental tools live in the private
[experimental repository](https://github.com/LibreEvolve/libreevolve-experimental);
they are not capabilities of this public engineering preview.

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
