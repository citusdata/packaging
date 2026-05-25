#!/bin/bash

# Installs PostgreSQL and Citus packages on a Debian/Ubuntu system.
#
# Note: need to run this as root
#
# Usage: install_package.sh <pg_major_version> <citus_full_version>
# Example: install_package.sh 18 14.0.0

set -euo pipefail

if [ "$#" -ne 2 ]; then
    echo "Error: some arguments are missing." >&2
    echo "Usage: $0 <pg_major_version> <citus_full_version>" >&2
    exit 1
fi

PG_MAJOR_VERSION="$1"
CITUS_FULL_VERSION="$2"

export DEBIAN_FRONTEND=noninteractive

apt-get -y update

## install postgres

echo "Installing PostgreSQL ..."

apt-get -y install curl ca-certificates

install -d /usr/share/postgresql-common/pgdg
curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
. /etc/os-release
sh -c "echo 'deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt $VERSION_CODENAME-pgdg main' > /etc/apt/sources.list.d/pgdg.list"

apt -y update
apt-get -y install postgresql-${PG_MAJOR_VERSION}

## install citus

echo "Installing Citus ..."

curl --fail https://install.citusdata.com/community/deb.sh > add-citus-repo.sh
bash add-citus-repo.sh

citus_major_minor_version="${CITUS_FULL_VERSION%.*}"
apt-get -y install postgresql-${PG_MAJOR_VERSION}-citus-${citus_major_minor_version}=${CITUS_FULL_VERSION}.citus-1

echo "PostgreSQL and Citus packages installed successfully."
