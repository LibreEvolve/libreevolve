# Continuation checkpoint

Goal remains active. Current candidate 97a5a822acfa9084355fdc6f2faf707e9bc63e1b
on private LibreEvolve branch codex/early-alpha-20260905; remote hash verified.
Runtime implementation commit d8911edd100c6ea23b59b6359390c021ce72f184; following
commit only makes paid integration CI explicit opt-in. No default-branch merge.

## Live handles — poll these; do not restart merely for elapsed time

- Session 55841 completed: Windows pytest tests/core/test_loop.py plus
  tests/test_alpha_reliability.py: 496 passed, 2 skipped in 704.55 seconds.
- Session 95463: PYTHONDONTWRITEBYTECODE=1 Windows pytest tests/ -m
  "not integration" --tb=short -q. Last observed beyond 65%, no failure printed.
  Began at runtime implementation commit; alpha and documentation fixes were
  made while running. This is not exact-final-candidate full-suite evidence.
- Galileo agent 01a0731a-e26c-72f3-9b49-831fd839bd56 completed read-only
  re-review: no residual blocking defects in doctor/export fixes. Explicit
  history source and CRLF-only equivalence would benefit from dedicated tests.
- Session 20709 ended with a precondition failure: baseline unstaged, not a
  completed scan. Baseline metadata update is now explicitly staged. A transient
  Git lock cleared naturally after session 95616 finished; no lock was deleted.

## Uncommitted follow-up and fresh evidence

Doctor labels mutation-disabled credential checks as skipped. Export defaults
to rejecting workspace/history disagreement and supports explicit source choice,
verifying and exporting the same frozen bytes. Oversized finite budgets now
produce an actionable CLI error rather than OverflowError. Canonical onboarding
guide is docs/alpha-quickstart.md, linked from README/docs index and the old draft.
The roadmap scan includes the new guide (29 Markdown files).

Session 2935 completed: 41 passed in 8.88 seconds for onboarding, full offline
workflow, AGENTS docs, roadmap scan, README map, and docs reader-path tests.
Secret scanner updated baseline line metadata and timestamp; CRLF churn was
normalized. Review its final result before committing. No live calls made.
Session 95616 completed: git diff --check passed. Full-suite session 95463
subsequently reached 77 percent without printed failures and remains live.

Follow-up secret scan session 54956 completed with hook exit 3: many potential
secrets, prominently Hex High Entropy String entries in paper inventory JSON;
baseline also modified by the scanner. These findings are NOT yet reviewed or
cleared. Do not blanket-allowlist them. Capture subsequent scanner output in a
bounded per-file/type summary rather than dumping thousands of findings.
Workflow test now additionally exercises explicit history export and CRLF-only
equivalence with raw-byte hash agreement (session 41945).

## Latest continuation

Session 41945 passed (1 workflow test, 5.26 seconds). Full suite 95463 remains
live beyond 82 percent, no failure printed. Fresh all-alpha suite session 49879
is live beyond 58 percent. Do not restart either on elapsed time.

Bounded secret scan session 85993 ended: 3005 new findings, of which 3002 Hex,
2 Secret Keyword, 1 Base64. Files: paper proposition inventory 1432, prose 558,
math 403, table-cell 300, code-listing 215, source-detail 69, documentation-claim
9, benchmark-coverage 8, status-claim 6, tests/core/test_feedback.py 3, planning
FILE_MATRIX and OWNERSHIP_MATRIX one each. Existing CI requires this scan.
No broad exclusion or new baseline acceptance was added. Baseline staged and
unstaged changes are scanner line-number/timestamp metadata; scanner CRLF churn
was normalized again after diff-check 35438 reported whitespace. Recheck after
future scanner writes. Galileo reactivated read-only to classify exact matches;
normalization of baseline paths by detect-secrets was confirmed from source,
so no portability migration is needed just for backslashes.

PLAN.md and EVIDENCE.md now distinguish previous 97a5a822 wheel evidence from
uncommitted follow-up fixes. New guide and checkpoint remain untracked until
explicit final staging. Original shared checkout remains untouched.

## Package and installed results

Windows build exit 0. dist/97a5a822 contains wheel, sdist and provenance JSON.
Coverage: all 455 package files in both distributions; wheel source bytes equal
current source bytes. Explicit Windows GIT_DIR/GIT_WORK_TREE environment was
needed for provenance because this worktree was created by WSL Git.

- wheel SHA-256: 2004e589a651ec61acef873288939f8e6d7266dea59eb995568d218374ca6829
- sdist SHA-256: f8d05093d65bd70a4eaf137347b32abff8702dbf1dd6c2f1a03813db8f2ebbe1
- provenance source: 97a5a822acfa9084355fdc6f2faf707e9bc63e1b, tracked files clean

