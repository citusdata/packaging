.. _debian-packages:

Debian Packages
===============

Introduction to Debian packaging
--------------------------------

Debian packaging provides a standardized way to create software packages for Debian-based operating systems. It ensures easy installation, upgrade, and removal of software components. The packaging format used in Debian is known as the Debian package format or ``.deb``.

Debian-specific tools and conventions
-------------------------------------

Debian packaging relies on a set of tools and conventions to streamline the packaging process. Familiarize yourself with the following:

- **dpkg**: The Debian package manager (``dpkg``) is the core tool for installing, querying, and managing Debian packages. It operates at a lower level than higher-level package management tools like ``apt`` or ``apt-get``.

- **Debian control file**: The ``debian/control`` file is a metadata file that provides information about the package, its dependencies, and other package-related details. It includes fields such as package name, version, maintainer, description, dependencies, and more. Maintaining an accurate and up-to-date control file is essential for proper package management.

- **Debian changelog**: The ``debian/changelog`` file maintains a record of changes made to the package across different versions. It includes information about the package version, the person responsible for the change, the change description, and other relevant details. The changelog helps users and maintainers track the history of the package and understand the modifications introduced in each release.

- **Debian rules file**: The ``debian/rules`` file is a makefile-like script that defines the build process and other package-specific tasks. It specifies how to compile the source code, configure the package, and install the files in the correct locations. The rules file allows for customization and automation of the packaging process.

Other important Debian-specific tools and files include ``debuild``, ``lintian``, and ``pbuilder``, which aid in building, linting, and testing packages respectively.

Additional Debian Files
-----------------------

In addition to the core Debian packaging files, the packaging process may involve other files with specific purposes. Here are some of the additional Debian files commonly used:

- **Source/format**: This file specifies the format version of the Debian source package.

- **Source/lintian-overrides**: This file is used to override specific lintian warnings or errors generated during the package build process.

- **Tests/control**: This file contains information about the tests to be run on the package.

- **Tests/installcheck**: This file specifies commands or scripts to be executed after the package is installed.

- **Upstream/signing-key.asc**: This file contains the ASCII-armored representation of the upstream signing key used to verify the authenticity and integrity of the package.

- **Changelog**: The ``debian/changelog`` file maintains a record of changes made to the package.

- **Compat**: The ``debian/compat`` file specifies the compatibility level of the package's packaging format.

- **Control.in**: The ``debian/control.in`` file is a template file used to generate the ``debian/control`` file.

- **Copyright**: The ``debian/copyright`` file provides information about the copyright holders and licensing terms.

- **Docs**: The ``debian/docs`` file lists the additional documentation files included with the package.

- **NOTICE**: The ``debian/NOTICE`` file contains any legally required notices or attributions.

- **Pgversion**: The ``debian/pgversion`` file specifies the PostgreSQL version for which the package is intended.

- **Rules**: The ``debian/rules`` file is a makefile-like script that defines the build process.

For more information about Debian packaging, see the `Debian New Maintainers' Guide <https://www.debian.org/doc/manuals/maint-guide/>`_.
