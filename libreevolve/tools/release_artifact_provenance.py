from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from pathlib import Path
from typing import Any


RELEASE_ARTIFACT_PROVENANCE_SCHEMA = "libreevolve.release_artifact_provenance.v1"


def collect_release_artifact_provenance(
    root: str | Path = ".",
    dist_dir: str | Path | None = None,
) -> dict[str, Any]:
    project_root = Path(root).resolve()
    artifact_dir = project_root / "dist" if dist_dir is None else Path(dist_dir)
    if not artifact_dir.is_absolute():
        artifact_dir = project_root / artifact_dir
    artifact_dir = artifact_dir.resolve()
    artifacts = [
        _artifact_record(path)
        for path in sorted(
            [
                *artifact_dir.glob("*.whl"),
                *artifact_dir.glob("*.tar.gz"),
            ]
        )
    ]
    source_files = [
        Path("pyproject.toml"),
        Path("MANIFEST.in"),
        Path(".github/workflows/tests.yml"),
    ]
    source_hashes = {
        path.as_posix(): _file_hash(project_root / path)
        for path in source_files
        if (project_root / path).is_file()
    }
    return {
        "schema": RELEASE_ARTIFACT_PROVENANCE_SCHEMA,
        "dist_dir": _relative_or_absolute(artifact_dir, project_root),
        "artifact_count": len(artifacts),
        "artifacts": artifacts,
        "source": {
            "git_commit": _git_output(project_root, "rev-parse", "HEAD"),
            "tracked_files_dirty": bool(
                _git_output(
                    project_root,
                    "status",
                    "--porcelain",
                    "--untracked-files=no",
                )
            ),
            "source_file_sha256": source_hashes,
        },
    }


def validate_release_artifact_provenance(record: object) -> list[str]:
    if not isinstance(record, dict):
        return ["record must be a JSON object"]
    issues: list[str] = []
    if record.get("schema") != RELEASE_ARTIFACT_PROVENANCE_SCHEMA:
        issues.append("invalid schema")
    artifacts = record.get("artifacts")
    if not isinstance(artifacts, list):
        issues.append("artifacts must be a list")
        artifacts = []
    if record.get("artifact_count") != len(artifacts):
        issues.append("artifact_count must match artifacts length")
    kinds = set()
    for artifact in artifacts:
        if not isinstance(artifact, dict):
            issues.append("artifact entries must be objects")
            continue
        kinds.add(artifact.get("kind"))
        if not isinstance(artifact.get("filename"), str) or not artifact["filename"]:
            issues.append("artifact filename must be a non-empty string")
        if artifact.get("kind") not in {"wheel", "sdist"}:
            issues.append("artifact kind must be wheel or sdist")
        if not isinstance(artifact.get("size_bytes"), int) or artifact["size_bytes"] <= 0:
            issues.append("artifact size_bytes must be positive")
        digest = artifact.get("sha256")
        if not isinstance(digest, str) or len(digest) != 64:
            issues.append("artifact sha256 must be a hex digest")
    if not {"wheel", "sdist"}.issubset(kinds):
        issues.append("provenance must include at least one wheel and one sdist")
    source = record.get("source")
    if not isinstance(source, dict):
        issues.append("source must be an object")
    else:
        hashes = source.get("source_file_sha256")
        if not isinstance(hashes, dict):
            issues.append("source.source_file_sha256 must be an object")
        else:
            for required in ("pyproject.toml", "MANIFEST.in"):
                digest = hashes.get(required)
                if not isinstance(digest, str) or len(digest) != 64:
                    issues.append(f"source hash missing for {required}")
    return issues


def write_release_artifact_provenance(
    output: str | Path,
    root: str | Path = ".",
    dist_dir: str | Path | None = None,
) -> dict[str, Any]:
    record = collect_release_artifact_provenance(root=root, dist_dir=dist_dir)
    issues = validate_release_artifact_provenance(record)
    if issues:
        raise ValueError("; ".join(issues))
    output_path = Path(output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(
        json.dumps(record, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Write release artifact provenance JSON.")
    parser.add_argument("--root", default=".", help="Project root.")
    parser.add_argument("--dist", default=None, help="Distribution artifact directory.")
    parser.add_argument(
        "--output",
        default="dist/release_artifact_provenance.json",
        help="Output JSON path.",
    )
    args = parser.parse_args(argv)
    try:
        record = write_release_artifact_provenance(
            output=Path(args.root) / args.output,
            root=args.root,
            dist_dir=args.dist,
        )
    except ValueError as exc:
        parser.error(str(exc))
    print(json.dumps(record, indent=2, sort_keys=True))
    return 0


def _artifact_record(path: Path) -> dict[str, Any]:
    return {
        "filename": path.name,
        "kind": "sdist" if path.name.endswith(".tar.gz") else "wheel",
        "size_bytes": path.stat().st_size,
        "sha256": _file_hash(path),
    }


def _file_hash(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_output(root: Path, *args: str) -> str | None:
    try:
        result = subprocess.run(
            ["git", *args],
            cwd=root,
            check=True,
            capture_output=True,
            text=True,
        )
    except (OSError, subprocess.CalledProcessError):
        return None
    value = result.stdout.strip()
    return value or None


def _relative_or_absolute(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return path.as_posix()


if __name__ == "__main__":
    raise SystemExit(main())
