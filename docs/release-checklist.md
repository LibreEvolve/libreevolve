# Release Checklist

This checklist defines the local release-smoke evidence that must exist before a
LibreEvolve release can be considered reviewed. It is not itself signed release
provenance, and it does not prove a package was published to an index.

## Required Local Evidence

- Build exactly one wheel and one source distribution with
  `py -3.12 -m build --wheel --sdist`.
- Verify every file under the `libreevolve/` package tree is present in both
  the wheel and source distribution.
- Install the built wheel into an isolated virtual environment.
- Smoke both command entrypoints: `libreevolve --help` and
  `python -m libreevolve --help`.
- Write `dist/release_artifact_provenance.json` with wheel/sdist hashes and
  selected source-file hashes.
- Upload or otherwise preserve the wheel, source distribution, and provenance
  JSON from the release-smoke run.

## Evidence Still Outside This Checklist

- Signed release provenance.
- Published-index or private-index artifact verification.
- A maintainer-approved release event that ties the reviewed checklist result to
  a public or private package version.
