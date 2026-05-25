# README Todo: Incorrect or Unsupported Claims

This list tracks README statements that are inaccurate, misleading, or too
strong after comparing the current code, `papers/`, and AlphaEvolve sources.

## AlphaEvolve Comparison Table

- [x] Correct "Gemini only" in the AlphaEvolve column.
  - README evidence: `README.md:66` says AlphaEvolve uses "Gemini only."
  - Spec evidence: the AlphaEvolve paper says it is model-agnostic and shows a
    "Choice of existing or custom LLMs" in the task setup, while the published
    experiments use Gemini 2.0 Flash and Gemini 2.0 Pro.
  - Required result: change this to a precise statement such as "published
    experiments use Gemini Flash/Pro; system is described as model-agnostic."

- [x] Correct "Extensibility: None" for AlphaEvolve.
  - README evidence: `README.md:70` says AlphaEvolve has no extensibility.
  - Spec evidence: AlphaEvolve supports user-provided evaluation code,
    configurations, custom/existing LLMs, prompt customization, explicit
    context, stochastic formatting, and evolve-block markers.
  - Required result: compare the real extension surfaces rather than claiming
    AlphaEvolve has none.

- [x] Qualify "Population model: Proprietary database."
  - README evidence: `README.md:67` contrasts AlphaEvolve's proprietary
    database with LibreEvolve's MAP-Elites and islands.
  - Spec evidence: the paper states AlphaEvolve's database is inspired by
    MAP-Elites and island-based population models.
  - Required result: say AlphaEvolve has a closed evolutionary database inspired
    by MAP-Elites/island models, while LibreEvolve has a small local
    MAP-Elites/island implementation.

- [x] Qualify "Evaluation: Internal infrastructure" versus "Cascade evaluator."
  - README evidence: `README.md:69`.
  - Spec evidence: AlphaEvolve supports user-defined evaluation functions,
    optional evaluation cascades, LLM-generated feedback, and parallelized
    evaluation.
  - Required result: avoid implying LibreEvolve has equivalent cascade behavior;
    call out that LibreEvolve has a fixed three-step local subprocess cascade.

## Research References and Bundled Papers

- [x] Fix the references count.
  - README evidence: badges and text claim 23 references
    (`README.md:15`, `README.md:72`, `README.md:356`, `README.md:360`).
  - Current evidence: `papers/download_manifest.csv` has 24 downloaded entries
    excluding the header.
  - Required result: decide whether the source of truth is 24 local papers or a
    curated 23-paper list, then update badges/text/manifest accordingly.

- [x] Remove or revise "does not bundle them."
  - README evidence: `README.md:360` says the repository "does not bundle" the
    cited papers.
  - Current evidence: the checkout has a `papers/` directory with downloaded
    PDFs and a manifest.
  - Required result: either stop bundling PDFs or document that the repo
    includes a local paper cache/manifest.

- [x] Expand the research table or explain why most downloaded papers are not
  listed.
  - README evidence: `README.md:364-380` lists 10 named references.
  - Current evidence: `papers/download_manifest.csv` lists 24 downloads,
    including domain result papers and benchmark/problem papers.
  - Required result: include all referenced local papers, split them into
    "system", "benchmarks/results", and "foundational" groups, or state that
    the README table is intentionally partial.

## Feature Claims

- [x] Replace "parallel populations" wording for islands.
  - README evidence: `README.md` described 5-island migration as "Parallel
    populations."
  - Current evidence: `IslandModel` keeps multiple MAP-Elites archives but runs
    synchronously in-process; no population worker concurrency exists.
  - Status: README now says "synchronous island archives" instead of implying
    parallel execution.
  - Required result: avoid using "parallel" for islands until there are actual
    concurrent island workers.

- [x] Soften UCB1/backend-routing claims.
  - README evidence: README called the ensemble "UCB1" and said it
    "automatically learns which model produces the best mutations."
  - Current evidence: `LLMEnsemble` is a UCB-style heuristic over unnormalized
    fitness improvements, with known canonical-UCB gaps tracked in
    `docs/todo/papers.md`.
  - Status: README now uses "UCB-style" and describes routing as tracking
    observed fitness improvements.
  - Required result: keep marketing text aligned with the heuristic
    implementation unless canonical UCB1 is implemented and tested.

