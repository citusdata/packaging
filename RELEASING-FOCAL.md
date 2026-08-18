# Releasing Citus for Ubuntu focal (20.04) — stop-gap runbook

This branch (`citus-focal-12.1.x`) is a **temporary stop-gap** that publishes Citus
`.deb` packages for **Ubuntu focal (20.04)** only. focal was dropped from the standard
distribution list, so this branch keeps focal alive for the `12.1.x` line until it is
formally retired.

It is intentionally **decoupled** from the normal `update_package_properties` flow used by
the all-citus branches: the version metadata on this branch is bumped **manually** for
each release (see below).

## What this branch publishes

- **Platform:** `ubuntu/focal` only.
- **PostgreSQL:** **PG14, PG15 and PG16** — the full `12.1` matrix from
  `postgres-matrix.yml`. focal has no entry in `pg_exclude.yml`, so nothing is dropped.
- **Target:** packagecloud repo **`citusdata/community`**, focal distro id **210**.
- **Builder image:** a fixed local image `citus/packaging:ubuntu-focal-all` built from
  `dockerfiles/ubuntu-focal-all/Dockerfile` (step 6 of the workflow), which pins the
  PostgreSQL apt **archive** so focal keeps building after it left the live apt suites.

## Workflow: `.github/workflows/build-citus-focal.yml`

Two ways it runs:

| Trigger | Behaviour |
|---|---|
| **push** to any `citus-focal**` branch | build **+ validate only** — never publishes |
| **workflow_dispatch** with `publish=false` (default) | dry-run: build + validate, no publish |
| **workflow_dispatch** with `publish=true` | build + validate **+ publish** to packagecloud |

The publish step is guarded by
`if: github.event_name == 'workflow_dispatch' && inputs.publish`, so a plain push can
never publish.

## How the version is resolved

The focal `.deb` build does **not** take the tag as an input. It reads the version from
repo metadata on this branch, then fetches and **GPG-verifies** the matching `v<version>`
tag from `citusdata/citus`:

- **`pkgvars`** → `pkglatest=<version>.citus-1` — **authoritative** for the deb build.
- **`debian/changelog`** → the **top** stanza's version stamps the package.
- **`citus.spec`** → RPM-only (`Version:` / `Source0:`). **Not** used by the focal deb
  build; bump only to keep the file consistent.

## Releasing a new version (e.g. 12.1.14)

### Prerequisite (release owner)

A signed, GPG-**verified** annotated tag `v12.1.14` must be pushed on `citusdata/citus`.
The focal build fails tag verification otherwise.

### Step A — bump version metadata on this branch

1. `pkgvars` — set `pkglatest=12.1.14.citus-1`.
2. `debian/changelog` — prepend a new **top** stanza:

   ```
   citus (12.1.14.citus-1) stable; urgency=low

     * Official 12.1.14 release of Citus

    -- Your Name <you@example.com>  <RFC-2822 date>
   ```

   Get the date with `date -R` (WSL/Linux).
3. `citus.spec` (optional, consistency only) — `Version: 12.1.14.citus` and
   `Source0: https://github.com/citusdata/citus/archive/v12.1.14.tar.gz`.

### Step B — dry-run (build + validate)

```sh
git add pkgvars debian/changelog citus.spec
git commit -m "Focal: bump to 12.1.14"
git push origin citus-focal-12.1.x        # push event -> build + validate dry-run
```

Watch it and confirm **Build packages** (the `--output_validation` gate) is green:

```sh
gh run list --repo citusdata/packaging --branch citus-focal-12.1.x --limit 1
gh run view <run-id> --repo citusdata/packaging --json status,conclusion,jobs
```

### Step C — publish

```sh
gh workflow run build-citus-focal.yml \
  --repo citusdata/packaging \
  --ref citus-focal-12.1.x \
  -f publish=true
```

Monitor the dispatched run and confirm **Publish packages = success** (not skipped).
The focal `.deb`s then land on `citusdata/community`, focal distro **210**.

## Expected, benign validation warning

`--output_validation` stays **on** for focal. focal's archived `postgresql-common` does not
populate the `${postgresql:Breaks}` substitution referenced by `debian/control.in`, which
produces a harmless empty `Breaks:` field. That specific warning is whitelisted in
`packaging_ignore.yml`, so validation still passes while every other warning remains fatal.
No action is needed for it each release.

## Retiring the stop-gap

When focal support ends for the `12.1.x` line, simply stop bumping this branch (and
optionally delete it). Nothing else in the repo depends on it.
