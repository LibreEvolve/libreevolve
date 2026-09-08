# Engineering-preview release checks

This checklist prepares a reviewable candidate. It does not authorize a merge,
release, registry upload, deployment, DNS change, billing change, CI repair or
marketing publication.

## Source and scope

1. Verify the intended `LibreEvolve/libreevolve` remote and exact candidate
   head in an isolated worktree.
2. Preserve unrelated changes and stage only the approved paths.
3. Confirm the README and docs still label the product as an engineering
   preview and preserve the Codex OAuth scope, host-access warning and usage
   uncertainty.
4. Check that roadmap items and unvalidated platform routes are not presented
   as current capabilities.

## Offline and distribution evidence

1. Run the retained offline test suite.
2. Build both wheel and sdist.
3. Check that both artifacts contain the bin-packing task assets and required
   Python modules, without experimental providers or private collections.
4. Install the wheel in a fresh environment outside the checkout and follow
   the [quickstart](alpha-quickstart.md): `pip check`, initialization, offline
   doctor, zero-generation seed run, inspection, HTML report and verified
   export.
5. Exercise output-collision and source-conflict protection. A candidate export
   must record its hash and fresh named training/held-out checks.
6. Record source and distribution identities with
   `python3.12 -m libreevolve.tools.release_artifact_provenance`.

Offline execution is not new live model evidence, external-usability evidence,
hosted CI evidence or a benchmark claim. A zero-generation run makes no model
request. Any real Codex request needs separate authorization for subscription
use.

## Public release gates

Before publication, independently verify the target repository, branch and
candidate head, then obtain the required approval for each action. The public
source target is [LibreEvolve/libreevolve](https://github.com/LibreEvolve/libreevolve);
no package-registry availability or deployment is implied by this link.

Keep workflows manual-only while the existing billing pause is unresolved. Do
not force-push, repair unrelated CI, publish private research, or infer
cross-platform live parity from one host.
