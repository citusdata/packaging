Introduction
===============================

Welcome to the documentation outlining the packaging process for Citus and its associated projects. Packaging plays a crucial role in the distribution and deployment of software, ensuring that it can be easily installed and utilized across various operating systems and environments.

In this document, we will explore the steps and best practices involved in preparing packages for different operating systems and releases. We will focus on the Debian and RPM package formats, as they are widely used and supported in the industry. Additionally, we will cover the creation and management of Docker environments to facilitate packaging for specific OS/release/PostgreSQL version combinations.

The supported operating systems and releases for packaging include:

- CentOS 8
- CentOS 7
- Oracle Linux 8
- Oracle Linux 7
- AlmaLinux 9
- Debian Buster
- Debian Bullseye
- Debian Bookworm
- Ubuntu Bionic
- Ubuntu Focal
- Ubuntu Jammy
- Ubuntu Kinetic

The packaging process will involve preparing packages for various projects, including:

* `Citus <https://github.com/citusdata/packaging/tree/all-citus>`_
* `Pgazure <https://github.com/citusdata/packaging/tree/all-pg-azure-storage>`_
* Cron
    * `Cron Debian <https://github.com/citusdata/packaging/tree/debian-cron>`_
    * `Cron RPM <https://github.com/citusdata/packaging/tree/redhat-cron>`_
* Hll
    * `Hll Debian <https://github.com/citusdata/packaging/tree/debian-hll>`_
    * `Hll RPM <https://github.com/citusdata/packaging/tree/redhat-hll>`_
* Topn
    * `Topn Debian <https://github.com/citusdata/packaging/tree/debian-topn>`_
    * `Topn RPM <https://github.com/citusdata/packaging/tree/redhat-topn>`_
* `Azure-gdpr <https://github.com/citusdata/packaging/tree/all-azure_gdpr>`_

Once the packages are ready, we will push them to PackageCloud, a package management and distribution service. Additionally, we will create Docker images for each OS/release/PostgreSQL version combination, which will be published on Docker Hub.

Lastly, we will cover the publishing of the applications into PGXN (PostgreSQL Extension Network), a platform that hosts and distributes PostgreSQL extensions.

By following the steps outlined in this document, you will gain a comprehensive understanding of the packaging process for Citus and related projects. This knowledge will empower you to efficiently distribute and deploy the software across a wide range of operating systems and environments.

Now, let's dive into the detailed steps for package preparation, Docker environment management, Docker image creation, PackageCloud integration, and PGXN publishing.
