Citus Docker images
====================

General Structure
------------------
Docker images are part of the Citus release process. They are built and pushed after every release. Dockerfiles are stored in the `citusdata/docker <https://github.com/citusdata/docker>`_ repository. In each release, we change the below Dockerfiles to point to the new Citus release.
Citus Docker images are published in DockerHub `citusdata/citus <https://hub.docker.com/repository/docker/citusdata/citus/>`_ 

1. `Main Dockerfile <https://github.com/citusdata/docker/blob/master/Dockerfile>`_: Used to build the latest regular Citus image for the latest Postgres version.
2. `alpine Dockerfile <https://github.com/citusdata/docker/tree/master/alpine>`_: Used to build the latest regular Citus image for the latest Postgres version with the alpine base Docker image.
3. `postgres-xx` Dockerfiles (where `xx` represents the major Postgres versions) : Used to build the Citus images for the older Postgres versions. We normally support the last 3 major Postgres versions. For example, if the latest Postgres version is 15, we support 13, 14, and 15. Therefore, we have 2 Dockerfiles in total for supported Postgres major versions other than the latest one.

Build Process
------------------
The Dockerfiles are built and pushed to Docker Hub by GH Actions pipelines. There are four pipelines used for the Citus Docker image build and publish process:

1. `Update Citus versions <https://github.com/citusdata/docker/blob/master/.github/workflows/update_version.yml>`_: This pipeline updates the Citus versions in the Dockerfiles and pushes the changes to a newly created branch and creates a PR. It should be triggered manually after finishing the publishing of Citus packages to the packagecloud.

2. `Build and publish Citus Docker images on push <https://github.com/citusdata/docker/blob/master/.github/workflows/publish_docker_images_on_push.yml>`_: This pipeline is triggered on every branch push to the repository. It builds the Docker images on every occasion and pushes them to Docker Hub if the branch is master.

3. `Build and publish Citus Docker images on schedule <https://github.com/citusdata/docker/blob/master/.github/workflows/publish_docker_images_cron.yml>`_: This pipeline is triggered every day at 00:30 UTC and builds and publishes the Docker images for the main, alpine, and `postgres-xx` Docker images to Docker Hub.

4. `Build and publish Citus Docker images manually <https://github.com/citusdata/docker/blob/master/.github/workflows/publish_docker_images_on_manual.yml>`_: This pipeline is triggered manually and builds and publishes the Docker images. It is useful when we want to build and publish the Docker images without waiting for the scheduled pipeline to run.

New Postgres Version Support
-----------------------------
When a new Postgres version is released, we need to add support for the new Postgres version in the Dockerfiles. To add support for a new Postgres version:

1. Create a new branch from the master branch.
2. Create a new Dockerfile for the new Postgres version. For example, for Postgres 16, create `postgres-16/Dockerfile` by copying the `postgres-15/Dockerfile`.
3. Change the Postgres version in the new Dockerfile to the new Postgres version.
4. Test the new Dockerfile using the appropriate Docker build and run commands.
5. Add new Postgres version support to the scheduled pipeline.
6. If the tests are successful, create a pull request to merge the changes to the master branch.

Adding new Postgres version support to the tools scripts
---------------------------------------------------------
When a new Postgres version is released, we also need to add support for the new Postgres version in the tools scripts. Mainly, the `update_docker.py <https://github.com/citusdata/tools/blob/develop/packaging_automation/update_docker.py>`_ script needs to be updated to add support for the new Postgres version. This script is used in the pipelines.
