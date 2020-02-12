# vim:set ft=dockerfile:
FROM oraclelinux:7

# FIXME: Hack around docker/docker#10180
RUN ( yum install -y yum-plugin-ovl || yum install -y yum-plugin-ovl ) \
    && yum clean all

# FIXME: make sure ol7_developer repo is available
# see https://oracle-base.com/articles/linux/download-the-latest-oracle-linux-repo-file#oracle-linux-7-updated
RUN pushd /etc/yum.repos.d/ \
    && rm -f * \
    && curl -O http://yum.oracle.com/public-yum-ol7.repo \
    && popd

# install build tools and PostgreSQL development files
RUN yum-config-manager --enable \
        ol7_software_collections \
        ol7_developer \
        ol7_developer_EPEL \
    && yum groupinstall -y 'Development Tools' \
    && yum install -y \
        curl \
        flex \
        gcc-c++ \
        hunspell-en \
        libcurl-devel \
        libicu-devel \
        libxml2-devel \
        libxslt-devel \
        llvm-toolset-7-clang \
        llvm5.0 \
        openssl-devel \
        pam-devel \
        readline-devel \
        rpm-build \
        rpmlint \
        spectool \
        tar \
    && yum install -y https://download.postgresql.org/pub/repos/yum/11/redhat/rhel-7-x86_64/pgdg-oraclelinux11-11-2.noarch.rpm \
    && yum install -y postgresql11-server postgresql11-devel \
    && yum clean all
# install documentation generation libraries
RUN yum install -y python-pip python-sphinx \
    && pip install --upgrade pip \
    && pip install -U Sphinx

# install jq to process JSON API responses
RUN curl -sL https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 \
         -o /usr/bin/jq \
    && chmod +x /usr/bin/jq

# install latest Citus release to get header files
RUN curl -s https://packagecloud.io/install/repositories/citusdata/community/script.rpm.sh | bash \
    && yum clean all

RUN touch /rpmlintrc \
    && echo '%_build_pkgcheck %{_bindir}/rpmlint -f /rpmlintrc' >> /etc/rpm/macros

# set PostgreSQL version, place scripts on path, and declare output volume
ENV PGVERSION=11 \
    PATH=/scripts:$PATH
COPY scripts /scripts
VOLUME /packages

ENTRYPOINT ["/scripts/fetch_and_build_rpm"]
