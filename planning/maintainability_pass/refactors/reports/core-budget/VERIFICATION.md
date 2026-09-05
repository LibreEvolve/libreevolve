# core-budget independent verification

## Verdict

**CONDITIONAL**.

The prior conditional report's 14-private-helper compatibility gap is
resolved, and the settled focused budget suite and behavioral compatibility
checks pass. A clean PASS is withheld because the support file currently
has Git create mode 100755, not the required 100644. The verifier did not
change that production file or its Git state.

## Scope and attribution

- Baseline: HEAD = 7983544e28e478eb6a0f5c35e4af5a86b125cea2.
- Inspected production paths: libreevolve/core/budget.py and
  libreevolve/core/budget_contract.py.
- budget.py is modified and budget_contract.py is currently untracked in
  the shared checkout. tests/core/test_budget.py was not edited by this
  verification.
- The verifier wrote only this VERIFICATION.md; no production, test,
  registry, matrix, staging, commit, or push action was performed.

## Requested checks

| Check | Result |
| --- | --- |
| /mnt/c/Windows/py.exe -3.12 -m py_compile libreevolve/core/budget.py libreevolve/core/budget_contract.py | PASS |
| git diff --check -- libreevolve/core/budget.py | PASS; exit 0, no diagnostics |
| git diff --no-index --check /dev/null libreevolve/core/budget_contract.py | No whitespace diagnostics; exit 1 is expected because the untracked file differs from /dev/null |
| /mnt/c/Windows/py.exe -3.12 -m pytest tests/core/test_budget.py --tb=short | **150 passed in 0.21s** |
| Private-name and identity smoke | PASS; 14/14 names re-exported with object identity |
| Current-vs-HEAD contract/behavior smoke | PASS |

The support source has no third-party or project imports: only
collections.abc, copy, datetime, math, re, typing, and __future__. AST
inspection found no RunBudget definition, project import,
filesystem/provider/network/subprocess operation, or forbidden I/O call. Its
only state mutation is applying validated synchronous events through the
supplied budget surface.

## Compatibility evidence

- RunBudget remains a dataclass with 46 fields in the exact HEAD order.
- All RunBudget public and private method signatures match HEAD.
- The seven inspected module-level replay/validation/event signatures match
  HEAD.
- The 14 names previously reported missing are now direct aliases from
  budget_contract.py, each passing identity comparison from budget.py:

  ~~~text
  _role_budget_exhausted
  _role_number_budget_exhausted
  _role_scope_consumed
  _role_scope_matches
  _validate_controller_budget_events
  _validate_controller_event_accounting
  _validate_controller_event_elapsed
  _validate_controller_event_required_fields
  _validate_event_text
  _validate_restored_consumed
  _validate_restored_limits
  _validate_restored_utc
  _validate_restored_wall_clock
  _validate_role_scope_label
  ~~~

- budget.BudgetSnapshotError is budget_contract.BudgetSnapshotError.
  Representative invalid snapshot/event inputs produced the same exception
  type names and messages as HEAD. The public alias is compatible, although
  the defining __module__ is now budget_contract.
- Matched HEAD state transitions for generation, LLM, evaluator, per-role
  accounting, snapshots, finish behavior, and all controller event kinds.
- Matched HEAD for 18 individual evaluator/LLM/role/runtime limit probes,
  the all-zero precedence case (max_evaluations first), and generation
  finish precedence (max_generations).

## Ownership audit

budget.py retains Config construction, monotonic/UTC clock acquisition,
RunBudget, snapshots, finish behavior, restored/replay façade assembly, and
async/resume-facing concerns. budget_contract.py retains only pure constants,
plain-record validation, limit selection, synchronous counter helpers, and
validated event application. It does not own persistence, JSONL, provider
calls, clock acquisition, subprocess execution, or async reservation.

## Remaining blocker

Current read-only Git checks report:

  ~~~text
  git diff --no-index --summary /dev/null libreevolve/core/budget_contract.py
  create mode 100755 libreevolve/core/budget_contract.py
  ~~~

The WSL-mounted working-tree stat also presents 777; the decisive Git
no-index summary is 100755. The support source must be recorded as mode
100644 before this lane can be promoted to PASS. No mode correction was
made because this verifier was restricted to this report file.

## Evidence boundary

This is focused static and behavioral evidence from a shared dirty checkout.
It does not establish the full repository gate, package/build behavior,
provider integration, crash recovery, native sandbox, distributed execution,
cross-process resume, or end-to-end runtime behavior.
