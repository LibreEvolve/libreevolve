# Preparing a local share bundle

LibreEvolve provides an explicit, local-only sharing workflow. It does not
upload, publish source, configure hosting or grant permission to deploy. A
generated bundle is not an authentic live-model demonstration merely because
it renders.

## Three separate operations

1. **Prepare:** resolve a saved candidate and perform fresh local checks. This
   executes candidate Python with host access, using the existing timed
   verification workers. It is not a security sandbox and makes no model call.
2. **Inspect:** validate and display a frozen, allowlisted proposal and its
   canonical SHA-256. This does not execute candidate code.
3. **Render:** approve that exact payload and write deterministic static files.
   This does not execute candidate code, fetch resources or upload anything.

The existing `alpha report` and verified `alpha export` commands retain their
old authority. Neither authorizes sharing. In particular, reports check the
on-disk workspace; export and share preparation support explicit history or
workspace selection when those sources differ.

## Prepare and review

After installing the engineering-preview checkout, use its environment
executable. Replace `RUN`
with a trusted saved run. Choose new paths and a deliberately public identifier;
do not reuse a private run path or account name as that identifier.

```bash
.venv/bin/libreevolve alpha share prepare RUN --public-id experiment-one --output proposal.json --evidence private-preparation.json --allow-local-execution
.venv/bin/libreevolve alpha share inspect proposal.json
```

On Windows use `.venv\Scripts\libreevolve.exe`. No native Windows validation is
implied by that executable spelling.

Preparation defaults to the training split. `--split holdout` selects a
reporting view; candidate selection is frozen before fresh held-out checks.
Never use these checks to tune a supposedly untouched holdout. The bundled
held-out corpus is public reporting data, not a secret challenge set.

If workspace bytes differ from history, preparation stops before verification.
Choose `--source history` or `--source workspace` deliberately. Private
preparation evidence records the choice and whether the bytes match history.
No history ID is turned into a public identity automatically.

Review **every** field of `proposal.json`, including descriptions, corpus and
provenance hashes. Hashes can link private artifacts. If you edit the proposal,
run `inspect` again: the prior approval digest no longer applies. A hash binds
bytes; it does not authenticate their author or establish factual truth.

## Render after record-specific approval

Copy the exact digest printed by `inspect`; `REVIEWED_SHA256` below is a
placeholder, not an approval. Keep the named operator and receipt private.

```bash
.venv/bin/libreevolve alpha share render proposal.json public-result --approve-sha256 REVIEWED_SHA256 --approved-by reviewer-name --receipt private-approval.json
```

The new `public-result/` contains only:

- `index.html`: escaped, script-free static evidence page;
- `card.svg`: deterministic plain factual layout, not generated brand artwork;
- `result.txt`: accessible text equivalent and limitations;
- `result.json`: the approved frozen record.

Do not copy `private-approval.json` or `private-preparation.json` into a public
directory. No upload takes place. Applying a hosting configuration or publishing
these files requires separate approval. A manually editable local receipt is
an accidental-disclosure interlock, not independent authentication.

An optional `approved_source_url` requires the additional
`--approve-source-link` flag. Preparation leaves this field null. A successful
local candidate export does not authorize its source link or source publication.
The public record never accepts source code, prompts, provider responses,
authentication fields, environment variables or run-directory paths.

## Record and outcome rules

The strict schema identifier is `libreevolve.public_result.v1`. Unexpected or
missing fields, duplicate JSON keys, non-finite numbers, invalid count types,
overlong text, unsafe links and Unicode display controls are rejected. Input
is bounded to 65,536 bytes. Text still requires human privacy review; the schema
cannot determine whether an operator embedded private meaning in an allowed
description.

Run status, selected source, candidate retention, validity, comparison and
usage remain separate. Modified workspace bytes do not inherit historical
retention; a legacy selection does not establish modern archive retention. A valid
candidate may survive an aborted run. A missing candidate is incomplete; it is
not a successful zero-bin solution. Synthetic fixtures carry a prominent label.

Bin reduction is calculated only for valid solutions on matching corpus ID,
corpus hash, split and case count, with a positive baseline. Empty, missing,
incompatible or inconsistent zero-bin data has no percentage. Negative
reductions are shown as regressions. Quality is not accuracy or speed.
Named finite checks do not prove universal correctness or optimality.

Unknown tokens and cost stay null and display as unknown. Recorded cost is not
provider billing or a spending guarantee. Public provenance hashes are included
only in the payload you explicitly approve; the private approval actor is not.

## Filesystem boundary and incomplete output

All output paths must be new and have existing parents. Traversal and symlink
or reparse-point paths are rejected. The receipt must be outside the public
destination. Existing files/directories are never overwritten, including empty
directories. The output directory and files start owner-only; hosting permission
changes belong to a separately reviewed deployment step.

Own the parent directory and prevent concurrent changes by other processes.
These guards are not containment against a malicious filesystem actor. An I/O
failure after creation can leave partial files: keep them local, inspect the
failure, and use new paths when retrying. Do not treat surviving files as a
successful export or invent an approval receipt.
