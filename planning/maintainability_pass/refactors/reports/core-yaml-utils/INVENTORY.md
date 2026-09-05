# core/yaml_utils.py inventory

Evidence state: read-only Wave 1 report.

The module is approximately 67 LOC with one class and four functions. It is a
small shared parsing seam used by configuration and problem loading. Its key
contract is duplicate-key rejection plus deterministic YAML decoding and
mapping validation at callers. The proposed ownership boundary is a pure
loader/parser utility; it must not absorb configuration policy or problem
metadata ownership.

The adjacent loader review identified a direct consumer hazard: callers using
`safe_load_unique(...) or {}` can turn falsey non-mapping YAML documents into an
empty mapping before validation.
