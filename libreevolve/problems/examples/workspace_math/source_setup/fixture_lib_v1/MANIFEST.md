# workspace_math Fixture Source Setup

This directory records the pre-marker source shape for the `workspace_math`
smoke fixture.

It is a local fixture bundle, not an upstream third-party project. The evolved
problem under `initial_programs/baseline/` adds canonical Python
`# EVOLVE-BLOCK-START/END` markers around `main.py:solve` and
`pkg/helpers.py:base_value` without changing the executable Python statements.

The binary fixture asset is intentionally represented by hash in
`codebase_integration.yaml`; the active candidate workspace still carries the
copied `assets/offset.bin` file.
