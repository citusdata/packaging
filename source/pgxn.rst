Citus PGXN Extension Builds
===========================

PGXN Build Infrastructure
----------------------------
In the packaging system, we have scripts and images to build PGXN extensions.
In the package build environment, we have Docker images, specifically Dockerfiles, to build pgxn extensions.

The `Docker image <https://github.com/citusdata/packaging/blob/develop/dockerfiles/pgxn-all/Dockerfile>`_ serves as the base image for all pgxn extensions. It contains all the dependencies required for building pgxn extensions.
Within this docker image, there is a script called `fetch_and_build_pgxn <https://github.com/citusdata/packaging/blob/develop/scripts/fetch_and_build_pgxn>`_ which is used to build pgxn extensions.

Citus PGXN Configuration
------------------------

For each project package configuration, we maintain a branch named `pgxn-citus <https://github.com/citusdata/packaging/tree/pgxn-citus>`_ specifically for building the pgxn extension for Citus. In this branch, we have three configuration files used for building the packages:

1. `META.json <https://pgxn.org/spec/>`_

2. pkgvars

3. postgres-matrix.yml

The usage of pkgvars and postgres-matrix.yml is similar to other project builds.

.. _Pgxn Build Process:
