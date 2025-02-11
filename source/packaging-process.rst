Packaging Process
=================

The packaging process consists of the following steps:

1. Bake deb and rpm packages
2. Bake docker images
3. Bake pgxn package
4. Open issue for PGDG packaging
5. Update: Repository Installation Scripts

Bake deb and rpm packages
---------------------------
        
In this phase, the packaging configuration files need to be edited to bake the packages for the desired application version.

Since this step relies on tools from the `citusdata/tools <https://github.com/citusdata/tools>`_ repository, some adjustments may be required before proceeding. For instance, if support for a new PostgreSQL version is needed, the package automation script must be updated accordingly.

Editing Configuration Files by Pipeline
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Citus has an automation process to edit the packaging configuration scripts called the  `Update Package Properties <https://github.com/citusdata/packaging/actions/workflows/update_package_properties.yml>`_ workflow.

By executing this workflow on the all-citus branch, a new pull request (PR) will be generated in the packaging repository. To do this, click the "Run Workflow" button, select all-citus as the branch for "Use workflow from," enter the tag name for the project repository to be released, and fill in any other necessary details.

This PR will update the packaging configuration files to the desired version. The tools version used in the workflow may need to be updated. Here you can find an example PR: `PR #1121 <https://github.com/citusdata/packaging/pull/1121/files>`_.


Once the necessary checks have passed, a review can be requested from the packaging team.

After the review is completed and the PR is merged, the workflow will execute all necessary jobs. Once finished, the updated packages will be available in the `Citusdata Package Repository <https://packagecloud.io/>`_.

Before moving to the next step, it is crucial to verify that the new packages are available for all supported distributions in the repository.

Editing Configuration Files Manually
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

For projects like pg_azure_storage and azure-gdpr that do not have automation pipelines, the configuration files need to be edited manually.
There are two categories of projects that require manual configuration file editing:

1. Projects with deb and rpm configuration files in the same branch:
    - For projects in this category, such as pg_azure_storage and azure-gdpr, the following steps can be followed:
        - Create a new branch from the latest commit on the master branch.
        - Edit the configuration files to the desired version:
            - Add a new entry to the `debian/changelog` file.
            - Update the version in the pkgvars file.
            - Update the version in the rpm spec file.
            - Add a new changelog entry to the rpm spec file.
        - Create a pull request (PR) from the new branch to the master branch.
        - After the PR is merged, the new packages can be found in the `Citusdata Package Repository <https://packagecloud.io/>`_. It is important to ensure that the new packages are available for all supported distributions in the repository before proceeding to the next step.

2. Projects with deb and rpm configuration files in different branches:
   - For projects like topn, hll, and cron that have deb and rpm configuration files in different branches, the following steps can be followed:

     **Debian Configuration Files:**
     - Checkout the debian-<project_name> branch.
     - Create a new branch from the latest commit on the debian-<project_name> branch.
     - Edit the configuration files to the desired version:

       - Add a new entry to the `debian/changelog` file.
       - Update the version in the pkgvars file.

     - Create a PR from the new branch to the debian-<project_name> branch.
     - After the PR is merged, the new packages can be found in the `Citusdata Package Repository <https://packagecloud.io/>`_.
       It is important to ensure that the new packages are available for all supported distributions in the repository before proceeding to the next step.

     **Redhat Configuration Files:**
     - Checkout the rpm-<project_name> branch.
     - Create a new branch from the latest commit on the rpm-<project_name> branch.
     - Edit the configuration files to the desired version:

       - Update the version in the rpm spec file.
       - Add a new changelog entry to the rpm spec file.

     - Create a PR from the new branch to the rpm-<project_name> branch.
     - After the PR is merged, the new packages can be found in the `Citusdata Package Repository <https://packagecloud.io/>`_. It is important to ensure that the new packages are available for all supported distributions in the repository before proceeding to the next step.

    Example PRs to generate TopN packages can be found:
    
    - `PR #1123 <https://github.com/citusdata/packaging/pull/1123/files>`_
    - `PR #1122 <https://github.com/citusdata/packaging/pull/1122/files>`_


