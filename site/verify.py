"""Check an existing static artifact inventory and hashes without executing it."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath


def verify(directory: Path) -> int:
    if directory.is_symlink() or not directory.is_dir():
        raise ValueError("Expected a non-symlink artifact directory")
    paths = list(directory.rglob("*"))
    if any(path.is_symlink() or getattr(path, "is_junction", lambda: False)() for path in paths):
        raise ValueError("Artifact links are not permitted")
    if any(not path.is_file() and not path.is_dir() for path in paths):
        raise ValueError("Artifact special files are not permitted")
    manifest_path = directory / "build-manifest.json"
    if not manifest_path.is_file() or manifest_path.stat().st_size > 1_048_576:
        raise ValueError("Missing or oversized build manifest")
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    expected = manifest.get("output_sha256")
    if type(expected) is not dict or not expected:
        raise ValueError("Missing output inventory")
    for name, digest in expected.items():
        path = PurePosixPath(name)
        if not name or "\\" in name or ":" in name or path.is_absolute() or ".." in path.parts or path.as_posix() != name:
            raise ValueError("Unsafe manifest path")
        if type(digest) is not str or len(digest) != 64 or any(c not in "0123456789abcdef" for c in digest):
            raise ValueError("Invalid content digest")
    actual = {path.relative_to(directory).as_posix() for path in paths if path.is_file()}
    if actual != set(expected) | {"build-manifest.json"}:
        raise ValueError("Artifact contains missing or unexpected files")
    for name, digest in expected.items():
        with (directory / name).open("rb") as stream:
            observed = hashlib.file_digest(stream, "sha256").hexdigest()
        if observed != digest:
            raise ValueError(f"Content hash mismatch: {name}")
    return len(expected)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("directory", type=Path)
    args = parser.parse_args()
    print(f"Verified {verify(args.directory)} content files against the supplied manifest. This is not approval or authenticity verification.")
