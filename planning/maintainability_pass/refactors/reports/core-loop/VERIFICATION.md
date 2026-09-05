# `core/loop.py` verification

Verifier: `01a06a0e-41ef-7393-a012-c8da889ab98c` (independent,
non-authoring). Verdict: `PASS` for the pure value seam.

Evidence:

- The four frozen dataclasses preserve baseline field order, annotations, and
  defaults exactly.
- `loop._Class` and `loop_models._Class` identity checks pass in both import
  orders. `evolve()` and other loop definitions are AST-identical after
  excluding only the moved classes/import.
- `loop_models.py` is data-only: no functions or side-effect calls.
- Windows Python 3.12.10: characterization `11 passed in 37.10s`; selected
  loop contracts `8 passed, 459 deselected in 24.43s`.
- Compile, import-cycle, alias-identity, signature, and whitespace checks
  passed.

The full `tests/core/test_loop.py` regression subsequently reports `465
passed, 2 skipped in 799.84s`. Provider/network, broader native-Windows,
distributed, and end-to-end runtime evidence remain unverified; async evidence
is local-process only.
