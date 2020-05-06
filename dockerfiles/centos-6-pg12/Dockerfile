# vim:set ft=dockerfile:
FROM centos:6

# FIXME: Hack around docker/docker#10180
RUN ( yum install -y yum-plugin-ovl || yum install -y yum-plugin-ovl || touch /var/lib/rpm/* ) \
    && yum clean all

# FIXME: make sure ol7_developer repo is available
# see https://oracle-base.com/articles/linux/download-the-latest-oracle-linux-repo-file#oracle-linux-7-updated
RUN [[ centos != oraclelinux ]] || [[ 6 != 7 ]] || ( \
        pushd /etc/yum.repos.d/ \
        && rm -f * \
        && curl -O http://yum.oracle.com/public-yum-ol7.repo \
        && popd \
        && yum-config-manager --enable \
            ol7_software_collections \
            ol7_developer \
            ol7_developer_EPEL \
        && yum clean all ) 

# install build tools and PostgreSQL development files
RUN ( [[ -z "epel-release centos-release-scl-rh" ]] || yum install -y epel-release centos-release-scl-rh) \
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
        openssl-devel \
        pam-devel \
        readline-devel \
        rpm-build \
        rpmlint \
        spectool \
        tar \
        llvm-toolset-7-clang llvm5.0 \
    && yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-6-x86_64/pgdg-redhat-repo-latest.noarch.rpm \
    && ( [[ 6 < 8 ]] || dnf -qy module disable postgresql ) \
    && yum install -y postgresql12-server postgresql12-devel \
    && yum clean all

# install jq to process JSON API responses
RUN curl -sL https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 \
         -o /usr/bin/jq \
    && chmod +x /usr/bin/jq

# install devtoolset-8-gcc on distros where it is available
RUN { \
        { yum search devtoolset-8-gcc 2>&1 | grep 'No matches found' ; } \
        || yum install -y devtoolset-8-gcc ; \
    } \
    && yum clean all

# install sphinx on distros with python3
RUN { \
        { yum search python3-pip 2>&1 | grep 'No matches found' ; } \
        || { \
            yum install -y python3-pip && \
            pip3 install sphinx==1.8 \
            ; \
        } \
    } \
    && yum clean all


RUN touch /rpmlintrc \
    && echo '%_build_pkgcheck %{_bindir}/rpmlint -f /rpmlintrc' >> /etc/rpm/macros

# set PostgreSQL version, place scripts on path, and declare output volume
ENV PGVERSION=12 \
    PATH=/scripts:$PATH
COPY scripts /scripts
VOLUME /packages

ENTRYPOINT ["/scripts/fetch_and_build_rpm"]
