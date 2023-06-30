Repository Installation Scripts
===============================

Citus packages are hosted on packagecloud.io. You can install the packages directly using the packagecloud.io installation scripts.
However, we also provide custom installation scripts for convenience.
The benefits of using the custom installation scripts are:

1. The repository URL `install.citusdata.com/repos.citusdata.com` is used instead of packagecloud.io.
   These URLs are managed by us, allowing isolation from potential changes to the packagecloud.io URL in the future.

2. The PostgreSQL repository is automatically installed alongside our packages for ease of use.

3. Essential programs such as curl, wget, gnupg, and apt-transport-https are installed if not already present,
   as they are required for installing PostgreSQL and Citus packages.

The Repository Installation Scripts are located in the `packaging/gh-pages branch <https://github.com/citusdata/packaging/tree/gh-pages>`_.
These files are served using GH Pages, and the GH Pages settings can be found in the `settings <https://github.com/citusdata/packaging/settings/pages>`_.
The original URL prefix for the files is `https://citusdata.github.io/packaging/<file-name>`.
For example, the URL for `deb.sh <https://citusdata.github.io/packaging/community/deb.sh>`_.
`install.citusdata.com/repos.citusdata.com` is a CNAME record for `citusdata.github.io` in our DNS settings on Cloudflare.
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

These scripts are used to install the corresponding repositories. For example, to install the community repository, run the following command:

For Debian/Ubuntu:

.. code-block:: shell

   curl https://install.citusdata.com/community/deb.sh | sudo bash

For RHEL/CentOS:

.. code-block:: shell

   curl https://install.citusdata.com/community/rpm.sh | sudo bash
