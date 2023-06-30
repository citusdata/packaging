Packaging Tools Scripts
=======================

Packaging operations are executed using a collection of Python scripts stored in the `tools <https://github.com/citusdata/tools>`_ repository.
These scripts are written in Python and require Python 3.8 or higher. They have been tested on Ubuntu focal.

Whenever a change is made, a tag is added to the commit and pushed to the repository. The tag follows the `v<major_version>.<minor_version>.<patch_version>` format.
The scripts are primarily utilized within GH Actions pipelines, where the corresponding tag is used.

The following scripts are employed for packaging purposes:

Tools Scripts
-------------

We utilize specific Python scripts to perform packaging operations. These scripts can be found at `https://github.com/citusdata/tools`.

For each change, we create a new tag for the latest release and incorporate that tag into the pipelines.

Packaging Scripts
~~~~~~~~~~~~~~~~~

The following provides an overview of the scripts used within the pipelines to execute various packaging operations:

* citus_package: This is the main script responsible for building the packages.
* update_docker: This script generates Citus Docker images for end users.
* upload_to_package_cloud: Publishes the packages created by citus_package to Package Cloud.
* publish_docker: Publishes the Docker images created by the update_docker script.
* delete_packages_on_package_cloud: Removes nightly packages older than 10 days from Package Cloud to reduce repository size and lower Package Cloud bills.
