Package Repositories
=====================

Baked packages are stored in various repositories.  The repositories are:

* `PackageCloud <https://www.packagecloud.io/citusdata>`_: Stores deb and rpm packages. Community users and Marlin uses this repository. This is the main repo for all users
* PGDG: Stores only latest Citus rpm packages. You can not find older versions here. We do not manage the packages here directly. We open a ticket with PGDG to create a new package.
* `PGXN <https://pgxn.org/dist/citus/>`_: The PostgreSQL Extension Network (PGXN) is a community-driven effort aimed at providing a centralized platform for distributing and sharing extensions for the PostgreSQL database management system. We use this repository to store the citus extension.
* `Docker Hub <https://hub.docker.com/repository/docker/citusdata/citus>`_: Stores docker images. We use this repository to store the docker images for citus.