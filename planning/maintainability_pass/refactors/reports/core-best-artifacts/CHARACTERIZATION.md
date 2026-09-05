# core/best_artifacts.py characterization

Evidence state: focused characterization gate passed; cleanup/platform/runtime
barrier remains partial and no writer is currently scheduled.

The test-only wave added six direct exporter cases. Root Windows verification
reports `5 passed, 2 skipped`; one initial platform-newline expectation was
corrected to hash the actual canonical bytes written by the host. Existing CLI
verification reports `271 passed, 6 skipped` and covers the duplicate consumer.

Cases cover canonical pair records, repeated export/tree-hash determinism,
runtime pointer attachment, static source-copy sidecars, failed source-copy
cleanup, and linked-target rejection. Native junction/locking, crash,
concurrency, cross-device rename, aborted-run, and hash-scope parity claims
remain open. A later constrained writer must coordinate the CLI duplicate-owner
handoff before changing shared export semantics.
