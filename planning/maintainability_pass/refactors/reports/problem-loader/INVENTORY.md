# problems/loader.py inventory

Evidence state: measured/read-only Wave 1 report.

## Measured shape

- 3,005 physical LOC; 2,802 nonblank LOC; 203 blank LOC.
- 91 top-level functions, 10 nested functions, two classes, 101 function
  symbols total.
- 376 decision nodes, 99 extra boolean operands, 1,139 calls, 495
  assignments, 96 comprehensions, and 52 exception handlers.
- Largest functions: `_load_context_manifest` (181 LOC),
  `_load_initial_workspaces` (174), `_normalize_metric_schema` (149),
  `_select_context_paths` (114), and `_load_context_files` (110).

## Contract and coupling anchors

`Problem` and `load_problem()` are the public façade. The file owns metric
normalization, validator policy, optional metadata, benchmark prompt
normalization, seeds/workspaces, context traversal, path safety, diagnostics,
PDF handling, and excerpts.

Production importers include CLI, database, evaluator, feedback, loop, prompt,
and matrix fixtures. `core/database.py` imports private
`_normalize_metric_schema`; that is a separate handoff and must not be folded
into an opportunistic loader extraction.

## Proposed seam

Extract context ingestion (selection/loading/diagnostics/excerpts/PDF-related
normalization as applicable) behind a normalized reader boundary such as
`problems/context_loader.py`. The new module must not import `Problem`, loop,
database, prompts, or evaluators. Keep public façade behavior and all path,
redaction, ordering, lazy-loading, and error-precedence contracts intact.
