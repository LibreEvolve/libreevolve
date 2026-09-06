# Early alpha delivery

Objective: install, optimize a small Python heuristic with a real model, inspect
quality and cost, and export an independently validated candidate without help.
Source objective: user attachment 303108df-80e6-4522-bfdb-951f4a3d3117/pasted-text-1.txt.
Baseline: 462443213b7391a6622d539a0564f14444e0cfce.
Branch: codex/early-alpha-20260905. Original shared checkout is preserved.
Candidate: 8621ea69b4d8bc6c2b5aafec75b8a90056a6a338. Merged into the private
LibreEvolve/libreevolve master at a906b53e138c5598edc40c12154f2d5f9635d6df.

## Milestones and acceptance evidence

| Milestone | Owner | Dependencies | Required evidence | State |
| --- | --- | --- | --- | --- |
| Bin-packing example | Galileo | baseline | valid next-fit seed, deterministic training/held-out corpora, negative correctness tests, measured positive calibration | local evaluator passed |
| Init and preflight | coordinator | example | clean template creation, bounded config, useful failures, no network during offline checks | local workflow passed |
| Reliability | Mill + coordinator | baseline | reproduce docs helper fault, inspect cancellation/persistence and prompt compatibility, regression tests | 496 broad loop/reliability tests pass, 2 skip |
| Report and export verification | Plato + coordinator | example, runtime inspection | baseline/best, held-out checks, diff, usage/cost/status; failure report; HTML escaping and artifact binding | 33 combined tests pass, real offline CLI smoke passes |
| Repeated real runs | coordinator | supported workflow, spending authorization | all attempts retained, independent seeds, comparable baseline/export reevaluation, actual usage and estimated spend | pending |
| Package and CI | coordinator | implementation | exact candidate commit, wheel/sdist, coverage/hashes, clean Windows Python 3.12 install, CLI workflow, passing CI | 8621ea69 wheel/sdist and clean Windows Python 3.12 offline workflow verified; CI billing blocked |
| External usability | coordinator + participants | installed workflow | 3–5 users, time/errors/help/export comprehension, approximately 30 minutes | trial materials prepared; participant evidence pending |

Initial declared reference environment: Windows with Python 3.12. Additional
platform support requires its own installed-package evidence. Initial provider
path: OpenAI, with user-selected model and explicit configured token price;
model availability and price are not assumed or hardcoded.

## Evidence rules

Use the existing engine, budget controls, run/show commands, and exporters.
Evaluator and held-out inputs remain outside candidate editable workspaces.
Local subprocess evaluation is not a hostile-code security sandbox.
Paper retrieval is outside onboarding; no hosted service or pending-work resume
claim. User trial materials can be prepared without contacting participants.

No live call is authorized by a default config. Before live experiments record
the user's aggregate dollar cap, model, current price source, attempts, seeds,
and stopping rules. Finish offline work before treating absent live access as
a blocker. Estimated token-price budgets are not billing guarantees.

The release checklist, complete relevant regressions, interruption tests,
installed-package runs, real-model attempts and independent user trials are
separate gates. Do not substitute scripted mutations for real-model evidence.
Required incomplete gates keep the goal active. Public publication and deployment
require authorization; a local candidate commit is part of packaging evidence.
