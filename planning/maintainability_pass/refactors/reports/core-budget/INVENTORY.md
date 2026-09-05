# core/budget.py inventory

Evidence state: measured/read-only Wave 1 report.

Measured shape: 1,497 physical LOC, 1,385 logical LOC, two classes, 42
top-level functions, and 18 `RunBudget` methods. `RunBudget` spans lines
111-569; `validate_controller_budget_event` and `_check_limits` are the main
complexity hotspots. Direct production consumers are loop and database; async
sampling/evaluation reservations, retries, cancellation, persistence, and
reporting remain owned by adjacent modules.

The cohesive future seam is the pure budget-contract kernel: cumulative
counters, limit precedence, snapshot/restore validation, controller-event
validation/application, and replay. Do not move async reservation or provider
cancellation into it.
