# `core/feedback.py` Wave 1 Inventory

Primary file: `libreevolve/core/feedback.py`
Lane: `core-feedback`
Agent: `01a069d0-b10b-7001-84a2-de1b63fd8efb`
Status: inventory complete; characterization barrier not passed

## Measurements and ownership

The module is 1,312 physical lines, 1,205 logical/token-bearing lines, 52
functions, no classes, 6 internal import edges, and an AST decision proxy of
221. `apply_llm_feedback` is the largest symbol at 238 lines; other large
clusters include grader validation, qualitative policy, stage results,
scheduler reward, safe provider values, prompt assembly, and retained text.

Direct importers are `loop.py` and `tests/core/test_feedback.py`. Loop calls it
from synchronous and async commit paths and critique; prompt, database,
CLI, evaluator, and program consumers depend on its adjusted fitness, stages,
metadata, telemetry, and retention behavior. The function concentrates
validation, retries, scoring, discard semantics, state mutation, stage
creation, retention, and scheduler rewards. Raw-text hashing before redaction,
bounded nested JSON, grader order, and existing metadata replacement/append
semantics are compatibility risks.

## Proposed seam and boundary

Proposed pure `libreevolve/core/feedback_boundary.py` for bounded context,
workspace/diagnostic rendering, safe JSON, telemetry normalization, retention,
redaction, hashing, and truncation. Keep configured-order planning, retries,
scoring, discard semantics, stage creation, and scheduler reward coordination
in `feedback.py`. The direction is `loop.py -> feedback.py ->
feedback_boundary.py`; do not import loop/prompt/database/config from the new
boundary module.

The required two child reviewers were not schedulable due to the thread limit;
pytest was unavailable to this checkpoint. No files were changed and no
implementation writer is authorized.
