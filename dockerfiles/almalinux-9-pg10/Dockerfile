# vim:set ft=dockerfile:
FROM almalinux:9
RUN [[ almalinux != centos ]] || [[ 9 != 8 ]] || ( \
    cd /etc/yum.repos.d/ && sed -i 's/mirrorlist/#mirrorlist/g' /etc/yum.repos.d/CentOS-* \
    && sed -i 's|#baseurl=http://mirror.centos.org|baseurl=http://vault.epel.cloud|g' /etc/yum.repos.d/CentOS-* \
    )

RUN yum -y update

# FIXME: Hack around docker/docker#10180
RUN ( yum install -y yum-plugin-ovl || yum install -y yum-plugin-ovl || touch /var/lib/rpm/* ) \
    && yum clean all

# Enable some other repos for some dependencies in OL/7 
# see https://yum.oracle.com/getting-started.html#installing-from-oracle-linux-yum-server
RUN [[ almalinux != oraclelinux ]] || [[ 9 != 7 ]] || ( \
       yum install -y oraclelinux-release-el7 oracle-softwarecollection-release-el7 oracle-epel-release-el7  oraclelinux-developer-release-el7 \
       && yum-config-manager --enable \
            ol7_software_collections \
            ol7_developer \
            ol7_developer_EPEL \
            ol7_optional_latest \
            ol7_optional_archive \
            ol7_u9_base \
            ol7_security_validation \
            ol7_addons \
         )

# lz4 1.8 is preloaded in oracle 7 however, lz4-devel is not loaded and only 1.7.5 version exists
# in oracle 7 repos. So package from centos repo was used
# There is no package in oracle repos for lz4. Also it is not preloaded. So both lz4 and lz4-devel packages
# were downloaded from centos el/6 repos
RUN if [[ almalinux   == oraclelinux ]] && [[ 9 == 7 ]]; then yum install -y wget \
        && wget http://mirror.centos.org/centos/7/os/x86_64/Packages/lz4-devel-1.8.3-1.el7.x86_64.rpm \
        && rpm -ivh lz4-devel-1.8.3-1.el7.x86_64.rpm ; \
        elif [[ almalinux   == oraclelinux ]] && [[ 9 == 6 ]]; then yum install -y wget \
        && wget https://cbs.centos.org/kojifiles/packages/lz4/r131/1.el6/x86_64/lz4-r131-1.el6.x86_64.rpm \
        && rpm -ivh lz4-r131-1.el6.x86_64.rpm \
        && wget https://cbs.centos.org/kojifiles/packages/lz4/r131/1.el6/x86_64/lz4-devel-r131-1.el6.x86_64.rpm \
        && rpm -ivh lz4-devel-r131-1.el6.x86_64.rpm;  \
        else yum install -y lz4 lz4-devel; fi

# install build tools and PostgreSQL development files
RUN ( yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-9-x86_64/pgdg-redhat-repo-latest.noarch.rpm  \
    && [[ -z "epel-release" ]] || yum install -y epel-release) \
    && yum groupinstall -y 'Development Tools' \
    && yum install -y \
        bzip2-devel \
        libffi-devel \
        xz-devel \
        flex \
        gcc-c++ \
        hunspell-en \
        libcurl-devel \
        libicu-devel \
        libstdc++-devel \
        libxml2-devel \
        libxslt-devel \
        openssl-devel \
        pam-devel \
        readline-devel \
        rpm-build \
        rpmlint \
        tar \
        libzstd \
        libzstd-devel \
        llvm-toolset ccache rpmdevtools krb5-devel \
    && ( [[ 9 != 8 ]] || dnf -qy module disable postgresql ) \
    && yum install -y postgresql10-server postgresql10-devel \
    && yum clean all

# install jq to process JSON API responses
RUN curl -sL https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 \
         -o /usr/bin/jq \
    && chmod +x /usr/bin/jq

# install devtoolset-8-gcc on distros where it is available
RUN { \
        { yum search devtoolset-8-gcc 2>&1 | grep 'No matches found' ; } \
        || yum install -y devtoolset-8-gcc devtoolset-8-libstdc++-devel; \
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

# install cmake, devtoolset and its dependencies to build azure sdk
RUN yum -y install  perl-IPC-Cmd libuuid-devel cmake3

# by default git 1.8.x is being installed in centos 7
# Git 2.7.1 is minimum requirement for cmake so we remove and reinstall latests git from an up-to-date repo
# Symbolic link is not being created for cmake from cmake3 by default. Therefore, we need to create the link as well.
# devtoolset-8-gcc-c++ is required to compile azure sdk in pg azure storage project
RUN [[ almalinux != centos ]] || [[ 9 != 7 ]] || ( \
    yum -y install  perl-IPC-Cmd libuuid-devel cmake3 && \
    ln -s /usr/bin/cmake3 /usr/bin/cmake  && \
    yum -y remove git && \
    yum -y install https://packages.endpointdev.com/rhel/7/os/x86_64/endpoint-repo.x86_64.rpm && \
    yum -y install git && \
    yum -y install  devtoolset-8-gcc-c++ && scl enable devtoolset-8 bash )

# install python 3.8 to be able to execute tools scripts
ARG PYTHON_VERSION=3.8.16
RUN set -ex \
    && curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
    && export PATH="$HOME/.pyenv/bin:$PATH" \
    && pyenv update \
    && pyenv install $PYTHON_VERSION \
    && pyenv global $PYTHON_VERSION \
    && pyenv rehash

RUN touch /rpmlintrc \
    && echo '%_build_pkgcheck %{_bindir}/rpmlint -f /rpmlintrc' >> /etc/rpm/macros

# set PostgreSQL version, place scripts on path, and declare output volume
ENV PGVERSION=10 \
    PATH=/scripts:$PATH
COPY scripts /scripts
VOLUME /packages

ENTRYPOINT ["/scripts/fetch_and_build_rpm"]
