Citus Docker images
====================

General Structure
------------------

Docker images are part of the Citus release process. They are built and pushed after every release.
Dockerfiles are stored in `citusdata/docker <https://github.com/citusdata/docker>`_ repository.
In each release, we change the below Dockerfiles to point to the new Citus release.
1. `Main Dockerfile <https://github.com/citusdata/docker/blob/master/Dockerfile>`_
which is used to build the latest regular Citus image for the latest Postgres version.
2. `alpine Dockerfile <https://github.com/citusdata/docker/tree/master/alpine>`_
which is used to build the latest regular Citus image for the latest Postgres version
with the alpine base docker image.
3. `postgres-xx Dockerfiles which are used to build the Citus images for the older Postgres versions.
Normally, we support the last 3 major Postgres versions. For example, if the latest Postgres version is 15,
we support 13, 14, and 15. Therefore, we have 2 Dockerfiles in total for supported postgres major versions other than the latest one.
For example, if we support 13, 14, and 15, we need to have postgres-13/Dockerfile
and postgres-14/Dockerfile Dockerfiles in our repository.

Build Process
------------------

The Dockerfiles are built and pushed to Docker Hub by GH Actions pipelines.
There are two pipelines to be used for Citus docker image build and publish process.
1. `Update Citus versions <https://github.com/citusdata/docker/blob/master/.github/workflows/update_version.yml>`_:
This pipeline should be triggered manually after finishing publishing of Citus packages to the packagecloud,
since the pipeline uses the Citus packages from the packagecloud to build the docker images.
This pipeline updates the Citus versions in the Dockerfiles and pushes the changes
to a newly created branch and creates a PR.
2. `Build and publish Citus docker images on push <https://github.com/citusdata/docker/blob/master/.github/workflows/publish_docker_images_on_push.yml>`_:
This pipeline is triggered on every branch push to repository.
This pipeline builds the docker images on every occasion and pushes them to Docker Hub if the branch is master.
Therefore, this pipeline is used to validate the build in the branches other than master and to publish the images to Docker Hub in the master branch.
3. `Build and publish Citus docker images on schedule <https://github.com/citusdata/docker/blob/master/.github/workflows/publish_docker_images_cron.yml>`_:
This pipeline is triggered every day at 00:30 UTC and build and publish the docker images for
main, alpine and postgres-xx docker images to Docker Hub.
4. `Build and publish Citus docker images manually <https://github.com/citusdata/docker/blob/master/.github/workflows/publish_docker_images_on_manual.yml>`_:
This pipeline is triggered manually and build and publish the docker images. It is useful when we want to build and publish the docker images
without waiting for the scheduled pipeline to run.

New Postgres Version Support
------------------

When a new Postgres version is released, we need to add the new Dockerfile for the new Postgres version.
Steps to add a new Postgres version support:
1. Create a new branch from master branch.
2. Create a new Dockerfile for the new Postgres version. For example for postgres 16 we need to add postgres-16/Dockerfile by copying the postgres-15/Dockerfile.
3. Change the postgres version in the new Dockerfile to the new Postgres version.
4. Test the new Dockerfile by running the below command in the root directory of the repository.

```
docker build -t citusdata/citus:16.0.0-postgres-16 .
```
5. If the build is successful, test the new docker image by running the below command.

```
# run PostgreSQL with Citus on port 5500
docker run -d --name citus -p 5500:5432 -e POSTGRES_PASSWORD=mypassword citusdata/citus:16.0.0-postgres-16
# connect using psql within the Docker container
docker exec -it citus psql -U postgres
# or, connect using local psql
psql -U postgres -d postgres -h localhost -p 5500
```
6. Add new postgres version support to the scheduled pipeline by adding the new postgres version to the pipelines.
7. If the tests are successful, create a PR to merge the changes to master branch.

Adding new postgres version support to the tools scripts
--------------------------------------------------------

When a new Postgres version is released, we need to add the new Postgres version support to the tools scripts.
Mainly `update_docker.py <https://github.com/citusdata/tools/blob/develop/packaging_automation/update_docker.py> script
needs to be updated to add the new Postgres version support.
This script is being used in the pipelines.





