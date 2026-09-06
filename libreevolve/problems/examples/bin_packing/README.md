# Integer bin packing (early alpha)

Candidate interface: `pack(items: list[int], capacity: int) -> list[list[int]]`.
The initial program is valid next-fit, intentionally leaving optimization room.
All corpus data lives in `validate.py`, outside the candidate workspace.

Coordinator interface: load `validate.py` and call `evaluate(code: str) -> dict`
for training, or `evaluate_holdout(code: str) -> dict` separately after freezing
the selected candidate. Both return `quality` and `is_valid`; valid results
also include `total_bins`, `lower_bound_bins`, and `case_count`. These diagnostics
are declared non-primary metrics; invalid results include zero placeholders for
all three to satisfy the engine's strict metric schema. Their bounds cover both
fixed corpora (fewer than 10,000 items and 100 cases each); only `quality` drives
primary fitness. To evaluate the
baseline, read `initial_programs/seed.py` and pass its text to either function.
There is no separate `evaluate_baseline` function.

Quality is the corpus sum of volume lower bounds divided by total bins used.
It is positive and at most one for valid results, and strictly increases when
total bins decrease on the same corpus. Empty instances must return `[]` and
contribute zero to both totals. Invalid results receive zero and fail validity.
The lower bound need not be attainable; quality one is not promised. Compare
candidates within the same split, not raw scores between different splits.

Training has 55 handcrafted and seeded cases: duplicates, edge cases, uniform,
ordered, small-item, and complementary-pair workloads. Holdout has 30 cases
using a different seed, capacities, lengths, and bimodal, near-half, and discrete
distributions. Local RNGs and immutable case tuples keep evaluation repeatable.
The validator compares exact types, capacity, and multiplicities against the
original tuple even when the candidate consumes or sorts its input.

Only `evaluate` is wired to the normal search contract. Do not feed holdout
results into prompts, selection, tuning, or stopping decisions. These public
fixtures are a reporting split, not a secret test set or protection against
deliberate introspection. First-fit-decreasing test results calibrate that an
established heuristic improves on the seed; they are not discovery evidence.

The engine supplies its usual temporary local subprocess and timeout boundary.
Direct validator calls execute candidate Python in the caller. Neither is a
hostile-code security sandbox. The small corpora target sub-second ordinary
heuristic evaluation; subprocess startup and candidate behavior affect latency.
