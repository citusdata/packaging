# vim:set ft=dockerfile:
FROM debian:buster
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

# install build tools and PostgreSQL development files

RUN echo 'deb http://apt.postgresql.org/pub/repos/apt/ buster-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
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
        wget \
        zlib1g-dev \
        python3-pip \
        python3-setuptools \
        liblz4-dev \
        liblz4-1 \
        libzstd1 \
        libzstd-dev \
    && rm -rf /var/lib/apt/lists/*

RUN pip3 install sphinx

# install jq to process JSON API responses
RUN curl -sL https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 \
         -o /usr/bin/jq \
    && chmod +x /usr/bin/jq

# install packagecloud repos for pg_auto_failover
RUN curl -s https://packagecloud.io/install/repositories/citusdata/community/script.deb.sh | bash \
    && rm -rf /var/lib/apt/lists/*

# patch pg_buildext to use multiple processors
COPY make_pg_buildext_parallel.patch /
RUN patch `which pg_buildext` < /make_pg_buildext_parallel.patch

# place scripts on path and declare output volume
ENV PATH /scripts:$PATH
COPY scripts /scripts
VOLUME /packages

ENTRYPOINT ["/scripts/fetch_and_build_deb"]
