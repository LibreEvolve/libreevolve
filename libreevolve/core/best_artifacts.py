from __future__ import annotations

import hashlib
import shutil
from pathlib import Path
from uuid import uuid4

from libreevolve.core.jsonl import (
    load_strict_json_object,
    strict_json_dump,
)
from libreevolve.core.redaction import redact_sensitive_text

STATIC_WORKSPACE_MANIFEST_NAME = ".libreevolve_static_files.json"


def export_best_artifacts(program, run_dir: Path) -> dict:
    try:
        best_py, best_workspace = _write_best_artifacts(program, run_dir)
    except Exception as exc:
        return best_artifact_export_failure_record(run_dir, exc)
    return best_artifact_export_success_record(run_dir, best_py, best_workspace)


def attach_best_artifact_export(runtime: dict, record: dict | None) -> None:
    if record is None:
        return
    runtime["best_artifact_export"] = record
    artifacts = runtime.get("artifacts")
    if not isinstance(artifacts, dict):
        return
    paths = record.get("paths")
    if not isinstance(paths, dict):
        return
    if isinstance(paths.get("best.py"), dict):
        artifacts["best.py"] = paths["best.py"]
    if isinstance(paths.get("best_workspace"), dict):
        artifacts["best_workspace"] = paths["best_workspace"]


def best_artifact_export_success_record(
    run_dir: Path, best_py: Path, best_workspace: Path
) -> dict:
    return {
        "status": "completed",
        "paths": {
            "best.py": _best_artifact_path_record(best_py, run_dir),
            "best_workspace": _best_artifact_path_record(best_workspace, run_dir),
        },
    }


def best_artifact_export_failure_record(run_dir: Path, exc: BaseException) -> dict:
    record = {
        "status": "failed",
        "error_type": exc.__class__.__name__,
        "error": _bounded_redacted_text(str(exc)),
        "paths": {
            "best.py": _best_artifact_path_record(run_dir / "best.py", run_dir),
            "best_workspace": _best_artifact_path_record(
                run_dir / "best_workspace", run_dir
            ),
        },
    }
    if isinstance(exc, BestArtifactExportError):
        record.update(exc.to_manifest_record())
    return record


def _record_best_artifact_export_success(
    run_dir: Path, best_py: Path, best_workspace: Path
) -> None:
    _update_best_artifact_export_manifest(
        run_dir, best_artifact_export_success_record(run_dir, best_py, best_workspace)
    )


def _record_best_artifact_export_failure(run_dir: Path, exc: BaseException) -> None:
    _update_best_artifact_export_manifest(
        run_dir, best_artifact_export_failure_record(run_dir, exc)
    )


def _update_best_artifact_export_manifest(run_dir: Path, record: dict) -> None:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.exists():
        return
    manifest = load_strict_json_object(manifest_path, source="manifest.json")
    runtime = manifest.get("runtime")
    if not isinstance(runtime, dict):
        return
    attach_best_artifact_export(runtime, record)
    strict_json_dump(manifest, manifest_path, indent=2)


def _write_best_artifacts(program, run_dir: Path) -> tuple[Path, Path]:
    run_dir.mkdir(parents=True, exist_ok=True)
    best_py = run_dir / "best.py"
    workspace_dir = run_dir / "best_workspace"

    suffix = uuid4().hex
    tmp_py = run_dir / f".best-{suffix}.py.tmp"
    tmp_workspace = run_dir / f".best_workspace-{suffix}.tmp"
    backup_py = run_dir / f".best-{suffix}.py.bak"
    backup_workspace = run_dir / f".best_workspace-{suffix}.bak"
    installed_py = False
    installed_workspace = False
    _preflight_best_artifact_export_paths(
        run_dir=run_dir,
        paths=(best_py, workspace_dir, tmp_py, tmp_workspace, backup_py, backup_workspace),
    )

    try:
        tmp_py.write_text(program.code, encoding="utf-8")
        workspace = program.workspace()
        workspace.materialize(tmp_workspace)
        _write_static_workspace_manifest(workspace, tmp_workspace)

        if best_py.exists():
            best_py.replace(backup_py)
        if workspace_dir.exists():
            workspace_dir.replace(backup_workspace)

        tmp_workspace.replace(workspace_dir)
        installed_workspace = True
        tmp_py.replace(best_py)
        installed_py = True
    except Exception as exc:
        rollback = _rollback_best_artifact_export(
            best_py=best_py,
            workspace_dir=workspace_dir,
            backup_py=backup_py,
            backup_workspace=backup_workspace,
            installed_py=installed_py,
            installed_workspace=installed_workspace,
            run_dir=run_dir,
        )
        cleanup_errors = _cleanup_best_artifact_export_paths(
            (tmp_py, tmp_workspace, backup_py, backup_workspace),
            run_dir=run_dir,
            preserve_paths=rollback["preserve_paths"],
        )
        raise BestArtifactExportError(
            exc,
            rollback_errors=rollback["errors"],
            cleanup_errors=cleanup_errors,
            preserved_paths=rollback["preserved_paths"],
        ) from exc
    cleanup_errors = _cleanup_best_artifact_export_paths(
        (tmp_py, tmp_workspace, backup_py, backup_workspace),
        run_dir=run_dir,
        preserve_paths=(),
    )
    if cleanup_errors:
        raise BestArtifactExportError(
            cleanup_errors[0]["exception"],
            rollback_errors=(),
            cleanup_errors=cleanup_errors,
            preserved_paths=(),
        )
    return best_py, workspace_dir


