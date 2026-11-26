---
name: Citus release checklist template
about: Follow the automated release flow for a Citus tag.
title: Citus release checklist - [vX.Y.Z]
labels: release checklist

---

## 1. Kick off the release

Run the [Citus Release workflow](https://github.com/citusdata/packaging/actions/workflows/citus-release.yml) on `develop` with:
- `citus_tag` (e.g. `v14.3.0` or `v15.0.0_beta1`)
- `changelog_name` and `changelog_email`
- `changelog_entry` (optional) and `force_docker` (only if forcing a Docker PR off the active line)

The workflow validates the tag, opens/updates the `all-citus` PR (and `pgxn-citus` PR when stable and semver-newer), and creates a `Release <tag>` tracking issue.

## 2. Human merge gates

- [ ] Review and merge the `all-citus` PR after build + pre-GA local install smoke checks pass
- [ ] Verify packagecloud upload and post-GA `test-package-installation` pass on `all-citus`
- [ ] Review and merge the `pgxn-citus` PR (if opened) and confirm PGXN publish succeeds
- [ ] Review and merge the auto-dispatched `citusdata/docker` PR (if opened) and confirm Docker tag publishing
- [ ] (Optional) File a PGDG RPM update request on [Redmine](https://redmine.postgresql.org/projects/pgrpms/issues/new)
