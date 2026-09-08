# Static site deployment and rollback

No hosting target or deployment is selected by this guide. A successful local
build is not a live release. Use the [build instructions](README.md) to prepare
a fresh artifact; activation requires separate owner approval.

## Before activation

Record privately the exact source commit, artifact manifest digest, approved
HTTPS origin/base path, hosting account, target directory, responsible operator,
activation window and rollback target. Independently check ownership through the
authorized hosting or domain account. A resolving DNS name or historical mention
does not establish permission. Keep the approval and evidence references private.

Approve public disclosure of every included example and source link. Noindex and
robots directives do not protect private information. Review the complete output
inventory, not only the linked pages. Exclude input records, receipts, test logs,
environments and coordination files from the release upload.

Build from the accepted source using the locked dependencies and approved-origin
configuration. Verify manifest hashes against all content files, and reject
unexpected files or partial outputs. Do not edit generated pages after approval;
rebuild and review the new artifact instead.

Run `../site-env/bin/python site/verify.py /absolute/path/to/artifact` from the
repository root. This checks the complete file inventory and content hashes
against the supplied manifest; it does not authenticate the manifest or approve
the content. Compare the manifest digest to the independently accepted release
record as a separate step. Use an operator-owned directory without concurrent
filesystem changes; this is not containment against a malicious filesystem.

Compute that digest with `sha256sum /absolute/path/to/artifact/build-manifest.json`
or PowerShell `Get-FileHash -Algorithm SHA256 C:\absolute\path\to\artifact\build-manifest.json`.
Compare the resulting hexadecimal digest to the independently accepted value,
not to a value taken from the same untrusted artifact delivery.

Test all routes, assets, downloads and fragments at the actual base path. Check
mobile/tablet/desktop, both themes, keyboard scrolling, browser zoom, reduced
motion and JavaScript-disabled access. Confirm canonical/OG URLs, organization
metadata and sitemap reflect the approved identity. For subpath hosting, agree
how root `robots.txt` is managed without overwriting another site's policy.

## Activate only the approved target

Inspect and preserve the active release and routing configuration. Upload into a
new release directory. Use the host's approved reversible release switch; do not
overwrite unknown files or change DNS, accounts or unrelated document roots.

After activation, check the actual public HTTPS URL: redirects, clean routes,
assets, example downloads, canonical metadata, sitemap and robots. Verify served
content against the accepted artifact and confirm private receipts are absent.
Record the observed release separately from build/test results. Do not report a
release as live on the basis of an upload command alone.

## Rollback or withdraw an example

If privacy, routing or content checks fail, restore the preserved release using
the pre-approved rollback action. Verify the live pages again. Preserve failure
evidence privately and do not delete user data as part of troubleshooting.

For withdrawal, build without the record and verify its route and downloads are
absent from the new artifact. The approved removal must also cover old served
release paths and relevant host/CDN caches, not just links in the new navigation.
Check the formerly public URLs after activation. Retain or remove old releases
only under the owner's explicit retention instructions.

## Handoff evidence

Keep exact source/artifact identities, approvals, local test results, live checks
and rollback observations as separate records. State whether the result is local,
in a PR, merged, activated, or withdrawn. Pending origin, artwork, experiment or
deployment approvals remain open gates; this guide does not grant them.
