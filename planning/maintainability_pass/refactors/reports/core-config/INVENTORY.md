# `core/config.py` Wave 1 Inventory

Primary file: `libreevolve/core/config.py`
Lane: `core-config`
Agent: `01a069d1-1bf6-7720-8a6d-912ffcad6a7a`
Status: read-only inventory; characterization completed and no production
writer authorized in this wave

## Measurements and ownership

Current source measurement is 2,776 physical lines, 2,592 nonblank lines,
2,587 token-line proxy, two classes, 86 module-level functions, and two
`Config` methods. Largest/highest-proxy symbols are `Config.validate` (about
398 lines), `_validate_eval_stages` (203/64), `_validate_backends` (164/40),
`_validate_candidate_build_systems` (123/14),
`_validate_candidate_execution_environment` (123/20),
`_validate_stage_hypothesis_test` (91/27), and `_validate_llm_feedback`
(85/25). The proxy is an AST branch/control-flow count, not formal McCabe
complexity.

`ConfigError`, `Config`, `Config.__post_init__`, `Config.validate`,
`canonicalize_env_var_allowlist`, and retry/evaluator/adaptive/candidate
execution constants are de facto public/imported surfaces. `Config` combines
defaults, nested schema validation, normalization, paths, provider/backend
policy, evaluator stages, candidate runners, prompt policy, plugin specs, and
runtime limits. `validate()` mutates normalized fields including `log_dir` and
nested mappings/lists; database serialization makes field names, ordering, and
normalized values durable manifest contracts.

Direct production importers include CLI, loop, evaluator, database, budget,
async controllers, ensemble, island code, and matrix fixtures. `.env` loading
belongs to CLI (`_build_config`, `_load_problem_config_yaml`, and
`_load_cli_dotenv`); this lane did not read `.env`.

## Characterization and handoffs

Relevant tests are `tests/core/test_config.py`, CLI dotenv/config tests,
database runtime revalidation/manifest tests, and loader/config boundary
tests. The current focused Windows Python 3.12 characterization reports
`639 passed`. No test paths were changed by this lane. Native Windows and
runtime evidence remain unverified.

Proposed seam: extract pure contract validation/normalization into a new
`libreevolve/core/config_contract.py`, retaining `Config`, `ConfigError`,
defaults, compatibility exports, and policy ownership in `config.py`. Keep
YAML parsing and `.env` loading in their separate lanes. Proposed later
allowlist: `config.py`, new `config_contract.py`, and focused config tests;
additional caller changes require explicit handoffs.

The lane remains a no-op because the characterization and coupling review did
not authorize a safe support-module extraction; the existing façade and its
dirty-path attribution are preserved.
