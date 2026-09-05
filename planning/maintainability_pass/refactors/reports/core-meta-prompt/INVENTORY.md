# core/meta_prompt.py inventory

Evidence state: measured/read-only Wave 1 report.

Measured shape: 919 physical LOC, 836 nonblank LOC, three classes, 29
top-level functions, and 15 methods. `PromptDatabase` spans about 411 LOC;
large symbols include `record_result`, `parse_prompt_mutation_response`,
`mutate`, and `_program_from_history_record`.

The module owns prompt-program identity/lineage, selection, scoring, mutation
parsing, history replay, quarantine, penalties, defensive copies, and
deterministic IDs. `prompt.py` owns semantic template validation; loop owns
provider context, synchronous/asynchronous orchestration, and runtime joins.
`artifact_schema.py`, `jsonl.py`, redaction, config, and database are adjacent
contracts. The proposed seam is one prompt-arm lifecycle contract, not a
provider-context or loop rewrite.
