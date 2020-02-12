# vim:set ft=dockerfile:
FROM centos:8

# install build tools and PostgreSQL development files
RUN yum install -y epel-release \
    && yum groupinstall -y 'Development Tools' \
    && yum install -y \
        # ccache is needed only for CentOS 8
        # Makefile.global has a hardcoded ccache reference in the PGDG PG package
        ccache \
        curl \
        flex \
        gcc-c++ \
        hunspell-en \
        libcurl-devel \
        libicu-devel \
        libxml2-devel \
        libxslt-devel \
        llvm-toolset \
        openssl-devel \
        pam-devel \
        readline-devel \
        rpm-build \
        rpmlint \
        spectool \
        tar \
    && yum install -y https://download.postgresql.org/pub/repos/yum/11/redhat/rhel-8-x86_64/pgdg-redhat-repo-latest.noarch.rpm \
    && dnf -qy module disable postgresql \
    && yum install -y postgresql11-server postgresql11-devel \
    && yum clean all

# install documentation generation libraries
RUN yum install -y python2 python2-pip  \
    && pip2 install --upgrade pip \
    && pip2 install -U Sphinx

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
