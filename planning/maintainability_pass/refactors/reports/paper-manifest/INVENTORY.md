# tools/paper_manifest.py inventory

Evidence state: measured/read-only Wave 1 report.

Measured shape: 15,430 physical LOC, 14,634 logical LOC, 364 top-level
functions, six frozen dataclasses, 5,936 statement AST nodes, and an aggregate
complexity proxy of 2,230. `validate_paper_manifest` fans into 293 unique local
helpers. The file eagerly imports 270 benchmark modules and exposes 590
symbols.

The module owns paper source/PDF/cache validation, sidecar claim inventories,
rehydration statuses, safe paths, hashes, redacted diagnostics, and report
serialization. Proposed seam: a data-driven sidecar specification/runner that
preserves validator order, public names, monkeypatch seams, claim inventories,
Appendix A, and PDF/source special cases. Benchmark matrix and rights
authorities remain separate handoffs.
