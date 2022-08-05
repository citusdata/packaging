---
name: pg-auto-failover release checklist template
about: Please make sure to follow the checklist below along the release process.
title: Pg Auto Failover release checklist - [vX.Y.Z]
labels: release_checklist
assignees: gurkanindibay

---

# Update OS Packages
## Debian and RedHat
- Change your directory to `packaging` repository directory & checkout `all-pgautofailover` branch.
- [ ] Run the pipeline using branch name as all-pgautofailover [update_package_properties workflow](https://github.com/citusdata/packaging/actions/workflows/update_package_properties.yml). Input tag name and if version is fancy, input the fancy version_no. Other parameters could be kept as is if you want
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
