# Documentation

These notes document the current implementation of LibreEvolve. They are intended
to make the codebase easier to understand and extend without forcing readers to
infer behavior from tests and source.

- [Architecture](./architecture.md): End-to-end runtime flow and component roles.
- [Problem Format](./problem-format.md): Required files and the validator
  contract for custom problems.
- [Configuration](./configuration.md): `Config` fields, CLI overrides, and
  `config.yaml` behavior.
- [Plugins](./plugins.md): Hook order, built-in plugins, and extension guidance.
- [Backends](./backends.md): OpenAI, Anthropic, and Ollama backend behavior.
- [Run Artifacts](./run-artifacts.md): What gets written under `runs/`.
- [Development](./development.md): Local setup, tests, and contributor workflow.
- [Paper Cache](../papers/README.md): Local paper roles, implementation status,
  and benchmark coverage decisions.

When these documents disagree with an aspiration mentioned elsewhere in the
repository, prefer the code and tests. The goal here is to describe how the
system behaves today.
