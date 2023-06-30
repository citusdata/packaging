Repository Installation Scripts
===============================

Citus packages are stored in packagecloud.io. To install the packages, you can use the packagecloud.io installation scripts directly.
However, custom installation scripts are provided for convenience.
The benefits of using the custom installation scripts are:
1. `install.citusdata.com/repos.citusdata.com` is used as the repository URL instead of packagecloud.io. These URLs are our own URLs, isolating users from packagecloud.io, which is useful in case we need to change the packagecloud.io URL in the future.
2. Since our packages are directly related to PostgreSQL, we install the PostgreSQL repository for convenience.
3. Programs like curl, wget, gnupg, and apt-transport-https are installed if they are not already installed, as they are required for installing PostgreSQL and Citus packages.

Repository Installation Scripts are stored in the `packaging/gh-pages branch <https://github.com/citusdata/packaging/tree/gh-pages>`_.
Files stored in this branch are served using GH Pages. You can see the GH Pages settings in the `settings <https://github.com/citusdata/packaging/settings/pages>`_.
The original URL prefix of the files is `https://citusdata.github.io/packaging/<file-name>`.
For example, the URL of `deb.sh <https://citusdata.github.io/packaging/community/deb.sh>`_. `install.citusdata.com/repos.citusdata.com`
is a CNAME record for `citusdata.github.io` in our DNS settings in Cloudflare.
For more information about URL redirection, please refer to the Citus Packaging Web Url Certificates document.

There are 8 scripts in this branch for 4 repositories on packagecloud.io:

1. community

   - `Community deb.sh <https://github.com/citusdata/packaging/blob/gh-pages/community/deb.sh>`_

   - `Community rpm.sh <https://github.com/citusdata/packaging/blob/gh-pages/community/rpm.sh>`_

2. community-nightlies

   - `community-nightlies deb.sh <https://github.com/citusdata/packaging/blob/gh-pages/community-nightlies/deb.sh>`_

   - `community-nightlies rpm.sh <https://github.com/citusdata/packaging/blob/gh-pages/community-nightlies/rpm.sh>`_

3. enterprise

   - `enterprise deb.sh <https://github.com/citusdata/packaging/blob/gh-pages/enterprise/deb.sh>`_

   - `enterprise rpm.sh <https://github.com/citusdata/packaging/blob/gh-pages/enterprise/rpm.sh>`_

4. enterprise-nightlies

   - `enterprise-nightlies deb.sh <https://github.com/citusdata/packaging/blob/gh-pages/enterprise-nightlies/deb.sh>`_

   - `enterprise-nightlies rpm.sh <https://github.com/citusdata/packaging/blob/gh-pages/enterprise-nightlies/rpm.sh>`_

These scripts are used to install the repositories. For example, to install the community repository, you can run the following command:

For Debian/Ubuntu:

.. code-block:: shell

   curl https://install.citusdata.com/community/deb.sh | sudo bash

For RHEL/CentOS:

.. code-block:: shell

   curl https://install.citusdata.com/community/rpm.sh | sudo bash
