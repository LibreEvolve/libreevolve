# Engineering-preview release checks

Before publishing a candidate:

1. Verify the intended remote and exact source commit. Preserve unrelated
   work and use an isolated worktree.
2. Run the complete retained offline test suite.
3. Build wheel and sdist. Check that both contain the bin-packing assets
   and required Python modules, with no experimental providers or collections.
4. Install the wheel into a fresh environment outside the checkout and run
   `pip check`, CLI/module help, initialization, offline preflight, a
   zero-generation seed run, inspection, HTML reporting and verified export.
5. Check the exported candidate hash and fresh training/held-out correctness.
   Exercise output-collision and source-conflict protection in the tests.
6. Record exact source and distribution identities with the existing
   `libreevolve.tools.release_artifact_provenance` command.
7. Label results accurately: offline verification is not new live model,
   external-usability or hosted-CI evidence. Any real Codex request needs
   separate authorization for subscription use.

Keep the product labeled **engineering preview**. Subscription charges may be
unknown. Candidate execution is a local subprocess, not a security sandbox.
Do not claim cross-platform live parity from one host.

The GitHub workflows remain manual-only during the existing billing pause.
Publication does not authorize CI repair, force-pushes or unrelated branch
deletion.
