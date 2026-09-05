# cli.py inventory

Evidence state: measured/read-only Wave 1 report.

Measured shape: 2,842 physical LOC, 2,622 logical/noncomment LOC, 103
functions, two classes, and 1,420 AST statements. Main hotspots are
`_build_config`, `show`, `_archive_summary`, `run`, and artifact-export
rollback. The module has 24 outbound module paths and a critical duplicate
artifact-ownership pattern: imported artifact helpers are locally rebound by
definitions in the latter half of the file.

The locked seam is the read-only `show` inspection pipeline: history/manifest
validation, archive selection, diagnostics, and bounded/redacted source
rendering. Keep Click parsing/formatting/exit translation and all artifact
writing/export/rollback in `cli.py`; the proposed `core/run_inspection.py`
must not import Click or take ownership of artifact writes.
