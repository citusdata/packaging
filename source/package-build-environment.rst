Packaging Build Environment Management
======================================

Introduction to Packaging Environments
--------------------------------------

In our packaging process, we utilize Docker images for each OS/release/PostgreSQL version combination. Docker images offer a reliable and consistent environment for packaging software applications. They provide several advantages for the packaging process:

1. **Isolation**: Docker containers encapsulate applications and their dependencies, ensuring isolation from the underlying host system. This isolation helps prevent conflicts between different software components and provides a clean and reproducible environment for packaging.

2. **Reproducibility**: Docker environments enable the creation of reproducible packaging environments. By defining the dependencies and configurations within a Docker image, it becomes easier to recreate the same environment across different systems, ensuring consistent packaging results.

3. **Portability**: Docker environments are portable and can be easily shared across different systems. This portability ensures that the same packaging results can be achieved across different systems, eliminating environment-related issues.

4. **Scalability**: Docker environments can be easily scaled up or down to meet the packaging requirements. This scalability ensures that the packaging process can be efficiently adjusted to handle different workload sizes.

5. **Other Benefits**: Docker environments provide a secure, reliable, consistent, flexible, efficient, simple, and maintainable packaging environment. Docker isolates the packaging process from the underlying host system, ensuring a controlled and stable environment.

Docker Images for Various Package Types
---------------------------------------

We utilize Docker images for each OS/release/PostgreSQL version combination to create a reproducible and consistent packaging environment.

For Debian-based packages, we can use the same Docker image for all PostgreSQL versions.

For example, the Debian/10 Docker image can be used for both PostgreSQL 13 and PostgreSQL 14 packages.

However, for RPM-based packages, we need a dedicated Docker image for each PostgreSQL version.

For instance, we require a Docker image for CentOS/7 with PostgreSQL 13 and another Docker image for CentOS/7 with PostgreSQL 14 packages.

Here are the supported OS/release pairs:

1. CentOS
    - centos/7

2. Oracle Linux
    - oraclelinux/7
    - oraclelinux/8

3. AlmaLinux
    - almalinux/9

4. Debian
    - debian/buster
    - debian/bullseye
    - debian/bookworm

5. Ubuntu
    - ubuntu/bionic
    - ubuntu/focal
    - ubuntu/jammy
    - ubuntu/kinetic

6. PGXN

Based on these OS/release pairs, the Docker images for each OS/release/PostgreSQL version combination are as follows:

1. CentOS
    - centos/7 PostgreSQL 13
    - centos/7 PostgreSQL 14
    - centos/7 PostgreSQL 15
    - centos/7 PostgreSQL 16 (planned)
2. Oracle Linux
    - oraclelinux/7 PostgreSQL 13
    - oraclelinux/7 PostgreSQL 14
    - oraclelinux/7 PostgreSQL 15
    - oraclelinux/7 PostgreSQL 16 (planned)
    - oraclelinux/8 PostgreSQL 13
    - oraclelinux/8 PostgreSQL 14
    - oraclelinux/8 PostgreSQL 15
    - oraclelinux/8 PostgreSQL 16 (planned)
3. AlmaLinux
    - almalinux/9 PostgreSQL 13
    - almalinux/9 PostgreSQL 14
    - almalinux/9 PostgreSQL 15
    - almalinux/9 PostgreSQL 16 (planned)
4. Debian
    - debian/buster (all PostgreSQL versions)
    - debian/bullseye (all PostgreSQL versions)
    - debian/bookworm (all PostgreSQL versions)
5. Ubuntu
    - ubuntu/bionic (all PostgreSQL versions)
    - ubuntu/focal (all PostgreSQL versions)
    - ubuntu/jammy (all PostgreSQL versions)
    - ubuntu/kinetic (all PostgreSQL versions)
6. PGXN

Developing and Maintaining Docker Images
-----------------------------------------

The Dockerfiles used to build Docker images are located in the "develop" branch of the packaging repository. We follow a template structure to auto-generate Docker files for each OS/release/PostgreSQL version combination. The templates used are:

1. `Dockerfile-deb.tmpl <https://github.com/citusdata/packaging/blob/develop/templates/Dockerfile-deb.tmpl>`_: This template generates Docker files for Debian-based packages.
2. `Dockerfile-rpm.tmpl <https://github.com/citusdata/packaging/blob/develop/templates/Dockerfile-rpm.tmpl>`_: This template generates Docker files for RPM-based packages.
3. `Dockerfile-pgxn.tmpl <https://github.com/citusdata/packaging/blob/develop/templates/Dockerfile-pgxn.tmpl>`_: This template generates Docker files for PGXN-based packages.

After making changes to the template files, the `update_dockerfiles.sh <https://github.com/citusdata/packaging/blob/develop/update-dockerfiles.sh>`_ script needs to be run to generate the Docker files for each OS/release/PostgreSQL version combination.

Once the changes are committed and pushed, the GitHub Actions workflow will build the Docker images using the generated Docker files.

After confirming that all Docker images are successfully built, the changes can be merged into the master branch.

When the changes are merged into the master branch, the GitHub Actions workflow will push the Docker images to the `citus/packaging <https://hub.docker.com/r/citus/packaging>`_ Docker Hub repository.

If you want to publish test images from `citus/packaging-test <https://hub.docker.com/r/citus/packaging-test>`_, you can use the `test pipeline <https://github.com/citusdata/packaging/blob/develop/.github/workflows/build-package-test.yml>`_. To use the test pipeline, change the current branch to your branch name. The test pipeline will then push the Docker images to the `citus/packaging-test <https://hub.docker.com/r/citus/packaging-test>`_ Docker Hub repository.

