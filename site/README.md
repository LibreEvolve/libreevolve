# Static website build

Status: local implementation is available and independently checked; this is
not an approved public deployment.

See [deployment and rollback](DEPLOYMENT.md) for the separately gated activation
and withdrawal procedure.

## Design and stack

Visual thesis: a precise, quiet developer instrument with a full-width dark
identity plane, editorial type, generous space and one green accent.

Content plan: LibreEvolve and preview scope; evidence interpretation and the
approved-example boundary; change/evaluate/inspect/export workflow; canonical
setup; scope, roadmap and contribution. No fabricated outcome or screenshot.

Interaction thesis: a short identity entrance, focused link/CTA transitions and
native expandable navigation. Respect reduced motion; no scroll hijacking,
background animation, remote fonts or analytics. Core content works without JS.

The frontend skill guides composition and utility copy. The site now integrates
the five approved raster family PNGs in `assets/brand/`, using the exact
public-safe roles and hashes recorded in
[`brand/approved-family.md`](../brand/approved-family.md). The remaining
catalog artwork, derivative/export and evidence gates stay separately reviewed
and open. No authentic live example or public demo is implied, and no synthetic
success story substitutes for one.

No suitable static stack exists in the reviewed product tree. Use a small
Python build with hash-locked markdown-it-py and mdurl, separate from runtime
dependencies. Disable Markdown HTML and external resources. Source docs remain
authoritative: the build maps their links to static routes instead of copying
and rewriting quickstart commands into a second document.

## Local build contract

The default configuration uses the reserved placeholder origin
`https://example.invalid`, emits no canonical or organization structured data,
and sets noindex plus a disallow-all robots file. An actual owned deployment
origin and publication authorization are still required before an indexable
production build or deployment. Nothing in this directory deploys a site.

Build output must be a new directory. Keep generated output outside this
checkout; do not publish private source records, receipts or local test results.
The website renderer must never prepare candidates or import verification
workers. A separately approved frozen share record is the example input boundary.

## Install, test and serve locally

Run from the repository root with Python 3.12. Choose fresh environment and
output names; the example sibling directories must not contain unrelated work.
The website environment is separate from the product environment and installs
only the two hash-locked build dependencies.

Replace `/absolute/path/to/...` with actual absolute paths whose parent
directories exist. Record, output and receipt paths must not contain `..`;
the build rejects parent traversal rather than resolving it silently.

```bash
python3.12 -m venv ../site-env
../site-env/bin/python -m pip install --require-hashes --only-binary=:all: -r site/requirements.txt
../site-env/bin/python -m unittest discover -s site/tests -v
../site-env/bin/python site/build.py --output /absolute/path/to/new-site-preview
../site-env/bin/python -m http.server 8768 --bind 127.0.0.1 --directory /absolute/path/to/new-site-preview
```

On native Windows, use `py -3.12` and the environment's
`..\site-env\Scripts\python.exe` executable. These spellings are not native
Windows validation evidence. The reference route has been exercised in WSL.
Stop the local preview server with Ctrl+C when finished.

Open `http://127.0.0.1:8768/`. No deployment or external analytics is configured.
Use `--base-path /preview/` with a new output directory to build under a
subpath, then serve that output root and open `/preview/`. Navigation, styles,
scripts and included example links use the same base path.

## Include one explicitly reviewed frozen record

Candidate preparation is not a website-build step. Use the product's existing
[share workflow](../docs/share-export.md) to prepare and inspect a record in its
own environment. Review every field, including hashes and any source link.
Then use the exact inspection digest; the following value is a placeholder:

```bash
../site-env/bin/python site/build.py --output /absolute/path/to/new-site-with-example --example-record /absolute/path/to/reviewed-record.json --example-sha256 REVIEWED_SHA256 --approved-by reviewer-name --example-receipt /absolute/path/to/new-private-site-approval.json
```

The receipt is mandatory, new and outside the output directory. Never publish
it. An included source link also needs `--approve-source-link`. A receipt is a
local disclosure interlock, not authentication, proof of an experiment, or
publication authorization. Rendering performs no candidate execution or fetch.

The experiments route links to four read-only W06 files under
`examples/PUBLIC_ID/`. Synthetic records remain conspicuously labeled; local
checks are not relabeled as live-model evidence. JSON, text and SVG remain the
W06 outputs; HTML adds only site navigation and local noindex metadata.

The CLI writes required private input-approval receipts before building. A
receipt-write failure therefore creates no site output. A later build failure
can leave a partial directory and approval receipts; receipts do not certify
build completion. Keep such output local and retry with new paths after
inspection. No cleanup or overwrite is
automatic. Own the output parents and prevent concurrent filesystem changes;
these checks are not containment against a malicious filesystem actor.

To withdraw an example, omit it from a fresh build, verify the example route
is absent, and prepare a separately approved deployment/removal change. Do not
leave a stale viewer route or blindly delete a directory containing user data.

## Approved-origin release candidate

This mode prepares files only. It does not verify domain ownership, authenticate
an operator, upload files, or authorize deployment. Obtain the owner's approval
for the exact origin, base path and public example before using it. Keep the
configuration and receipts private, outside the generated output. The following
reserved-domain configuration is a test fixture, not an approved deployment:

```json
{
  "origin": "https://fixture.example.test",
  "base_path": "/preview/",
  "ownership_evidence": "PRIVATE reference to independently checked ownership",
  "authorization_reference": "PRIVATE reference to the owner's scoped approval",
  "public_example_sha256": null
}
```

For a real release, replace the fixture values with approved values. Hash the
exact configuration file bytes with `sha256sum` (Windows: `Get-FileHash -Algorithm
SHA256`). Record the owner approval separately; a matching digest proves byte
identity, not approval authenticity. Use a new output and receipt path:

```bash
../site-env/bin/python site/build.py --output /absolute/path/to/new-release-candidate --base-path /preview/ --publication-config /absolute/path/to/private-publication.json --publication-sha256 EXACT_FILE_SHA256 --publication-approved-by reviewer-name --publication-receipt /absolute/path/to/new-private-publication-receipt.json
```

The configured base path must match the build. Origins are normalized bare
HTTPS DNS origins without credentials, ports, paths, queries or fragments.
The release emits canonical and Open Graph text/URL metadata, organization JSON-LD,
a base-path sitemap and root robots file. No image metadata is invented while
approved artwork is unavailable. No analytics or remote resources are introduced.

An included example additionally requires its normal example flags and separate
receipt, plus its exact payload digest in `public_example_sha256`. Set that field
to `null` when no example is included. This binds the public disclosure selection;
the builder still cannot authenticate the approval. Example viewers stay noindex
and are excluded from the sitemap. Robots directives are not access controls:
never deploy private or draft evidence, even if marked noindex.

The manifest identifies `release_candidate` and the configuration digest, without
private operator/evidence references. It does not assert activation. Review the
entire artifact before a separately authorized release switch, preserving the
previous release for rollback. For subpath hosting, the host must explicitly
approve handling of root `robots.txt`; do not overwrite another site's policy.
Verify actual HTTPS routes, canonical URLs and removals after any authorized
activation or rollback. No production activation has been performed here.
