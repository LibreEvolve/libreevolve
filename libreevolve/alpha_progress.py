"""Observe complete history records without taking ownership of run state."""

from contextlib import contextmanager
import json
from pathlib import Path
import threading

import click


@contextmanager
def observe_progress(run_dir: Path, enabled: bool):
    """Emit bounded summaries; partial writes are retried on the next poll."""
    if not enabled:
        yield
        return
    stopped = threading.Event()

    def observe():
        offset = 0
        count = 0
        while True:
            try:
                with (run_dir / "history.jsonl").open("rb") as stream:
                    stream.seek(offset)
                    while True:
                        line = stream.readline(8_000_001)
                        if not line or not line.endswith(b"\n"):
                            break
                        offset = stream.tell()
                        try:
                            record = json.loads(line)
                        except (ValueError, UnicodeError):
                            continue
                        if not isinstance(record, dict):
                            continue
                        count += 1
                        generation = record.get("generation")
                        score = record.get("fitness")
                        if type(generation) is not int or type(score) not in (int, float):
                            continue
                        click.echo(f"Evaluated {count}: generation {generation}, score {score:.6g}",
                                   err=True)
            except OSError:
                pass
            if stopped.wait(1):
                return

    worker = threading.Thread(target=observe, name="libreevolve-progress", daemon=True)
    worker.start()
    try:
        yield
    finally:
        stopped.set()
        worker.join(timeout=2)
