# LibreEvolve engineering preview

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/logo-mark.svg">
  <img src="assets/logo-mark-light.svg" alt="LibreEvolve Diff Arrow logo" width="80" height="80">
</picture>

LibreEvolve improves a small Python bin-packing heuristic through bounded local
optimization with **Codex OAuth, `gpt-5.6-luna`, high reasoning**.

`main` contains the engineering preview. The complete committed research
platform, other providers, plugins, examples, papers and experimental tools
are preserved with their Git history in the private
[experimental repository](https://github.com/LibreEvolve/libreevolve-experimental).

## Start here

Use Python 3.12. From this checkout on Linux/WSL:

```bash
python3.12 -m venv .venv
.venv/bin/python -m pip install .
.venv/bin/libreevolve alpha init packing-task
.venv/bin/libreevolve alpha doctor packing-task --offline
```

On Windows, use `py -3.12 -m venv .venv` and the executables in
`.venv\Scripts\`. The earlier live model workflow was validated on Linux/WSL;
native Windows live Codex execution and external usability remain unvalidated.

A working Codex CLI and an authorized ChatGPT/OAuth login are required for
optimization. Read the [quickstart](docs/alpha-quickstart.md) before authorizing
subscription use.

```bash
.venv/bin/libreevolve alpha doctor packing-task
.venv/bin/libreevolve run packing-task --run-name first --progress
.venv/bin/libreevolve show runs/first
.venv/bin/libreevolve alpha report runs/first --output first.html
.venv/bin/libreevolve alpha export runs/first verified-first
```

Add `--max-generations 0` to the run command for a seed-only check without a
model request. This is not optimization or evidence of provider access.

## Scope and limits

- Defaults: three model calls, four evaluations, 900 seconds per run,
  180 seconds per Codex call, and no retries or fallback.
- Subscription quota and charges may be unknown. Reported tokens are
  observational; there is no hard token or dollar-cap claim.
- Ctrl+C attempts to stop the local process tree and save an aborted run with
  its best retained candidate. This does not prove remote work or billing stopped.
- Inspection and export reject inconsistent required artifacts. Export freshly
  checks the selected candidate on training and held-out cases and records its hash.
- Candidate and validator execution are local subprocesses, **not a security
  sandbox**. Use trusted tasks and an appropriately isolated machine.
- Earlier live evidence predates this cleanup. Offline tests and package smoke
  checks do not establish a new live run, general performance, or usability.

Documentation: [quickstart](docs/alpha-quickstart.md),
[saved artifacts](docs/run-artifacts.md), [development](docs/development.md),
[release checks](docs/release-checklist.md).

[MIT license](LICENSE).

[Original artwork and branding preview](assets/branding/README.md).
