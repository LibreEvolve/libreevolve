# Early alpha implementation evidence

This record separates source-checkout, installed-package, provider, CI, and
external-usability evidence. The packaged candidate is
`8621ea69b4d8bc6c2b5aafec75b8a90056a6a338`; the code is merged at
`a906b53e138c5598edc40c12154f2d5f9635d6df`.

## Follow-up source reliability fix

Local source commit `2b7b7e30` fixes a POSIX verification cleanup race: a
worker that exits after spawning a child is now observed without reaping its
process-group leader, the inherited session is killed, and group disappearance
is boundedly awaited. The focused descendant-cleanup test passes all 3
parameters, and the combined alpha report/reliability subset passes 62 tests
with 1 Windows-only skip. These are source-checkout results on Linux Python
3.12.3 with temporary test dependencies. A fresh Linux Python 3.12 package
build from `aa973ff3c192242e557421d615f5d161a68994c0` is preserved under
`dist/aa973ff3/` with these SHA-256 values:

- follow-up wheel: `6587126830c28e7e427cfd5d6aae4882ab3736ff3badf328309518491aca654b`
- follow-up sdist: `34ec142e405ca216efa935cd2a7369ba05b917fbf70e130e921c36b3a671365a`
- follow-up provenance: `9f06ccec151bb9dd75850a948e5c6589e2770126b5b6ec280ecac84f9d35808e`

The follow-up wheel and sdist each contain all 455 tracked package files, and
a clean target-directory install passed the documented provider-free
`--help`, `alpha init`, offline doctor, zero-generation run, show, HTML report,
and verified export smoke. This is Linux package evidence; the Windows package
hashes below remain evidence for `8621ea69`, and the follow-up has not been
pushed or installed on the declared Windows reference environment.

## Implemented workflow

- The supported example is deterministic bin packing with an intentionally
  improvable next-fit Python seed, fixed training and held-out cases, strict
  correctness checks, and evaluator data outside the editable workspace.
- `alpha init` creates a bounded task; `alpha doctor` performs provider/config
  preflight; `run --progress`, `show`, `alpha report`, and `alpha export` cover
  the first-run workflow.
- Reports include baseline/best quality, correctness, code changes, run state,
  stopping reason, provider/model identity, token usage, and estimated cost.
  Estimated cost is explicitly not a hard billing guarantee.
- Cancellation, interruption, persistence failures, prompt compatibility,
  artifact inspection, and source-selection ambiguity have dedicated tests and
  documentation. Restore documentation explicitly excludes pending-work resume.
- The prepared developer trial materials contain no participant results; no
  participants have been contacted.

## Source-checkout verification

- Exact-candidate non-integration suite: 6,640 passed, 27 skipped, 3
  deselected, exit 0. This is not installed-package or provider evidence.
- Recorded alpha suite: 124 passed, exit 0.
- Recorded broad loop/reliability suite: 496 passed, 2 skipped, exit 0.
- Secret baseline review and configured all-files scan passed without weakening
  detector settings. No provider calls were made by these checks.

## Exact-head package and installed verification

Built with Windows Python 3.12 from the clean tracked exact candidate:

- wheel: `libreevolve-0.1.0-py3-none-any.whl`
  - SHA-256: `8271db759a94a5a637539a65d2d9138966a6958c520feaf4f0801e9a3ba7871f`
- source distribution: `libreevolve-0.1.0.tar.gz`
  - SHA-256: `b5626d897273527e2378236a4fc432d4a8448ebc14fc6559884fee2d905a830d`
- `release_artifact_provenance.json`
  - SHA-256: `bc35ef56f6c50ff234e01d4d7783bbe91188dc7fb27d05924b284fe43a876548`

The wheel and source distribution each contain all 455 files under the
`libreevolve/` package tree. In the isolated venv, both
`libreevolve --help` and `python -m libreevolve --help` passed.

A fresh Windows Python 3.12 venv without system packages installed the exact
wheel and its declared dependencies; `pip check` passed. The documented
provider-free workflow then passed end to end: CLI help, `alpha init`, offline
`alpha doctor`, zero-generation run, `show`, HTML report, and verified export.
The exported code passed independent training and held-out correctness checks:

- exported code SHA-256: `a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507`
- training score/correctness: `0.8016472203157172` / `true`
- held-out score/correctness: `0.8121645796064401` / `true`
- provider attempts: `0`

This is retained-seed evidence only; it does not demonstrate model-guided
improvement.

## Remote CI and external acceptance gates

PR #1 is merged, but post-merge runs `34019445028` (Tests) and `34019445056`
(Installed Alpha) failed before job execution because GitHub reported recent
account payment failure or an insufficient spending limit. Passing CI remains
unproved; this is an account gate, not a code-failure diagnosis. Automatic
push, pull-request, and scheduled triggers are temporarily disabled while that
account issue is unresolved; both workflows remain available by manual
dispatch and must be re-enabled before claiming a release gate.

The following acceptance evidence is still missing:

1. Three independent real-provider experiments under an explicitly authorized
   aggregate cap, with all attempts, failures, usage, cost estimates, and
   independent exported-candidate reevaluations retained.
2. A passing exact-head CI run after the GitHub billing gate is resolved.
3. Observed usability results from 3–5 developers who did not build the
   product. The trial packet and record template are prepared, but no contact
   or feedback is authorized or recorded.

## Current classification

The evidence supports an engineering preview. It does not support a
trial-ready or release-ready alpha, and no broad improvement claim is made.
