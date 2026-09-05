# problems/loader.py characterization

Evidence state: characterization gate passed with a platform qualification;
no production refactor has been applied in the root checkout.

The current focused test command was independently run from the root checkout:

```text
PYTHONDONTWRITEBYTECODE=1 /mnt/c/Windows/py.exe -3.12 -m pytest -p no:cacheprovider --confcutdir=tests/core tests/core/test_loader.py --tb=short -q
279 passed, 8 skipped in 3.68s
```

Coverage includes optional metadata mappings and alias conflicts, embedded-only
validator exemption, required-file precedence, benchmark goal-prompt
normalization, and failed-load side-effect absence. Existing tests cover seed
and context loading, redaction, Unicode, deterministic ordering/hashes,
resource limits, PDFs, and link/junction safety.

`tests/core/test_loader.py` was already a tracked dirty path in the captured
baseline; its line-ending churn and existing edits are therefore preserved and
not attributed to this coordination record. Native Windows CI remains a
separate platform claim.

The lane is ready for one production writer with this allowlist:
`libreevolve/problems/loader.py` and optionally the new
`libreevolve/problems/context_loader.py`. Tests and database/schema handoffs are
support work only if explicitly reviewed; no broad formatting or cleanup.
