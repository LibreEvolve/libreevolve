# Core component report: candidate, workspace, and diff

Status: integrated root fix; focused verification passed; native Windows
verification remains unverified.

Owned paths: `libreevolve/core/candidate.py`, `libreevolve/core/diff.py`.

Agent: `01a06255-f7b5-70e1-be00-d9d64dc349ea`. The independent
cross-platform review did not report a residual defect in this component;
native Windows execution remains unverified.

Change: workspace collision keys now normalize Unicode NFC and case-fold
relative paths, with deterministic POSIX/Windows grammar tests for drive,
backslash, traversal, and case collisions.

Evidence: candidate/diff/evaluator slice passed `265 passed in 3.60s`, including
the materialization collision regression. This is test-derived POSIX evidence;
native Windows execution is still unverified. Finding `MP-001` is remediated
for the shared cross-platform contract.
