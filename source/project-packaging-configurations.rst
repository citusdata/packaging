Project Packaging Configurations
================================

For each project, a new branch is created in the packaging repository where packaging configuration files for the project are added.
The packaging configuration files include:

1. Pkgvars
2. Postgres-matrix.yml

Pkgvars
-------
Pkgvars is a property file that contains essential information about the package.
It is used by the packaging system to generate the package name, version, and other details.

Here is an example of a pkgvars file:

.. code-block:: ini

    pkgname=citus
    hubproj=citus
    pkgdesc='Citus (Open-Source)'
    pkglatest=11.3.0.citus-1
    nightlyref=main
    versioning=fancy

Parameters for the pkgvars file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. pkgname: Prefix of the package.
2. hubproj: Name of the repository in GitHub.
3. pkgdesc: Description of the package. It is for reference purposes and not used by the packaging system.
4. pkglatest: Latest version of the package. It is used by the packaging system to generate the package name and retrieve the release number from the GitHub repository.
5. nightlyref: Branch name of the nightly builds.
6. versioning: Versioning scheme. It can be either 'fancy' or 'simple'. If 'fancy', fancy version numbers are added to the package name. The default is 'simple'.

Postgres-matrix.yml
-------------------
The Postgres-matrix.yml file contains the Citus Postgres version matrix.
The packaging system utilizes this file to determine the appropriate Postgres versions for a given Citus version.

Here is an example of a postgres-matrix.yml file:

.. code-block:: yaml

    name: Postgres Version Matrix
    project_name: citus
    version_matrix:
      - 8.0:
          postgres_versions: [10, 11]
      - 9.0:
          postgres_versions: [11, 12]
      - 9.5:
          postgres_versions: [11, 12, 13]
      - 10.1:
          postgres_versions: [12, 13]
      - 10.2:
          postgres_versions: [12, 13, 14]
      - 11.0:
          postgres_versions: [13, 14]
      - 11.1:
          postgres_versions: [13, 14, 15]

In the packaging system, the version number is obtained from the pkgvars file, and the corresponding matrix entry is determined by comparing the version number with the entries in the matrix file.
The Postgres versions specified in the matrix entry are then used to generate individual packages.

For instance, if we want to create a package for Citus version 9.3.8, we will retrieve the matrix entry for version 9.0 and generate a package for each Postgres version listed in the matrix entry since 9.3.8 falls between 9.0 and 9.5.
