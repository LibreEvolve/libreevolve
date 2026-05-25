# Backends

LibreEvolve supports three backend types through a common `generate(prompt) ->
str` interface:

- OpenAI
- Anthropic
- Ollama

The bandit router that selects among them is implemented in
[`libreevolve/llm/ensemble.py`](../libreevolve/llm/ensemble.py).

## Selection and reward

`LLMEnsemble` wraps one or more backends and chooses one backend per mutation
attempt using a UCB-style heuristic over observed fitness improvements. It is
not a canonical UCB1 implementation; reward-normalization gaps are tracked in
[`docs/todo/papers.md`](todo/papers.md).

Current behavior:

- `generate(prompt)` returns both the raw backend response and the backend index
- selection counts are incremented when a backend is chosen
- rewards are recorded only after evaluation
- the evolution loop clamps reward to `max(0.0, score - parent.fitness)`
- critique, feedback-grader, and meta-prompt calls currently share this same
  selection/count state even though only candidate mutation calls receive an
  improvement reward
- provider response metadata is not persisted. Token usage, latency, retry
  counts, API mode, request/response ids, finish reasons, and raw provider
  diagnostics are discarded by the backend adapters.

This means backends are rewarded for improvement over the selected parent, not
for absolute score, and role-specific auxiliary-call accounting remains a known
gap.

## OpenAI backend

Implemented in [`libreevolve/llm/openai.py`](../libreevolve/llm/openai.py).

Constructor fields:

- `model`
- `max_tokens`
- `reasoning_effort`

Behavior:

- if `reasoning_effort` is not set, the backend uses Chat Completions
- if `reasoning_effort` is set, the backend uses the Responses API
- both code paths retry up to 3 times with exponential backoff
- there is no automatic model-capability detection; a reasoning-capable model
  without `reasoning_effort` still follows the Chat Completions path

API split:

- Chat Completions call:
  - `chat.completions.create(...)`
  - uses `max_completion_tokens`
- Responses call:
  - `responses.create(...)`
  - uses `max_output_tokens`
  - passes `reasoning={"effort": ...}`

OpenAI currently recommends Responses for new projects, and its docs describe a
richer experience for reasoning models through Responses. LibreEvolve has not
yet made Responses the default OpenAI path or added model/parameter validation.

## Anthropic backend

Implemented in [`libreevolve/llm/anthropic.py`](../libreevolve/llm/anthropic.py).

Constructor fields:

- `model`
- `max_tokens`

Behavior:

- uses `messages.create(...)`
- returns the first text block from `msg.content`
- retries up to 3 times with exponential backoff

## Ollama backend

Implemented in [`libreevolve/llm/ollama.py`](../libreevolve/llm/ollama.py).

Constructor fields:

- `model`
- `max_tokens`

Behavior:

- uses `ollama.chat(...)`
- passes `num_predict` as the output token limit
- retries up to 3 times with exponential backoff

This backend is useful for local experimentation where API cost or offline work
matters more than peak model quality.

## Environment setup

Typical environment variables:

```text
OPENAI_API_KEY=...
ANTHROPIC_API_KEY=...
OLLAMA_HOST=http://localhost:11434
```

The CLI loads `.env` automatically before command execution.

## Adding a new backend

Today, adding a provider is a source-code extension, not a config-only plugin.
This is an AlphaEvolve-alignment gap tracked in
[`docs/todo/code.md`](todo/code.md). To add a new provider today:

1. Implement a backend class with:
   - `generate(prompt) -> str`
   - `name` property
2. Update `build_llm()` in
   [`libreevolve/llm/ensemble.py`](../libreevolve/llm/ensemble.py) so the new
   backend type string resolves to that class.

Minimal skeleton:

```python
class MyBackend:
    def __init__(self, model: str = "my-model", max_tokens: int = 4096):
        self._model = model
        self._max_tokens = max_tokens

    @property
    def name(self) -> str:
        return f"mybackend/{self._model}"

    def generate(self, prompt: str, **kwargs) -> str:
        ...
```

## Practical guidance

- Prefer non-reasoning OpenAI or Anthropic models when you want cheaper, shorter
  mutations.
- Use `reasoning_effort` sparingly. Long internal reasoning can consume output
  budget and reduce useful diff text.
- Mix backends when exploring a new problem. The ensemble tracks which backend
  has produced useful mutations for that task.