- [x] Qualify "Feed it a problem, a seed program, and any LLM."
  - README evidence: `README.md:22`.
  - Current evidence: supported backend types are hard-coded to OpenAI,
    Anthropic, and Ollama in `build_llm()`.
  - Required result: say "any configured OpenAI/Anthropic/Ollama-compatible
    backend currently supported" or add a backend plugin interface.

- [x] Qualify the plugin names as inspired approximations, not implementations
  of the cited systems.
  - README evidence: `README.md:298-302` names CausalEvolve, DeepEvolve,
    ImprovEvolve, and ThetaEvolve as built-in plugins.
  - Current evidence: plugins are lightweight heuristics/stubs:
    CausalEvolve is regex/UCB1 factor guidance, DeepEvolve is arXiv Atom search,
    ImprovEvolve is a static prompt block, and ThetaEvolve writes JSONL without
    training.
  - Required result: use names such as "CausalEvolve-inspired" and document
    what is missing from each paper.

- [x] Qualify "comprehensive test coverage."
  - README evidence: `README.md:59` claims comprehensive coverage across all
    components.
  - Current evidence: the local non-integration suite now has 159 selected
    tests, but major AlphaEvolve features are still absent or represented only
    as narrow prototype behavior.
  - Required result: keep the count but change the coverage claim to the
    current prototype surface.

- [x] Correct test commands for this machine.
  - README evidence: `README.md:327-331` uses `pytest`.
  - Project instructions: `AGENTS.md` says to use `py -3.12 -m pytest`.
  - Current evidence: tests run successfully after installing dev extras, and
    documentation now uses `py -3.12 -m pytest`.
  - Required result: document installation first and use `py -3.12 -m pytest`.

- [x] Qualify model names as examples, not guaranteed current model IDs.
  - README evidence: `README.md:31`, `README.md:51`, `README.md:99-105`,
    `README.md:212-214`.
  - Current evidence: the code forwards model strings to vendor SDKs and does
    not validate availability.
  - Required result: say model names are examples and add validation or docs for
    provider-specific availability.

## Architecture Description

- [x] Correct prompt-evolution placeholder guarantee wording.
  - README-adjacent evidence: architecture/configuration docs described
    meta-prompt mutation as preserving placeholders.
  - Current evidence: `evolve()` asks the LLM to keep placeholders but
    `PromptDatabase.mutate()` accepts arbitrary template text without
    validation.
  - Status: architecture/configuration docs now state that placeholder
    preservation is instructed but not enforced.
  - Required result: avoid implying prompt mutation is validated until the
    placeholder-validation todo is implemented.

- [x] Add missing AlphaEvolve gap callouts to the README architecture section.
  - README evidence: `README.md:225-254` presents the package architecture.
  - Missing from README: evolve-block markers, prompt sampler, multi-objective
    metrics, evaluator result objects, async controller/workers, meta-prompt
    database, full-code mutation mode, and language/workspace runners.
  - Required result: add an "AlphaEvolve fidelity gaps" subsection or link to
    `docs/todo/code.md`.

- [x] Clarify that the current problem format is Python-only and local-workspace.
  - README evidence: `README.md:258-285` describes `validate.py`, seed files,
    and optional seed workspaces.
  - AlphaEvolve contrast: AlphaEvolve evolves marked regions inside an existing
    codebase and can evaluate complex workflows.
  - Required result: explicitly state current Python/local-workspace scope and
    remaining arbitrary-language/build-system limitations.

- [x] Rework the "Comparison to AlphaEvolve" section so it does not overstate
  LibreEvolve as a feature superset.
  - README evidence: `README.md:61-72`.
  - Required result: present LibreEvolve as an open prototype with several
    deliberate divergences and many missing AlphaEvolve features.