def _write_static_workspace_manifest(workspace, root: Path) -> None:
    if not workspace.static_files:
        return
    strict_json_dump(
        {
            "schema": "libreevolve.static_workspace_files.v1",
            "note": (
                "Static files are immutable candidate members tracked by metadata; "
                "encoded or verified source-copy static member bytes are "
                "materialized when present."
            ),
            "static_files": [_static_workspace_manifest_record(item) for item in workspace.static_files],
        },
        root / STATIC_WORKSPACE_MANIFEST_NAME,
        indent=2,
    )


def _static_workspace_manifest_record(record: dict) -> dict:
    return {key: value for key, value in record.items() if key != "content_b64"}


def _preflight_best_artifact_export_paths(
    *, run_dir: Path, paths: tuple[Path, ...]
) -> None:
    resolved_run_dir = run_dir.resolve(strict=False)
    for path in paths:
        if _path_is_present_or_link(path) and _path_is_link_like(path):
            raise OSError(
                "refusing to replace linked best artifact path "
                f"{_run_relative_path_label(path, run_dir)}"
            )
        resolved_path = path.resolve(strict=False)
        try:
            resolved_path.relative_to(resolved_run_dir)
        except ValueError as exc:
            raise OSError(
                "refusing best artifact path outside run directory "
                f"{_run_relative_path_label(path, run_dir)}"
            ) from exc


def _path_is_present_or_link(path: Path) -> bool:
    return path.exists() or path.is_symlink()


def _path_is_link_like(path: Path) -> bool:
    return path.is_symlink() or _path_is_junction(path)


def _best_artifact_path_record(path: Path, run_dir: Path) -> dict:
    is_symlink = path.is_symlink()
    is_junction = _path_is_junction(path)
    exists = path.exists()
    present = exists or is_symlink
    record = {
        "path": _run_relative_path_label(path, run_dir),
        "exists": exists,
        "present": present,
        "is_symlink": is_symlink,
        "is_junction": is_junction,
    }
    if is_symlink or is_junction:
        record["kind"] = "link"
        return record
    if path.is_dir():
        record["kind"] = "directory"
        record.update(_best_workspace_tree_record(path))
        return record
    if path.is_file():
        record["kind"] = "file"
        try:
            raw = path.read_bytes()
        except OSError as exc:
            record["inspection_error_type"] = exc.__class__.__name__
            record["inspection_error"] = _bounded_redacted_text(str(exc))
            return record
        record["bytes"] = len(raw)
        record["sha256"] = hashlib.sha256(raw).hexdigest()
        return record
    record["kind"] = "missing"
    return record


def _best_workspace_tree_record(path: Path) -> dict:
    digest = hashlib.sha256()
    file_count = 0
    try:
        entries = sorted(path.rglob("*"), key=lambda item: item.as_posix())
    except OSError as exc:
        return {
            "tree_hash_status": "listing_error",
            "inspection_error_type": exc.__class__.__name__,
            "inspection_error": _bounded_redacted_text(str(exc)),
        }
    for entry in entries:
        if entry.is_symlink() or _path_is_junction(entry):
            continue
        if not entry.is_file():
            continue
        try:
            rel = entry.relative_to(path).as_posix()
            raw = entry.read_bytes()
        except OSError as exc:
            return {
                "tree_hash_status": "read_error",
                "inspection_error_type": exc.__class__.__name__,
                "inspection_error": _bounded_redacted_text(str(exc)),
            }
        digest.update(rel.encode("utf-8"))
        digest.update(b"\0")
        digest.update(hashlib.sha256(raw).hexdigest().encode("ascii"))
        digest.update(b"\0")
        file_count += 1
    return {
        "tree_hash_status": "ok",
        "tree_hash": digest.hexdigest(),
        "tree_hash_scope": "best_workspace_file_paths_and_sha256",
        "file_count": file_count,
    }


def _run_relative_path_label(path: Path, run_dir: Path) -> str:
    try:
        return path.relative_to(run_dir).as_posix()
    except ValueError:
        return redact_sensitive_text(str(path))


