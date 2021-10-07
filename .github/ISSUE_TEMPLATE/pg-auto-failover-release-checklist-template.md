---
name: pg-auto-failover release checklist template
about: Please make sure to follow the checklist below along the release process.
title: Pg Auto Failover release checklist - [vX.Y.Z]
labels: release_checklist
assignees: gurkanindibay

---

## Several things to note here

These instructions assume you have `$VERSION`, `$PROJECT`, and `$REPO` environment variables set in your shell (e.g. `10.0.2`, `citus`, and `citus`). With those set, code from most steps can be copy-pasted.

**After this checklist, you're still not done: open a release checklist for Enterprise too!**

# Update OS Packages
## Debian and RedHat
- Change your directory to `packaging` repository directory & checkout `all-$PROJECT` branch.
- [ ] Run the pipeline using branch name as all-project https://github.com/citusdata/packaging/actions/workflows/update_package_properties.yml. Input tag name and if version is fancy, input the fancy version_no. Other parameters could be kept as is if you want
  - Then check the following (needed for both debian & redhat):
    - [ ] Updated `pkglatest` variable in the `pkgvars` file to `$VERSION.citus-1`
  - Then check the following (needed for debian):
    - [ ] A new entry (`$VERSION.citus-1`, `stable`) is added to the `debian/changelog` file
  - Then check the following (needed for redhat):
    - [ ] `$PROJECT.spec` file is updated:
      - [ ] `Version:` field
      - [ ] `Source0:` field
      - [ ] A new entry (`$VERSION.citus-1`) in the `%changelog` section
- [ ] Get changes reviewed; merge the PR
- [ ] Ensure Github Actions builds completed successfully and package count for each os is as below table and packages in postgres versions is compliant with `postgres-matrix.yml` in the `all-project` branch
