#!/bin/bash

# Installs PostgreSQL and Citus packages on a Debian/Ubuntu system.
# Usage: install_package.sh <pg_major_version> <citus_version_or_revision>

set -euo pipefail

[ "$#" -eq 2 ] || { echo "Usage: $0 <pg_major_version> <citus_version_or_revision>" >&2; exit 1; }

PG_MAJOR_VERSION="$1"
CITUS_PKG_VERSION="$2"
[[ "${CITUS_PKG_VERSION}" == *".citus-"* ]] || [[ "${CITUS_PKG_VERSION}" == *".citus~"* ]] || CITUS_PKG_VERSION="${CITUS_PKG_VERSION}.citus-1"
CHANNEL="${CITUS_CHANNEL:-community}"
RETRIES="${CITUS_INSTALL_RETRIES:-1}"
RETRY_DELAY="${CITUS_INSTALL_RETRY_DELAY:-30}"

export DEBIAN_FRONTEND=noninteractive
apt-get -y update
apt-get -y install curl ca-certificates
install -d /usr/share/postgresql-common/pgdg
curl -o /usr/share/postgresql-common/pgdg/apt.postgresql.org.asc --fail https://www.postgresql.org/media/keys/ACCC4CF8.asc
# shellcheck disable=SC1091
. /etc/os-release
comp="main"; [ "${PG_MAJOR_VERSION}" = "19" ] && comp="main 19"
echo "deb [signed-by=/usr/share/postgresql-common/pgdg/apt.postgresql.org.asc] https://apt.postgresql.org/pub/repos/apt ${VERSION_CODENAME}-pgdg ${comp}" > /etc/apt/sources.list.d/pgdg.list
apt-get -y update
apt-get -y install "postgresql-${PG_MAJOR_VERSION}"

curl --fail "https://install.citusdata.com/${CHANNEL}/deb.sh" > add-citus-repo.sh
bash add-citus-repo.sh

mm=$(sed -E 's/^([0-9]+\.[0-9]+).*/\1/' <<< "${CITUS_PKG_VERSION}")
if [ "${CHANNEL}" = "community-nightlies" ] || [[ "${CITUS_PKG_VERSION}" == *"~git."* ]]; then
    pkg_name="postgresql-${PG_MAJOR_VERSION}-citus"
elif [[ "${CITUS_PKG_VERSION}" == *[_-]beta* ]]; then
    pkg_name="postgresql-${PG_MAJOR_VERSION}-citus-beta-${mm}"
else
    pkg_name="postgresql-${PG_MAJOR_VERSION}-citus-${mm}"
fi

for attempt in $(seq 1 "${RETRIES}"); do
    if [ "${attempt}" -gt 1 ]; then
        echo "Package ${pkg_name}=${CITUS_PKG_VERSION} not indexed yet; retrying in ${RETRY_DELAY}s (${attempt}/${RETRIES})..."
        sleep "${RETRY_DELAY}"
        apt-get -y update
    fi
    if apt-get -y install "${pkg_name}=${CITUS_PKG_VERSION}"; then
        echo "PostgreSQL and Citus packages installed successfully."
        exit 0
    fi
done

echo "Error: failed to install exact package ${pkg_name}=${CITUS_PKG_VERSION} after ${RETRIES} attempt(s)." >&2
exit 1
