# vim:set ft=dockerfile:
FROM debian:bookworm
ARG DEBIAN_FRONTEND=noninteractive

# See https://github.com/tianon/docker-brew-debian/issues/49 for discussion of the following
#
# https://bugs.debian.org/830696 (apt uses gpgv by default in newer releases, rather than gpg)
RUN set -x \
	&& apt-get update \
# Fix ipv6 issue on travis: https://github.com/f-secure-foundry/usbarmory-debian-base_image/issues/9#issuecomment-466594168
	&& mkdir ~/.gnupg && echo "disable-ipv6" >> ~/.gnupg/dirmngr.conf \
	&& { \
		which gpg \
# prefer gnupg2, to match APT's Recommends
		|| apt-get install -y --no-install-recommends gnupg2 \
		|| apt-get install -y --no-install-recommends gnupg \
	; } \
# Ubuntu includes "gnupg" (not "gnupg2", but still 2.x), but not dirmngr, and gnupg 2.x requires dirmngr
# so, if we're not running gnupg 1.x, explicitly install dirmngr too
	&& { \
		gpg --version | grep -q '^gpg (GnuPG) 1\.' \
		|| apt-get install -y --no-install-recommends dirmngr \
	; } \
	&& rm -rf /var/lib/apt/lists/*

RUN set -ex; \
# pub   4096R/ACCC4CF8 2011-10-13 [expires: 2019-07-02]
#       Key fingerprint = B97B 0AFC AA1A 47F0 44F2  44A0 7FCC 7D46 ACCC 4CF8
# uid                  PostgreSQL Debian Repository
    key='B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8'; \
    export GNUPGHOME="$(mktemp -d)"; \
# Fix ipv6 issue on travis: https://github.com/f-secure-foundry/usbarmory-debian-base_image/issues/9#issuecomment-466594168
    echo "disable-ipv6" >> $GNUPGHOME/dirmngr.conf; \
    gpg --batch --keyserver hkp://keyserver.ubuntu.com:80 --recv-keys "$key"; \
    gpg --batch --export "$key" > /etc/apt/trusted.gpg.d/postgres.gpg; \
    command -v gpgconf > /dev/null && gpgconf --kill all; \
    rm -rf "$GNUPGHOME"; \
    apt-key list

# add buster backports repo to be able to download missing packages in buster main repo
RUN ( [ debian != debian ] || [ bookworm != buster ] ) || ( \
    echo "deb http://deb.debian.org/debian buster-backports main" >> /etc/apt/sources.list  \
    )

# install build tools and PostgreSQL development files

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ bookworm-pgdg main 16' > /etc/apt/sources.list.d/pgdg.list \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        autotools-dev \
        build-essential \
        ca-certificates \
        curl \
        debhelper \
        devscripts \
        fakeroot \
        flex \
        libbz2-dev \
        libffi-dev \
        libcurl4-openssl-dev \
        libdistro-info-perl \
        libedit-dev \
        libfile-fcntllock-perl \
        libicu-dev \
        libkrb5-dev \
        libpam0g-dev \
        libreadline-dev \
        libselinux1-dev \
        libssl-dev \
        libxslt-dev \
        lintian \
        postgresql-server-dev-all \
        postgresql-server-dev-16 \
        wget \
        zlib1g-dev \
        python3-pip \
        python3-sphinx \
        python3-setuptools \
        liblz4-dev \
        liblz4-1 \
        libzstd1 \
        libzstd-dev \
# below are needed for cmake and pgazure build
        checkinstall \
        git \
        libtemplate-perl \
        pkg-config \
        tar \
        unzip \
        uuid \
        uuid-dev \
        zip \
        sudo \
    && rm -rf /var/lib/apt/lists/*


# install jq to process JSON API responses
RUN curl -sL https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 \
         -o /usr/bin/jq \
    && chmod +x /usr/bin/jq

# install packagecloud repos for pg_auto_failover
RUN curl https://install.citusdata.com/community/deb.sh | bash \
    && rm -rf /var/lib/apt/lists/*

# patch pg_buildext to use multiple processors
COPY make_pg_buildext_parallel.patch /
RUN patch `which pg_buildext` < /make_pg_buildext_parallel.patch


# install cmake from source
RUN wget https://github.com/Kitware/CMake/releases/download/v3.22.2/cmake-3.22.2.tar.gz && \
    tar -zxvf cmake-3.22.2.tar.gz && \
    cd cmake-3.22.2 && ./bootstrap && \
    make && \
    make install && \
    rm -f cmake-3.22.2.tar.gz && \
    rm -rf cmake-3.22.2

# install pyenv and python 3.8 to be able to execute tools scripts
ARG PYTHON_VERSION=3.8.16
RUN set -ex \
    && curl -L https://github.com/pyenv/pyenv-installer/raw/master/bin/pyenv-installer | bash \
    && export PATH="$HOME/.pyenv/bin:$PATH" \
    && pyenv update \
    && pyenv install $PYTHON_VERSION \
    && pyenv global $PYTHON_VERSION \
    && pyenv rehash \
    && echo 'export PYENV_ROOT="$HOME/.pyenv"' >> ~/.bashrc \
    && echo 'command -v pyenv >/dev/null || export PATH="$PYENV_ROOT/bin:$PATH"' >> ~/.bashrc \
    && echo 'eval "$(pyenv init -)"' >> ~/.bashrc


# Added for pg16 beta package support.
ENV DEB_PG_SUPPORTED_VERSIONS="10 11 12 13 14 15 16"

# place scripts on path and declare output volume
ENV PATH /scripts:$PATH
COPY scripts /scripts
VOLUME /packages

ENTRYPOINT ["/scripts/fetch_and_build_deb"]
