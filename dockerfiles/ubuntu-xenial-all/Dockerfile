# vim:set ft=dockerfile:
FROM ubuntu:xenial

# install build tools and PostgreSQL development files
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        dirmngr \
        gnupg2 \
    && apt-key adv --keyserver ha.pool.sks-keyservers.net --recv-keys B97B0AFCAA1A47F044F244A07FCC7D46ACCC4CF8 \
    && echo 'deb http://apt.postgresql.org/pub/repos/apt/ xenial-pgdg main' > /etc/apt/sources.list.d/pgdg.list \
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

# patch pg_buildext to use multiple processors
COPY make_pg_buildext_parallel.patch /
RUN patch `which pg_buildext` < /make_pg_buildext_parallel.patch

# place scripts on path and declare output volume
ENV PATH /scripts:$PATH
COPY scripts /scripts
VOLUME /packages

ENTRYPOINT ["/scripts/fetch_and_build_deb"]
