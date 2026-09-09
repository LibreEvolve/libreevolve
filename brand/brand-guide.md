# LibreEvolve brand guide

Status: independently reviewed brand guidance. This guide
describes the engineering preview, not a production-ready product or a launch.
Factual wording is sourced in [claims-summary.json](claims-summary.json);
reusable surface copy lives in [copy-registry.json](copy-registry.json).

## The identity

Display name: **LibreEvolve**. Technical identifier, import and command:
`libreevolve`. Do not rename the organization, repository, package or CLI as
part of applying this guide. Use sentence case for headings and labels.

Primary line: **Evolve code. Show the evidence.**

Category: **An open-source workbench for inspectable code-evolution experiments.**

Always accompany the category with the shipping qualifier:
**Engineering preview: bounded Python bin-packing optimization with Codex OAuth.**

The category describes the direction of the project. The qualifier describes
what the public preview supports today. Keep both visible when a description
could otherwise imply arbitrary-repository optimization or multiple providers.

“Evolve” describes searching for changes, not a promise of improvement.
“Evidence” means recorded artifacts and named checks, not formal proof,
independent certification, universal correctness or optimality.

## Who it is for

Primary: Python developers comfortable with coding agents who want to inspect
a small, bounded experiment rather than accept an opaque result. Start with
the candidate, its checks and the result—not research terminology.

Secondary: people studying evaluators, reproducibility and evolutionary
programming. Give them exact source and environment identities, a clear
training/held-out distinction and honest failure records.

Do not target enterprise buyers with throughput, security, cost or reliability
promises that lack representative evidence. OAuth is an access route, not a
claim of unique competitive advantage. Omit competitor comparisons unless
current primary evidence supports the specific comparison.

## Message order

1. Name the product and say what the preview does.
2. Offer a concrete result to inspect, including no-improvement outcomes.
3. Explain the workflow: change a seed, evaluate candidates, inspect retained
   results, then export after fresh named checks.
4. Explain execution, usage and evidence limits before asking for a live run.

Primary CTA: **Inspect an example**. Secondary CTA: **Run the preview**.
Bind each CTA to a real, checked destination before use. Until an approved
example viewer exists, do not add a dead or misleading example button; a
clearly labeled documentation link is not an authentic demonstration.
Stars and social sharing are optional secondary actions, never access gates.

## Voice and vocabulary

Use short, specific sentences. Prefer “candidate,” “saved run,” “fresh checks,”
“training cases” and “held-out cases” to unexplained research shorthand.
Say “attempts to improve” or “searches for changes,” not an unconditional
“improves your code.” Avoid “autonomous genius,” “production-ready,” “proven
optimal,” unsupported superiority, fake endorsements and decorative test counts.

Separate statuses rather than compressing them into a success badge:

| Dimension | What the label means |
| --- | --- |
| Run status | Whether the local run finished, was cancelled or is incomplete |
| Validity | Whether the candidate passed the named finite checks |
| Training quality | Quality on the training corpus, not accuracy or speed |
| Held-out quality | Separate reporting checks after selection is frozen |
| Retention | Whether a candidate was retained in search state |
| Usage | What usage is actually recorded, including missing information |
| Export | A newly checked candidate artifact, not public publication |

Do not style an invalid zero-bin placeholder as a win. Compare valid solutions
on identical cases within the same split. Report regressions and unchanged
results plainly. Missing usage is unknown, not zero cost. A source hash
identifies bytes; it is not a signature or independent attestation.

Use the registry's complete limitation text beside abbreviated status labels.
Conditional outcome copy must only appear when its condition is established
by the data. Never use a fixed “improved” caption on every result card.

## Diff Arrow and layout

Retain the existing Diff Arrow concept. Existing source assets are
[dark mark](../assets/logo-mark.svg) and
[light mark](../assets/logo-mark-light.svg). These links identify the current
assets, not newly generated masters or final artwork approval.

The approved static-site family is integrated as unchanged raster PNGs with
explicit roles: the four-part core and light treatment anchor the identity
plane, the two-form micro treatment carries compact identity, and neutral
monochrome siblings follow the theme. The public-safe fingerprints below
identify bytes only; they are not signatures, vector-master claims, product
evidence, or deployment approval. This bounded integration does not convert
the private concept masters into production-approved destination exports.

