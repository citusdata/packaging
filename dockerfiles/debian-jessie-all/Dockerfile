# vim:set ft=dockerfile:
FROM debian:jessie

# See https://github.com/tianon/docker-brew-debian/issues/49 for discussion of the following
#
# https://bugs.debian.org/830696 (apt uses gpgv by default in newer releases, rather than gpg)
RUN set -x \
	&& apt-get update \
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

# install build tools and PostgreSQL development files
RUN apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 \
    && echo 'deb http://apt.postgresql.org/pub/repos/apt/ jessie-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
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
        libdistro-info-perl \
        libedit-dev \
        libfile-fcntllock-perl \
        libkrb5-dev \
        libpam0g-dev \
        libselinux1-dev \
        libssl-dev \
        libxslt-dev \
        lintian \
        postgresql-server-dev-all \
        wget \
    && rm -rf /var/lib/apt/lists/*

# install jq to process JSON API responses
RUN curl -sL https://github.com/stedolan/jq/releases/download/jq-1.5/jq-linux64 \
         -o /usr/bin/jq \
    && chmod +x /usr/bin/jq

# install latest Citus release to get header files
RUN curl -s https://packagecloud.io/install/repositories/citusdata/community/script.deb.sh | bash \
    && apt-get install -y postgresql-9.5-citus-6.0 postgresql-9.6-citus-6.0 \
    && rm -rf /var/lib/apt/lists/*

# patch pg_buildext to use multiple processors
COPY make_pg_buildext_parallel.patch /
RUN patch `which pg_buildext` < /make_pg_buildext_parallel.patch

# place scripts on path and declare output volume
ENV PATH /scripts:$PATH
COPY scripts /scripts
VOLUME /packages

ENTRYPOINT ["/scripts/fetch_and_build_deb"]
