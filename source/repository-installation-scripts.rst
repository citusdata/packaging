Repository Installation Scripts
===============================

Citus packages are stored in packagecloud.io. To install the packages, you can use the packagecloud.io installation scripts directly.
However, custom installation scripts are provided for convenience. Benefits of using the custom installation scripts are:
1. install.citusdata.com/repos.citusdata.com is used as the repository URL instead of packagecloud.io. These URLs are our own URLs
 and isolating users from packagecloud.io which is useful in case we need to change the packagecloud.io URL in the future.
2. Since our packages directly related to postgresql, we install postgresql repository for convenience.
3. Programs like curl, wget, gnupg, apt-transport-https are installed if they are not already installed which are required for installing postgres and citus packages.

Repository Installation Scripts are stored in the `packaging/gh-pages branch <https://github.com/citusdata/packaging/tree/gh-pages>`_.
Files stored in this branch are served using GH pages.
You can see the GH Pages settings in the `settings <https://github.com/citusdata/packaging/settings/pages>`_.
The original url of the files are `https://citusdata.github.io/packaging/<path to file>`_.
For example, the url of the `deb.sh < https://citusdata.github.io/packaging/community/deb.sh>`_.
install.citusdata.com/repos.citusdata.com is a CNAME record for citusdata.github.io in our DNS settings in Cloudflare.
For more information about url redirection, please refer to Citus Packaging Web Url Certificates document

There are 8 scripts in this branch for 4 repositories the packagecloud.io.
1. community
    * `deb.sh <https://github.com/citusdata/packaging/blob/gh-pages/community/deb.sh>`_
    * `rpm.sh <https://github.com/citusdata/packaging/blob/gh-pages/community/rpm.sh>`_
2. community-nightlies
    * `deb.sh <https://github.com/citusdata/packaging/blob/gh-pages/community-nightlies/deb.sh>`_
    * `rpm.sh <https://github.com/citusdata/packaging/blob/gh-pages/community-nightlies/rpm.sh>`_
3. enterprise
    * `deb.sh <https://github.com/citusdata/packaging/blob/gh-pages/enterprise/deb.sh>`_
    * `rpm.sh <https://github.com/citusdata/packaging/blob/gh-pages/enterprise/rpm.sh>`_
4. enterprise-nightlies
    * `deb.sh <https://github.com/citusdata/packaging/blob/gh-pages/enterprise-nightlies/deb.sh>`_
    * `rpm.sh <https://github.com/citusdata/packaging/blob/gh-pages/enterprise-nightlies/rpm.sh>`_

These scripts are used to install the repositories. For example, to install the community repository, you can run the following command:

For Debian/Ubuntu for community repository:

```
curl https://install.citusdata.com/community/deb.sh | sudo bash
```

For RHEL/CentOS for community repository:

```
curl https://install.citusdata.com/community/rpm.sh | sudo bash
```


