# Package metadata component report

Status: root-integrated dependency-policy change; build/install evidence
passed; repeat-build parity remains open.

Owned paths: `pyproject.toml`, `libreevolve/__init__.py`.

Agent: `01a06255-f3c5-71a3-8d77-a921e473bc60`. Independent verifier: none.

Change: `pypdf` was bounded to `>=6.6,<6.11` to make cached-PDF extraction
evidence reproducible; development documentation records the same policy.

Evidence: local wheel/sdist/editable installs and package/CLI smoke checks
passed in isolated Python 3.12 environments. Repeat builds were not
byte-identical, so release reproducibility is not complete.
