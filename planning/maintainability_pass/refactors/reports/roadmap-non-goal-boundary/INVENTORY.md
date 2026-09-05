# Roadmap non-goal Markdown boundary inventory

Primary: `libreevolve/problems/benchmarks/roadmap_non_goal_markdown_scan_boundary.py`.

The current scanner recursively includes all Markdown paths except its listed
generated/cache directories and now explicitly excludes the `planning`
directory. The current checkout observes 27 governed non-planning files; the
prior pre-fix scan included coordination records and is retained only as
historical diagnostic context.
Clean `HEAD` observes 77 total, with the same 27 non-planning product/document
files. The two failing terminal assertions therefore identify a stale boundary
rather than a missing product document.

The direct test contract asserts the governed count, safe-scope phrases,
line-level records, and explicit non-promotion evidence. The intended seam is
the corpus directory policy; no runtime or promotion claim is authorized.
The source verifier matched the baseline/current hashes and passed the focused
tests and direct validator; strict diff output remains EOL-qualified.