def _path_is_junction(path: Path) -> bool:
    is_junction = getattr(path, "is_junction", None)
    return bool(is_junction()) if callable(is_junction) else False


def _bounded_redacted_text(text: str, limit: int = 1000) -> str:
    rendered = redact_sensitive_text(text)
    if len(rendered) <= limit:
        return rendered
    return rendered[:limit] + "...<truncated>"


class BestArtifactExportError(OSError):
    def __init__(
        self,
        original: BaseException,
        *,
        rollback_errors,
        cleanup_errors,
        preserved_paths,
    ) -> None:
        self.original_error_type = original.__class__.__name__
        self.original_error = _bounded_redacted_text(str(original))
        self.rollback_errors = _manifest_error_records(rollback_errors)
        self.cleanup_errors = _manifest_error_records(cleanup_errors)
        self.preserved_paths = tuple(preserved_paths)
        parts = [f"{self.original_error_type}: {self.original_error}"]
        if self.rollback_errors:
            parts.append(f"rollback_errors={len(self.rollback_errors)}")
        if self.cleanup_errors:
            parts.append(f"cleanup_errors={len(self.cleanup_errors)}")
        if self.preserved_paths:
            parts.append(f"preserved_backups={len(self.preserved_paths)}")
        super().__init__("; ".join(parts))

    def to_manifest_record(self) -> dict:
        record = {
            "original_error_type": self.original_error_type,
            "original_error": self.original_error,
        }
        if self.rollback_errors:
            record["rollback_errors"] = self.rollback_errors
        if self.cleanup_errors:
            record["cleanup_errors"] = self.cleanup_errors
        if self.preserved_paths:
            record["preserved_backups"] = list(self.preserved_paths)
        return record


def _manifest_error_records(errors) -> list[dict]:
    records = []
    for error in errors:
        record = {
            "stage": error["stage"],
            "path": error["path"],
            "error_type": error["exception"].__class__.__name__,
            "error": _bounded_redacted_text(str(error["exception"])),
        }
        records.append(record)
    return records


def _best_artifact_operation_error(
    *, stage: str, path: Path, run_dir: Path, exc: BaseException
) -> dict:
    return {
        "stage": stage,
        "path": _run_relative_path_label(path, run_dir),
        "exception": exc,
    }


def _rollback_best_artifact_export(
    *,
    best_py: Path,
    workspace_dir: Path,
    backup_py: Path,
    backup_workspace: Path,
    installed_py: bool,
    installed_workspace: bool,
    run_dir: Path,
) -> dict:
    errors = []
    preserve_paths: list[Path] = []
    preserved_paths: list[str] = []
    if installed_py and best_py.exists():
        try:
            _remove_best_artifact_temp(best_py)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="remove_installed_best.py",
                    path=best_py,
                    run_dir=run_dir,
                    exc=exc,
                )
            )
    if installed_workspace and workspace_dir.exists():
        try:
            _remove_best_artifact_temp(workspace_dir)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="remove_installed_best_workspace",
                    path=workspace_dir,
                    run_dir=run_dir,
                    exc=exc,
                )
            )
    if backup_py.exists():
        try:
            backup_py.replace(best_py)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="restore_best.py",
                    path=backup_py,
                    run_dir=run_dir,
                    exc=exc,
                )
            )
            preserve_paths.append(backup_py)
            preserved_paths.append(_run_relative_path_label(backup_py, run_dir))
    if backup_workspace.exists():
        try:
            backup_workspace.replace(workspace_dir)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="restore_best_workspace",
                    path=backup_workspace,
                    run_dir=run_dir,
                    exc=exc,
                )
            )
            preserve_paths.append(backup_workspace)
            preserved_paths.append(_run_relative_path_label(backup_workspace, run_dir))
    return {
        "errors": errors,
        "preserve_paths": tuple(preserve_paths),
        "preserved_paths": tuple(preserved_paths),
    }


def _cleanup_best_artifact_export_paths(
    paths: tuple[Path, ...], *, run_dir: Path, preserve_paths
) -> list[dict]:
    preserved = set(preserve_paths)
    errors = []
    for path in paths:
        if path in preserved:
            continue
        try:
            _remove_best_artifact_temp(path)
        except OSError as exc:
            errors.append(
                _best_artifact_operation_error(
                    stage="cleanup", path=path, run_dir=run_dir, exc=exc
                )
            )
    return errors


def _remove_best_artifact_temp(path: Path) -> None:
    if _path_is_link_like(path):
        raise OSError(
            "refusing to remove linked best artifact path "
            f"{redact_sensitive_text(str(path))}"
        )
    if path.is_dir():
        shutil.rmtree(path)
    elif path.exists():
        path.unlink()
