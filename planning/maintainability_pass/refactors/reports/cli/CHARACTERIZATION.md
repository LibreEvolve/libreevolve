# cli.py characterization

Evidence state: focused gate passed; production seam implemented and
independently verified with a conditional shared-dirty attribution.

The characterization wave added `tests/test_cli_characterization.py` with
normal help/run/show behavior, invalid configuration and restore conflicts,
malformed history, bounded/repeatable source output, deterministic best-record
selection, overwrite preservation, bounded export errors, and platform cases.
The root-reported characterization result is 9 passed and two skipped. The
combined current root run of characterization plus existing CLI tests reports
`271 passed, 6 skipped`. The implementation extracted read-only inspection
helpers into `core/run_inspection.py`; CLI parsing, formatting, export, and
rollback remain in `cli.py`. Native Windows behavior beyond this Python run and
broader-suite results remain separate claims.

The production writer is restricted to `cli.py` and new `core/run_inspection.py`
and must preserve current monkeypatch seams and dirty line endings. Artifact
schema/storage/database/config/loop changes require separate lanes.
