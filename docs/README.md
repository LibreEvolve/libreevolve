# Documentation

These notes document the current implementation of LibreEvolve. They are intended
to make the codebase easier to understand and extend without forcing readers to
infer behavior from tests and source.

Use the root [README](../README.md) as the practical entry point for install,
smoke checks, provider-backed first runs, current limits, and repository layout.
Use this directory for operational details and the fuller implementation-status
ledger. Use [ROADMAP](../ROADMAP.md) and the [TODO ledgers](./todo/) for
implementation gaps. Use [papers/README.md](../papers/README.md) for
paper/source status and claim boundaries.

## Reader Paths

- New user: start with the root README, run the provider-free smoke command,
  then read [Problem Format](./problem-format.md) before creating a custom
  problem.
- Operator/debugger: use [Run Artifacts](./run-artifacts.md),
  [Configuration](./configuration.md), and [Backends](./backends.md).
- Contributor: use [Development](./development.md), then the active TODO files
  under [todo](./todo/).
- Paper/spec reviewer: use [Current Status](./status.md),
  [ROADMAP](../ROADMAP.md), and [papers/README.md](../papers/README.md).

## Operational Guides

- [Architecture](./architecture.md): End-to-end runtime flow and component roles.
- [Problem Format](./problem-format.md): Required files and the validator
  contract for custom problems.
- [Configuration](./configuration.md): `Config` fields, CLI overrides, and
  `config.yaml` behavior.
- [Plugins](./plugins.md): Hook order, built-in plugins, and extension guidance.
- [Backends](./backends.md): built-in and custom backend behavior, including
  the Google/Gemini provider-parity absence boundary.
- [Run Artifacts](./run-artifacts.md): What gets written under `runs/`.
- [Current Status](./status.md): Detailed implemented-versus-absent capability
  ledger moved out of the root README.
- [Development](./development.md): Local setup, tests, and contributor workflow.
- [Paper Cache](../papers/README.md): Local paper roles, implementation status,
  and benchmark coverage decisions.

## Documentation Boundaries

- The root README should stay short enough to be useful on a first read.
- Detailed runtime behavior belongs in the operational guides above.
- The full implementation and absence-boundary ledger belongs in
  [status.md](./status.md).
- Long-term status belongs in `ROADMAP.md` and `docs/todo/`.
- Paper-derived claims belong in `papers/README.md` and validated JSON sidecars.
- AlphaEvolve-alignment cleanup is a whole-documentation task. When a claim is
  tightened or a missing feature is identified, check the root README,
  operational guides, `docs/status.md`, `ROADMAP.md`, `papers/README.md`, paper
  sidecars, and the active/completed TODO ledgers for matching wording.

When these documents disagree with an aspiration mentioned elsewhere in the
repository, prefer the code and tests. The goal here is to describe how the
system behaves today.
