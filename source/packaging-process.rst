Packaging Process
=================

Packaging process is done by the following steps:

1. Bake deb and rpm packages
2. Bake docker images
3. Bake pgxn package
4. Open issue for PGDG packaging

Bake deb and rpm packages
---------------------------

In this phase, we need to edit packaging configuration files to bake the packages for the desired application version.

Editing Configuration Files by Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Citus has its own automation to edit the packaging configuration scripts; `Update Package Properties <https://github.com/citusdata/packaging/actions/workflows/update_package_properties.yml>`_ workflow.
After executing this workflow on all-citus branch, you will see a new PR to the packaging repository. This PR will update the packaging configuration files to the desired version.
After seeing all the checks are passed, you can request a review from the packaging team.
After the review is done, you can merge the PR.
After all jobs are done, you can see the new packages in the `Citusdata Package Repository <https://packagecloud.io/>`_.
You need to make sure that the new packages are available for all distros we support in the repository before proceeding to the next step.

Editing Configuration Files Manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Other projects such as pg_azure_storage, topn does not have automation pipelines, so we need to edit the configuration files manually.
There are two categories of projects that we need to edit the configuration files manually.

1. Projects that deb and rpm configuration files are in the same branch
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

``pg_azure_storage``, ``azure-gdpr`` is in this category.
Below are the steps to edit the configuration files manually:

1. Create a new branch from the latest commit on the master branch.
2. Edit the configuration files to the desired version.
    * Add a new entry to the ``debian/changelog`` file.
    * Update the version in the pkgvars file
    * Update the version in the rpm spec file
    * Add a new changelog entry to the rpm spec file
3. Create a PR from the new branch to the master branch.
4. After the PR is merged, you can see the new packages in the `Citusdata Package Repository <https://packagecloud.io/>`_. You need to make sure that the new packages are available for all distros we support in the repository before proceeding to the next step.

2. Projects that deb and rpm configuration files are in different branches
""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""""

``topn``, ``hll`` and ``cron``  is in this category.
Below are the steps to edit the configuration files manually:

Debian Configuration Files
'''''''''''''''''''''''''''

1. Checkout the debian-<project_name> branch.
2. Create a new branch from the latest commit on the debian-<project_name> branch.
3. Edit the configuration files to the desired version.
    * Add a new entry to the ``debian/changelog`` file.
    * Update the version in the pkgvars file
4. Create a PR from the new branch to the debian-<project_name> branch.
5. After the PR is merged, you can see the new packages in the `Citusdata Package Repository <https://packagecloud.io/>`_. You need to make sure that the new packages are available for all distros we support in the repository before proceeding to the next step.

Redhat Configuration Files
'''''''''''''''''''''''''''

1. Checkout the rpm-<project_name> branch.
2. Create a new branch from the latest commit on the rpm-<project_name> branch.
3. Edit the configuration files to the desired version.
    * Update the version in the rpm spec file
    * Add a new changelog entry to the rpm spec file
4. Create a PR from the new branch to the rpm-<project_name> branch.
5. After the PR is merged, you can see the new packages in the `Citusdata Package Repository <https://packagecloud.io/>`_. You need to make sure that the new packages are available for all distros we support in the repository before proceeding to the next step.

Bake docker images
------------------
This step is applicable just for Citus Community.

Baking Main versions
~~~~~~~~~~~~~~~~~~~~
In this phase, we need to edit the docker image configuration files to bake the docker images for the desired application version.
To edit the docker image configuration files, you can use the `Update Version on Docker Files <https://github.com/citusdata/docker/blob/master/.github/workflows/update_version.yml>`_ workflow.
After executing this workflow on master branch, you will see a new PR to the docker repository. This PR will update the docker image configuration files to the desired version.
After seeing all the checks are passed, you can request a review from the packaging team.
After the review is done, you can merge the PR.
After all jobs are done, you can see the new docker images in the `Citusdata Docker Repository <https://hub.docker.com/r/citusdata/citus>`_.
Versions that needs to be in the docker repository are:
1. latest
2. alpine
3. postgres_xx (all supported postgres versions before latest)

Create Images for Patch Releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this phase, we need to create docker images for patch releases. For example, if we have a patch release for 10.1.1, we need to create a docker image for 10, 10.1 and 10.1.1.

To create docker images for patch releases, you just need to add a tag to the latest commit on master branch and push it
`The tag pipeline <https://github.com/citusdata/docker/blob/master/.github/workflows/publish_docker_images_on_tag.yml>`_ will create the docker images for the tag and push them to the docker repository.
After all jobs are done, you can see the new docker images in the `Citusdata Docker Repository <https://hub.docker.com/r/citusdata/citus>`_.
The versioned images should appear in the docker repository for all supported postgres versions and alpine.
For example for 10.1.1 for postgres 13,14,15;  we need to see the following images in the docker repository:

1. 10.1.1 (latest i.e. 15)
2. 10.1   (latest i.e. 15)
3. 10   (latest i.e. 15)
4. 10.1.1-alpine
5. 10.1-alpine
6. 10-alpine
7. 10.1.1-pg13
8. 10.1-pg13
9. 10-pg13
10. 10.1.1-pg14
11. 10.1-pg14
12. 10-pg14

Bake pgxn packages
--------------------------------------------
When we build the pgxn extension for citus, we need to go through the following steps.

1. Execute the pipeline `Update Version on PGXN Config Files <https://github.com/citusdata/packaging/actions/workflows/update-pgxn-version.yml>`_ to update the version in the pgxn configuration files. This pipeline will create a PR with the updated version.

2. Check for the minimum postgres version. If it is different from the one that citus has, it should be changed to the one that citus has.

3. Check for the tests and if they all pass, notify the PR reviewer to review the PR.

4. Once the PR is reviewed, merge the PR and make sure that the `Citus PGXN <https://pgxn.org/dist/citus/>`_ is updated with the new version.

Open issue for PGDG packaging
--------------------------------------------

After all the packages are baked, we need to open an issue for PGDG packaging.
PGDG is a repository of PostgreSQL packages for several Linux distributions.
Citus packages are available for RPM based distributions.
When releasing Citus, we open an issue in Postgres Redmine to request a new release from the link below
https://redmine.postgresql.org/projects/pgrpms/issues/new
We select the fields as below:

* Tracker: Bug

* Subject: https://redmine.postgresql.org/projects/pgrpms/issues/new

* Description: Kindly release the following version of Citus: xx.x.

* Category: New Package

* Priority: Normal

* Target version: <The version of PostgreSQL that Citus is compatible with>

* Assignee: Devrim Gündüz