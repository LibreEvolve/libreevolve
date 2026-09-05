# problems/benchmarks/matrix_results.py inventory

Evidence state: measured/read-only Wave 1 report.

Measured shape: 7,534 physical LOC, 7,164 logical LOC, 160 top-level
functions, 16 frozen dataclasses, 1,373 decision nodes, and an aggregate
complexity proxy of 1,533. High fan-in helpers include `_load_report`, safe
relative paths, stable JSON SHA, text fields, runtime path/SHA validation, and
the public report validator.

The façade owns matrix result schema, runtime/cascade/evolution boundaries,
publication bundles, artifact inventories, canonical JSON, and source/rights
bridges. Proposed seam: artifact identity and canonical serialization helpers,
while keeping schema policy, registry interpretation, rights selection, public
imports, and package exports in the façade.
