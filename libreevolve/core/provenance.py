from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path
from types import ModuleType

_EXCLUDED_DIRS = {".git", "__pycache__", ".pytest_cache", ".mypy_cache", "runs"}


def problem_provenance(problem_dir: Path) -> dict:
    return _tree_provenance(problem_dir, label="problem")


def source_provenance() -> dict:
    return _tree_provenance(Path(__file__).resolve().parents[1], label="libreevolve")


def plugin_provenance(plugins: list[object]) -> list[dict]:
    records = []
    for plugin in plugins:
        cls = plugin.__class__
        module = _module_for_class(cls)
        path = Path(getattr(module, "__file__", "") or "")
        record = {
            "class": f"{cls.__module__}.{cls.__qualname__}",
            "module": cls.__module__,
        }
        if path.is_file():
            raw = path.read_bytes()
            record.update(
                {
                    "path": str(path.resolve()),
                    "sha256": hashlib.sha256(raw).hexdigest(),
                    "bytes": len(raw),
                }
            )
        else:
            record["path"] = None
        records.append(record)
    return records


def git_state(cwd: Path | None = None) -> dict:
    cwd = cwd or Path.cwd()
    root = _git(["rev-parse", "--show-toplevel"], cwd)
    if root is None:
        return {"available": False}
    head = _git(["rev-parse", "HEAD"], Path(root))
    status = _git(["status", "--porcelain"], Path(root))
    return {
        "available": True,
        "root": root,
        "head": head,
        "dirty": bool(status),
        "status_entries": [] if not status else status.splitlines(),
    }


def _tree_provenance(root: Path, label: str) -> dict:
    root = root.resolve()
    files = [_file_record(path, root) for path in _iter_files(root)]
    tree_hash = _hash_records(files)
    return {
        "label": label,
        "root": str(root),
        "tree_hash": tree_hash,
        "file_count": len(files),
        "files": files,
    }


def _iter_files(root: Path) -> list[Path]:
    paths = []
    for path in root.rglob("*"):
        if not path.is_file():
            continue
        rel_parts = path.relative_to(root).parts
        if any(part in _EXCLUDED_DIRS for part in rel_parts):
            continue
        paths.append(path)
    return sorted(paths, key=lambda p: p.relative_to(root).as_posix())


def _file_record(path: Path, root: Path) -> dict:
    raw = path.read_bytes()
    return {
        "path": path.relative_to(root).as_posix(),
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
    }


def _hash_records(records: list[dict]) -> str:
    payload = json.dumps(records, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(payload).hexdigest()


def _module_for_class(cls: type) -> ModuleType | None:
    import sys

    module = sys.modules.get(cls.__module__)
    return module if isinstance(module, ModuleType) else None


def _git(args: list[str], cwd: Path) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=str(cwd),
            capture_output=True,
            text=True,
            timeout=5.0,
        )
    except (OSError, subprocess.SubprocessError):
        return None
    if result.returncode != 0:
        return None
    return result.stdout.strip()
