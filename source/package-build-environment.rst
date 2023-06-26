III. Packaging Build Environment Management
---------------------------------

A. Introduction to Packaging environments
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Mainly, we are using docker images for each OS/release/postgres version pair. We are using docker images to create a reproducible and consistent packaging environment. Docker images provide a reliable and consistent way to package software applications. They offer several advantages for packaging processes:
1. Isolation: Docker containers encapsulate applications and their dependencies, ensuring isolation from the underlying host system. This isolation helps prevent conflicts between different software components and provides a clean and reproducible environment for packaging.
2. Reproducibility: Docker environments enable the creation of reproducible packaging environments. By defining the dependencies and configurations within a Docker image, it becomes easier to recreate the same environment across different systems, ensuring consistent packaging results.
3. Portability: Docker environments are portable and can be easily shared across different systems. This portability ensures that the same packaging results can be achieved across different systems, eliminating environment-related issues.
4. Scalability: Docker environments can be easily scaled up or down to meet the packaging requirements. This scalability ensures that the packaging process can be easily scaled up or down to meet the packaging requirements.
5. Other: Docker environments provide a secure,reliable,consistent,flexible,efficient,simple and maintainable  packaging environment. Docker environments provide this by isolating the packaging process from the underlying host system.

B. Docker images for various package types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We are using docker images for each OS/release/postgres version pair. We are using docker images to create a reproducible and consistent packaging environment.
For debian based packages, we can use the same docker image for all postgres versions. For example, we can use the same docker image for debian/10 postgres 13 and debian/10 postgres 14 packages.
For rpm based packages, we need a dedicated docker image for each postgres version. For example, we need a docker image for centos/7 postgres 13 and centos/7 postgres 14 packages.

Below is our supported os/release pair

1. Centos
    1. centos/7
2. Oracle Linux
    1. oraclelinux/7
    2. oraclelinux/8
3. AlmaLinux
    1. almalinux/9
4. Debian
    1. debian/buster
    2. debian/bullseye
    3. debian/bookworm
5. Ubuntu
    1. ubuntu/bionic
    2. ubuntu/focal
    3. ubuntu/jammy
    4. ubuntu/kinetic
6. pgxn

Below is our supported postgres version
1. 13
2. 14
3. 15
4. 16 (planned)

Therefore, docker images for each OS/release/postgres version pair are as follows:

1. Centos
    1. centos/7 postgres 13
    2. centos/7 postgres 14
    3. centos/7 postgres 15
    4. centos/7 postgres 16 (planned)
2. Oracle Linux
    1. oraclelinux/7 postgres 13
    2. oraclelinux/7 postgres 14
    3. oraclelinux/7 postgres 15
    4. oraclelinux/7 postgres 16 (planned)
    5. oraclelinux/8 postgres 13
    6. oraclelinux/8 postgres 14
    7. oraclelinux/8 postgres 15
    8. oraclelinux/8 postgres 16 (planned)
3. AlmaLinux
    1. almalinux/9 postgres 13
    2. almalinux/9 postgres 14
    3. almalinux/9 postgres 15
    4. almalinux/9 postgres 16 (planned)
4. Debian
    1. debian/buster all postgres versions
    2. debian/bullseye all postgres versions
    3. debian/bookworm all postgres versions
5. Ubuntu
    1. ubuntu/bionic all postgres versions
    2. ubuntu/focal all postgres versions
    3. ubuntu/jammy all postgres versions
    4. ubuntu/kinetic all postgres versions
6. Pgxn

C. Developing and Maintaining Docker Images
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Dockerfiles, which are used to build docker images, are located in the develop branch of packaging repository.
We have a template structure to auto-generate the docker files for each OS/release/postgres version pair. The template structure is as follows:

1. `Dockerfile-deb.tmpl <https://github.com/citusdata/packaging/blob/develop/templates/Dockerfile-deb.tmpl>`_: This template is used to generate docker files for debian based docker files.
2. `Dockerfile-rpm.tmpl <https://github.com/citusdata/packaging/blob/develop/templates/Dockerfile-rpm.tmpl>`_ : This template is used to generate docker files for rpm based docker files.
3. `Dockerfile-pgxn.tmpl <https://github.com/citusdata/packaging/blob/develop/templates/Dockerfile-pgxn.tmpl>`_ : This template is used to generate docker files for pgxn based docker files.

After changing the template files, we need to run the `update_dockerfiles.sh <https://github.com/citusdata/packaging/blob/develop/update-dockerfiles.sh>`_ script to generate the docker files for each OS/release/postgres version pair.
After commit and push the changes, GH actions will build the docker images using the generated docker files. After seeing all the docker images are built successfully, we can merge the changes to the master branch.
When we merge the changes to the master branch, GH actions will push the docker images to the `citus/packaging <https://hub.docker.com/r/citus/packaging>`_ docker hub repository.

If you want to publish test images from `citus/packaging-test <https://hub.docker.com/r/citus/packaging-test>`_, you can use the `test pipeline <https://github.com/citusdata/packaging/blob/develop/.github/workflows/build-package-test.yml>`_.
To use the test pipeline, you need to change the current branch into your branch name. In this case, the test pipeline will push the docker images to the `citus/packaging-test <https://hub.docker.com/r/citus/packaging-test>`_ docker hub repository.



