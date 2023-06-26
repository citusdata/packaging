Citus PGXN Extension Builds
===========================

PGXN Build Infrastructure
----------------------------
In packaging system, we have scripts and images to build PGXN extensions.
In package build environment, we have Docker images , so Dockerfiles, to build pgxn extensions.
`Docker image <https://github.com/citusdata/packaging/blob/develop/dockerfiles/pgxn-all/Dockerfile>`_
is the base image for all pgxn extensions. It has all the dependencies to build pgxn extensions.
In this docker image, there is a script called `fetch_and_build_pgxn <https://github.com/citusdata/packaging/blob/develop/scripts/fetch_and_build_pgxn>`_
which is used to build pgxn extensions.

Citus PGXN COnfiguration
------------------------

As each project package configuration, we have a branch named `pgxn-citus <https://github.com/citusdata/packaging/tree/pgxn-citus>`_
which is used to build pgxn extension for citus. In this branch, we have three configuration files used to build the packages
1. `META.json <https://pgxn.org/spec/`>_
2. pkgvars
3. postgres-matrix.yml

Pkgvars and postgres-matrix.yml has the same usage as in other project builds.

Building PGXN Extension for the new release
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
When we build the pgxn extenson for citus, we need to go through the following steps.
1. Execute the pipeline `Update Version on PGXN Config Files <https://github.com/citusdata/packaging/actions/workflows/update-pgxn-version.yml>`_
   to update the version in the pgxn configuration files. This pipeline will create a PR with the updated version.
2. Check for the minimum postgres version. If it is different from the one that citus has, it should be changed to the one that citus has.
3. Check for the tests and if they all pass, notify the PR reviewer to review the PR.
4. Once the PR is reviewed, merge the PR and make sure that the `Citus PGXN <https://pgxn.org/dist/citus/>`_ is updated with the new version.




