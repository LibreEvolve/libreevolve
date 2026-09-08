# Public result rendering boundary

Status: implementation in progress; not a shipping-command announcement.

Existing `alpha report` builds fresh local verification data and then renders
HTML. Existing `alpha export` resolves source selection and freshly verifies
the candidate. Neither operation grants public sharing permission. Their
execution and history/workspace authority remain unchanged.

The new public-record modules admit a strict frozen allowlist. Public rendering
will accept that record, not a run directory, candidate module or HTML upload.
It will not import the verification module, execute source or fetch resources.
Private-to-public preparation and CLI integration are implemented separately.
Preparation explicitly executes trusted candidate checks; inspect and render
consume the frozen record without executing candidate code. Record-only tests
do not by themselves prove the preparation or command paths.

## Approval

Canonical JSON hashes bind an operator's affirmative action to the entire
reviewed payload. A source link requires a separate affirmative choice. Full
provenance hashes are part of the same reviewed payload. No candidate code,
raw prompt, account field or private path is an allowed record field.

The approval receipt names the operator and must remain private. It is a local
accidental-disclosure interlock, not authentication or a signature. Operators
can edit data; tests cannot establish the truth of their claims. Synthetic
fixtures retain an explicit evidence-class label in every rendered surface.

## Presentation contract

Visual thesis: a quiet developer work surface with aligned evidence tables,
clear type and one restrained green accent.

Content plan: product and evidence class; separate run and candidate outcomes;
same-corpus comparison; named checks and usage; provenance and limitations.
There is no marketing hero or invented proof graphic.

Interaction thesis: keyboard-visible source-link focus and native document
navigation only. Static cards and local evidence pages have no active scripts,
scroll effects or ornamental animation. The frontend guidance's utility-copy
and cardless-layout rules apply; its landing-page motion defaults do not.

The image card is a plain functional, deterministic data layout, not new brand
artwork. Generated-art approval remains a separate workstream and gate.

## Interpretation

Outcomes are derived from admitted baseline/candidate metrics, not an editable
success caption. Compare only valid data with matching corpus ID, corpus hash,
split and case count. An empty corpus or zero baseline has no percentage.
Negative reductions remain negative. Run cancellation never overwrites
candidate validity. Missing usage stays null and displays as unknown.

Projection/source-conflict handling, safe output paths, renderer/CLI integration,
adversarial tests and retained regressions now have targeted test coverage and
an independent source review. Remaining acceptance includes installed-package
validation, current-record rendered accessibility inspection, and independent
review of the separate local-report presentation changes. Component evidence
does not establish release, deployment, native Windows support or a live demo.
