# problems/loader.py verification

Verifier: independent non-authoring lane. Verdict: PASS.

Root-side evidence:

- `tests/core/test_loader.py`: `279 passed, 8 skipped`.
- `tests/test_readme_problem_layout_boundary.py` and
  `tests/test_problem_format_loader_contract_boundary.py`: `6 passed`.
- AST parsing, in-memory compilation, imports, public `Problem`/
  `load_problem`, compatibility-wrapper delegation, and lazy `pypdf` loading:
  passed.
- Falsey manifest values (`false`, `0`, `[]`, empty string, `null`) reject;
  blank manifests remain accepted.
- Loader diff check and line-ending/trailing-whitespace audit: clean.

The verifier confirmed the required source anchors remain in `loader.py`:
literal `_CONTEXT_MANIFEST_NAMES` and a `def _load_context_files` compatibility
wrapper. The new context module has no runtime-orchestration imports and keeps
PDF import function-local.

Scoped implementation paths are `libreevolve/problems/loader.py` and
`libreevolve/problems/context_loader.py`. The tracked dirty
`tests/core/test_loader.py` path was preserved and not edited by the writer.
The lane is ready for a separately authorized PR packet; no PR or Git staging
was performed here.
