# Core component report: provenance and redaction

Status: integrated root fix; focused verification passed; native Windows
verification remains unverified.

Owned paths: `core/provenance.py`, `core/redaction.py`.

Agent: `01a06256-159e-7b11-b12d-b3bf6d26a250`. The independent
cross-platform review did not report a residual defect in this component;
native Windows execution remains unverified.

Change: executable basename extraction now handles POSIX, Windows drive, and
UNC forms portably through `ntpath`; accelerator evidence was made stable in
the patched subprocess test.

Evidence: targeted helper/accelerator checks passed; the full provenance slice
passed `110 passed, 1 skipped in 50.09s`. This is test-derived POSIX evidence;
native Windows and live provenance parity remain unverified. `MP-002` is
remediated for the shared portable contract.
