---
name: citus-enterprise release checklist template
about: Please make sure to follow the checklist below along the release process.
title: Citus Enterprise release checklist - [vX.Y.Z]
labels: release_checklist
assignees: gurkanindibay

---

# Update OS Packages
## Debian and RedHat
- Change your directory to `packaging` repository directory & checkout `all-enterprise` branch.
- [ ] Run [this pipeline](https://github.com/citusdata/packaging/actions/workflows/update_package_properties.yml) using branch name as `all-enterprise`. Input tag name and if version is fancy, input the fancy version number. Other parameters could be kept as is if you want.
  - Then check the following (needed for both debian & redhat):
    - [ ] Updated `pkglatest` variable in the `pkgvars` file to `$VERSION.citus-1`
  - Then check the following (needed for debian):
    - [ ] A new entry (`$VERSION.citus-1`, `stable`) is added to the `debian/changelog` file
  - Then check the following (needed for redhat):
    - [ ] `citus.spec` file is updated:
      - [ ] `Version:` field
      - [ ] `Source0:` field
      - [ ] A new entry (`$VERSION.citus-1`) in the `%changelog` section
- [ ] Get changes reviewed; merge the PR
- [ ] Ensure Github Actions builds completed successfully and package count for each os is as below table and packages in postgres versions is compliant with `postgres-matrix.yml` in the `all-project` branch

https://github.com/citusdata/tools/blob/be12af3b8f435d17a52e607c666f6b15379f5970/packaging_automation/tests/test_citus_package.py#L21-L33

## Microsoft Packages

- [ ] Add vso (Visual Studio Online) remote to your local git checkout of the github packaging repo (only needed once):
     `git remote add vso msdata@vs-ssh.visualstudio.com:v3/msdata/Database%20Systems/citus-packaging`
- [ ] To trigger a test build on Azure DevOps:
`git checkout all-enterprise`
`git pull # from normal github origin`
`git push vso # update Azure DevOps mirror`
- [ ] Open [ADO pipeline page](https://msdata.visualstudio.com/Database%20Systems/_build?definitionId=10018&_a=summary)
- [ ] Wait for build to succeed. If build does not success, go [here](https://msdata.visualstudio.com/Database%20Systems/_apps/hub/ms.vss-ciworkflow.build-ci-hub?_a=edit-build-definition&id=10018)
Maybe you need to update some parameters there (like the tools repo version). Then save it without queuing and then “Run pipeline” again via the first link.
- [ ] Check that it created the right packages by looking at the logs and artifacts (the button with the box/drawer icon and text “8 published”).
  - [ ] Click there, and see 7 items in signed packages
         centos 6/7/8
         debian buster/stretch
         ubuntu bionic/xenial
  - [ ] Check logs for each of 7 builds, by clicking `View raw log`
- [ ] Go back to the overview: https://msdata.visualstudio.com/Database%20Systems/_build?definitionId=10018&_a=summary
- [ ] Click “Run pipeline”
- [ ] Click “Variables”
- [ ] Change `PUBLISH_TO_PACKAGE_REPO` to “true”
- [ ] Go back after doing so and click "Run”
- [ ] Wait until completed.
- [ ] Check if packages are successfully published using below links:
  - [ ] 6 new items for the version for Ubuntu (xenial , bionic and focal): [here](https://packages.microsoft.com/repos/citus-ubuntu/pool/main/c/citus-enterprise/)
  - [ ] 4 new items for the version for Debian (buster and stretch): [here](https://packages.microsoft.com/repos/citus-debian/pool/main/c/citus-enterprise/) ( for release >9.4 and < 9.5,  4 package is expected. Since 9.5 6 package is expected)
  - [ ] 2 new items for the version for CentOS7/RHEL7: [here](https://packages.microsoft.com/yumrepos/citus-centos7/)
  - [ ] 2 new items for the version for CentOS8/RHEL8: [here](https://packages.microsoft.com/yumrepos/citus-centos8/)
