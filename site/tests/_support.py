"""Shared helpers for platform-portable site tests."""

from contextlib import contextmanager
from pathlib import Path
import tempfile


@contextmanager
def temporary_directory():
    """Yield a canonical temporary root for the path-security contracts."""
    with tempfile.TemporaryDirectory() as directory:
        yield Path(directory).resolve()
