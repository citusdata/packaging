Project Packaging Configurations
=================================

For each project, we open a new branch in the packaging repository.
In these branches, we add the packaging configuration files for the project. The packaging configuration files are:
1. Pkgvars
2. Postgres-matrix.yml

Pkgvars
-------
Pkgvars is a property file that contains the basic information about the package. It is used by the packaging system to generate the package name, version, etc.

Below is a sample pkgvars file:

```
pkgname=citus
hubproj=citus
pkgdesc='Citus (Open-Source)'
pkglatest=11.3.0.citus-1
nightlyref=main
versioning=fancy

```

Parameters for the pkgvars file
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
1. pkgname: prefix of the package
2. hubproj: name of the repository in the GitHub
3. pkgdesc: description of the package. It is just for reference. It is not used by the packaging system
4. pkglatest: latest version of the package. It is used by the packaging system to generate the package name and get the release number
from the GitHub repository
5. nightlyref: branch name of the nightly builds
6. versioning: versioning scheme. It can be either `fancy` or `simple`. If it is `fancy`,fancy version numbers are added to the package name.
By default, it is `simple`.

Postgres-matrix.yml
-------
Citus Postgres version matrix. Packaging system decides which postgres versions for the Citus version by referencing this file

Below is a sample postgres-matrix.yml file:

```
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
      postgres_versions: [ 13, 14, 15 ]

```

In packaging system, version number is taken from pkgvars file and correct matrix entry is being found from this file by comparing the version number with the matrix entries.
Then, the postgres versions are taken from the matrix entry and one package is generated for each postgres version.

For example, if we want to create a package for 9.3.8 version of Citus, we will take the matrix entry for 9.0 and
create a package for each postgres version in the matrix entry since 9.3.8 is between 9.0 and 9.5.

