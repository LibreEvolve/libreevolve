# LLM component report: provider adapters

Status: isolated partial; no shared LLM patch integrated; verifier absent.

Owned paths: `anthropic.py`, `openai.py`, `openai_compat.py`, `gemini.py`,
`ollama.py`, and `codex_cli.py`.

Agent: `01a06257-001f-7e10-b1a5-bca3bebe99a9`. Independent verifier: none.

Evidence: isolated adapter tests reported `117` passing before the safety stop.
The broader LLM lane reported `502 passed, 1 failed` in its baseline slice;
that failure was not converted into a shared patch. Live credentials and
provider parity were intentionally not exercised.

Disposition: open/unverified; maintain the opt-in live-provider boundary.