Bake docker images
------------------

This step is applicable only for Citus Community.

See the Citus Docker images <https://citusdata-packaging.readthedocs.io/en/latest/citus-docker-images.html>`_ for more details.

Baking Main versions
~~~~~~~~~~~~~~~~~~~~

In this phase, the docker image configuration files need to be edited to bake the docker images for the desired application version.

The `Update Version on Docker Files <https://github.com/citusdata/docker/blob/master/.github/workflows/update_version.yml>`_ workflow can be used to edit the docker image configuration files.  
By executing this workflow on the master branch, a new pull request (PR) will be generated in the docker repository.  

To do this, click the **"Run Workflow"** button, select `master` as the branch for **"Use workflow from,"** enter the version number to be released, and fill in any other necessary details.

This PR will update the docker image configuration files to the desired version. Here you can find an example PR: `PR #354 <https://github.com/citusdata/docker/pull/354/files>`_.

Once all the necessary checks have passed, a review can be requested from the packaging team.

After the review is completed, the PR can be merged.

Once all the jobs are finished, the new docker images can be found in the `Citusdata Docker Repository <https://hub.docker.com/r/citusdata/citus>`_.

The versioned images should appear in the docker repository for all supported postgres versions and alpine.

Create Images for Patch Releases
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In this phase, docker images need to be created for patch releases.
For example, if there is a patch release for version 10.1.1, docker images need to be created for versions 10, 10.1, and 10.1.1.

To create docker images for patch releases, a tag needs to be added to the latest commit on the master branch and pushed.

The `The tag pipeline <https://github.com/citusdata/docker/blob/master/.github/workflows/publish_docker_images_on_tag.yml>`_  pipeline will create the docker images for the tag and push them to the docker repository.

Once all the jobs are finished, the new docker images can be found in the `Citusdata Docker Repository <https://hub.docker.com/r/citusdata/citus>`_.

The versioned images should appear in the docker repository for all supported postgres versions and alpine.

Bake pgxn package
-----------------

When building the pgxn extension for Citus, the following steps need to be followed:

1. Execute the `Update Version on PGXN Config Files <https://github.com/citusdata/packaging/actions/workflows/update-pgxn-version.yml>`_ pipeline to update the version in the pgxn configuration files. This pipeline will create a pull request (PR) with the updated version.
2. Check for the minimum postgres version and update it if necessary.
3. Check that all the tests pass and notify the PR reviewer to review the PR.
4. Once the PR is reviewed, merge the PR and ensure that the Citus PGXN is updated with the new version.

See the `PGXN documentation <https://citusdata-packaging.readthedocs.io/en/latest/pgxn.html>`_ for more details.

Opening an issue for PGDG packaging
-----------------------------------

After all the packages are baked, an issue needs to be opened for PGDG packaging. PGDG is a repository of PostgreSQL packages for several Linux distributions.

Citus packages are available for RPM-based distributions.
To request a new release for Citus, an issue needs to be opened in the `PostgreSQL YUM Repository Issues <https://redmine.postgresql.org/projects/pgrpms/issues>`_.

The required fields for the issue are as follows:

- Tracker: Bug
- Subject: New release of Citus <version>
- Description: Provide a detailed description of the new release, including any notable changes or improvements.
- Category: Package update
- Priority: Normal
- Target version: <appropriate version>
- Assignee: Leave blank unless specified example: PostgreSQL 15 and above

Please make sure to include all the necessary information and follow the bug reporting guidelines provided by the PostgreSQL YUM Repository.
An example issue record can be found here: `Issue #8092 <https://redmine.postgresql.org/issues/8092>`_.

See the `Citus PGDG Packages <https://citusdata-packaging.readthedocs.io/en/latest/pgdg.html>`_ for more details.


Update: Repository Installation Scripts
---------------------------------------

The repository installation scripts have been updated to support the new PostgreSQL version. This ensures compatibility with the latest PostgreSQL releases.

For complete details on the script changes and usage instructions, please refer to `Repository Installation Scripts <https://citusdata-packaging.readthedocs.io/en/latest/repository-installation-scripts.html>`_