| Public path | Role | SHA-256 |
| --- | --- | --- |
| `assets/brand/mark-dark.png` | Dominant dark hero mark | `443525a55f45359e1ddcb69fef98754a62eefab7a926e96461475c2411d1ec62` |
| `assets/brand/mark-light.png` | Light-plane hero sibling | `f5623a8ec07bf534970989596291514ff2bf726c72cf1d3017bd675597dc652d` |
| `assets/brand/micro-mark.png` | Compact and favicon mark | `1e136500c2d1fba2d16f10fe7b28fd7ebcb342269c31799332014d882f7c1a5f` |
| `assets/brand/mark-mono-dark.png` | Dark-theme navigation mark | `865657ed1c7575ab985f2071d1bc56eaa1375fbe27af5d998ca54684a0e9ad54` |
| `assets/brand/mark-mono-light.png` | Light-theme navigation mark | `30d443bd42bd95e7e58f090e843ff001c2644a3a942ff6ffc4a2844e9a0e9f2e` |

Keep the mark's proportions and contrast. Do not stretch, skew, add glow,
redraw a mascot or place it over busy text. Pair the mark with the display name
where the product would otherwise be ambiguous. Use a plain text name when
a small rendition would be illegible. Use alt text “LibreEvolve” when the mark
is the sole name; use empty alt text when an adjacent wordmark duplicates it.

Visual thesis: a precise developer instrument—clear editorial type, calm
surfaces, generous space and a restrained green accent around real evidence.

Website content sequence: identity and preview scope; one inspectable example;
the change/evaluate/inspect/export workflow; then a setup CTA and limitations.
Give each section one job. The future hero should be edge-to-edge with an
inner text column, not a stack of dashboard cards. Make LibreEvolve unmistakable
and give the authentic evidence artifact the dominant visual role. Do not
invent a screenshot or metrics panel to fill the space before evidence exists.

Reports are work surfaces, not landing pages: use plain outcome, validity,
split and usage labels. Prefer readable tables, dividers and aligned text to
repeated cards, glow effects or a marketing hero above the result.

## Color, type and motion

Starting tokens, subject to combination-specific contrast tests:

| Role | Dark | Light |
| --- | --- | --- |
| Background | `#0D1117` | `#FFFFFF` |
| Surface | `#161B22` | `#F4F7F5` |
| Text | `#E6EDF3` | `#17231C` |
| Secondary text | `#9DA7B3` | `#526159` |
| Accent | `#00FF41` | `#007A3D` |

The bright green is not default text on white. Verify actual foreground,
background, focus and disabled-state combinations before shipping. Status
must have text or shape in addition to color. Prefer one accent, not a
separate decorative color for every section.

Use system sans-serif and monospace fallbacks offline. IBM Plex Sans and
IBM Plex Mono are the preferred optional families only after provenance and
license review; no font binaries are included here. Limit the interface to
two font families. Use monospace for code and identifiers, not all prose.

Interaction thesis for the future website: a brief identity entrance,
an inspectable workflow progression, and a clear focus/hover transition on
the primary action. Motion must explain hierarchy or affordance. Disable
non-essential transitions for reduced motion; no scroll hijacking, flashing
status, or perpetual background animation. Static local reports stay usable
without network access or active scripts.

## Applying the copy source

Use a registry unit's text, claim IDs and usage conditions together. A unit's
presence in this repository is not approval to apply GitHub settings, deploy
a site, publish a post or run a paid experiment. Review the actual surface
after integration; line wrapping and shortened copy must not drop qualifiers.

Run `python3.12 brand/check_claims.py` from the checkout to check the registries
(Windows: `py -3.12 brand/check_claims.py`). Use `--require-reviewed` for a
publication candidate. The checker catches structural and selected wording
errors; it does not prove source semantics or replace human content review.

Revalidate after relevant source, default, provider-access, export, report,
validator or licensing changes. Keep historical live evidence explicitly
historical. Do not print frozen test totals or imply paused CI is running.
Final artwork, an approved authentic example, site deployment, publication on
organization surfaces and the proposed Three-Call Challenge remain separately
tracked work with their own review and authorization gates. The local share
workflow and static website source are implemented and independently checked;
that evidence does not authorize publication or establish live-model evidence.
