# Contributing

Contributions should make the engineering preview easier to inspect without
expanding its public scope. Keep `LibreEvolve` as the display name and
`libreevolve` as the package, import and command identifier.

## Before opening a change

1. Start from a fresh branch based on the current public head.
2. Read the [quickstart](alpha-quickstart.md) and [safety boundary](safety.md).
3. Decide whether the change affects source behavior, artifact interpretation,
   documentation, or only presentation.
4. Preserve training/held-out separation, local usage uncertainty and the
   host-access execution warning.

Do not add a provider, claim universal optimization, imply a secure sandbox,
turn offline checks into live evidence, or add a package-registry install
instruction without separately verified release evidence.

## Local checks

Run focused tests for the changed path, then the retained offline suite and
package build checks described in [development](development.md). Ordinary
verification must not load API-key files or make a model request. If a change
needs live Codex use, document the separate authorization and exact limits
instead of making it an incidental test.

For documentation changes, check local links, command signatures, collision
behavior, source-history selection and the distinction between a seed-only
check and optimization. Keep command examples in the canonical quickstart;
other docs should link to it rather than drift.

## Review and pull requests

Describe the exact branch/head, changed paths, tests run and remaining limits.
Separate source inspection, offline execution, live model evidence, browser
checks, hosted CI and publication. Include a small reproducible example for
behavior changes, but do not include raw prompts, credentials, home paths or
private candidate code.

Authors do not approve their own claims or release evidence. A review of local
docs does not approve a merge, deployment, release, public metadata change or
marketing publication.
