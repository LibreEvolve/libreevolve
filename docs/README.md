# Documentation

These notes document the current implementation of LibreEvolve. They are intended
to make the codebase easier to understand and extend without forcing readers to
infer behavior from tests and source.

Use the root [README](../README.md) as the practical entry point for setup,
quick-start commands, current limits, and repository layout. Use this directory
for operational details and the fuller implementation-status ledger. Use
[ROADMAP](../ROADMAP.md) and the [TODO ledgers](./todo/) for implementation
gaps. Use [papers/README.md](../papers/README.md) for paper/source status and
claim boundaries.

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
- Detailed runtime behavior belongs in the operational guides above, while the
  full implementation and absence-boundary ledger belongs in
  [status.md](./status.md).
- Long-term status belongs in `ROADMAP.md` and `docs/todo/`.
- Paper-derived claims belong in `papers/README.md` and validated JSON sidecars.

When these documents disagree with an aspiration mentioned elsewhere in the
repository, prefer the code and tests. The goal here is to describe how the
system behaves today.
