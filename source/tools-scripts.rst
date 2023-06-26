Packaging Tools Scripts
=======================

Packaging operations are performed by a set of python scripts stored under the `tools <https://github.com/citusdata/tools>`_ repository.
The scripts are written in python and require python 3.8 or higher. The scripts are tested on Ubuntu focal.

For each change we add a tag to the commit and push it to the repository. The tag is of the form `v<major_version>.<minor_version>.<patch_version>` format.
Mainly, we are using the scripts inside GH Actions pipelines. In these pipelines we use the tools scripts with the corresponding tag.

For more details on the tools scripts, please refer to the `tools README <https://github.com/citusdata/tools/blob/master/README.md>`_.