Clean environment outside checkout:
C:/Users/timot/AppData/Local/Temp/libreevolve-alpha-wheel.NUDGXn/venv.
Verified imports from its site-packages; pip check and both CLI help paths pass.
Initially installed d8911edd wheel, then reinstalled exact 97a5a822 wheel without
dependency changes. Both full offline workflow attempts pass. Current-head
run/report/export exited 0 under session 66857; artifacts at external temp root
runs/installed-head, head-result.html, verified-head/verification.json.
Both correctness splits pass; exported bytes match code SHA-256
a37e6880acd271cbb5ad50b781d95b8e71d9fbbde15701505738d62f51d06507.
This evaluates the seed only; zero real-model calls and no discovery claim.

## Remote CI blocker

Private repo LibreEvolve/libreevolve confirmed ADMIN access and isPrivate true.
Runs 33989147661 (Installed Alpha) and 33989147632 (Tests) failed before steps
started. Check-run annotation 101368106016 explicitly says recent account
payments failed or spending limit needs increasing. User/account action needed;
do not bypass billing limits or describe these as code failures/green checks.
Paid Anthropic integration and source refresh were skipped as intended.

## Next work

Capture terminal results from live tests, review findings and fix concrete
issues. Preserve required full-suite/source-scope evidence through any repairs.
Finish release secret/doc checks and usable final onboarding documentation.
Keep exact candidate/artifact/install evidence tied together when code changes.
Real-model protocol and user trial materials are prepared. No live spending
cap/credential use or participant contact has been authorized for this goal.
Finish independent offline work before requesting the specific live cap/access.
No goal completion until required gates are actually satisfied.

## Most recent progress (supersedes earlier live-status notes)

- Alpha suite 49879 ended: 124 passed in 70.61 seconds.
- Provenance/AGENTS checks 8671 ended: 17 passed in 1.50 seconds. An initial
  command used a nonexistent test filename and collected no tests; corrected
  command used tests/test_release_artifact_provenance.py.
- Full suite 95463 remains live beyond 83 percent, no failure printed. Keep
  polling the same handle; it is still mixed-source rather than exact-candidate.
- Independent read-only scan review classified exactly 3005 new findings:
  3000 complete SHA256 JSON fields, two locally resolving Git commits, three
  synthetic redaction-test strings at test_feedback.py lines 1920/1975/2070.
- Galileo is now AUTHORIZED WRITER for .secrets.baseline and
  planning/early_alpha/SECRET_REVIEW.md only. Submission
  01a07342-da54-7db3-ac82-ed1e238c33c4 requests exact reviewed additions,
  preserved existing entries/settings, LF normalization, no staging or hook.
  Await its terminal status before coordinator baseline staging/scanning.
- Installed-alpha CI now records exact-commit provenance, pip check and
  retained run/report/export artifacts. YAML structure parse passed; remote
  execution remains unproven. These workflow changes are uncommitted.
- Non-baseline git diff --check passed (session 74088). Final baseline check
  must follow writer completion. EVIDENCE.md reflects newest test results.

## Scanner convergence follow-up

All candidate files explicitly staged (15 files); no broad add used. Initial
reviewed update completed with 5814 records. Configured hooks 10633, 86491 and
69024 found NO new secrets, but each exited nonzero due to baseline metadata
refresh. Hook trimmed two stale status_claim_inventory Hex records (old2190,
2713), leaving5812 including all3005 reviewed false additions. Settings match
HEAD exactly. Later passes updated different old line numbers, consistent with
concurrent hook chunks overwriting one another's metadata refreshes.

Galileo reactivated as exclusive .secrets.baseline/SECRET_REVIEW.md writer for
single-process line-number-only refresh of exact existing path/type/hash rows.
Preserve all5812 records, detector settings and review flags; no new findings
accepted. Do not stage or rerun hook until writer completion. Latest baseline
may have CRLF from hook; writer instructed to normalize LF.
Full suite95463 still live beyond84 percent; no failures printed. No new
provider requests or billing/account actions. Candidate not yet committed.

## Secret gate passed

Galileo metadata refresh session52603 exited0; 436 line updates, all5812 rows
preserved, no new additions/settings changes. Earlier48981 failed before writes
on finding-drift assertion; restart was not due to elapsed time. Writer stopped.
Hook19890 then refreshed serialization/metadata with no new findings. After
staging, hook87454 exited0: PASSED, no findings, baseline not modified.
Remote CI33989147661/check101368106016 rechecked: still completed failure due
to billing before execution for97a5a822, not a code failure or passing evidence.
Full95463 remains live beyond85 percent; no failure printed. Final candidate
can now be committed and packaged, retaining mixed-source full-suite caveat.
