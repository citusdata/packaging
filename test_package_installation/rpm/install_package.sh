#!/bin/bash

# Installs PostgreSQL and Citus packages on an EL/OL (RPM-based) system.
# Usage: install_package.sh <pg_major_version> <citus_version_or_revision> <os_version>

set -euo pipefail

[ "$#" -eq 3 ] || { echo "Usage: $0 <pg_major_version> <citus_version_or_revision> <os_version>" >&2; exit 1; }

PG_MAJOR_VERSION="$1"
CITUS_PKG_VERSION="$2"
OS_VERSION="$3"
[[ "${CITUS_PKG_VERSION}" == *".citus-"* ]] || CITUS_PKG_VERSION="${CITUS_PKG_VERSION}.citus-1"
CHANNEL="${CITUS_CHANNEL:-community}"
RETRIES="${CITUS_INSTALL_RETRIES:-1}"
RETRY_DELAY="${CITUS_INSTALL_RETRY_DELAY:-30}"

yum -y update
yum install -y "https://download.postgresql.org/pub/repos/yum/reporpms/EL-${OS_VERSION}-x86_64/pgdg-redhat-repo-latest.noarch.rpm"
yum -qy module disable postgresql || true
yum install -y "postgresql${PG_MAJOR_VERSION}-server"

curl --fail "https://install.citusdata.com/${CHANNEL}/rpm.sh" > add-citus-repo.sh
bash add-citus-repo.sh

mm=$(sed -E 's/^([0-9]+\.[0-9]+).*/\1/' <<< "${CITUS_PKG_VERSION}")
mm_nodot="${mm//./}"
if [[ "${CITUS_PKG_VERSION}" == *[_-]beta* ]]; then
    pkg_name="citus${mm_nodot}_beta_${PG_MAJOR_VERSION}"
else
    pkg_name="citus${mm_nodot}_${PG_MAJOR_VERSION}"
fi
pkg_spec="${pkg_name}-${CITUS_PKG_VERSION}.el${OS_VERSION}"

for attempt in $(seq 1 "${RETRIES}"); do
    if [ "${attempt}" -gt 1 ]; then
        echo "Package ${pkg_spec} not indexed yet; retrying in ${RETRY_DELAY}s (${attempt}/${RETRIES})..."
        sleep "${RETRY_DELAY}"
        yum clean metadata
    fi
    if yum install -y "${pkg_spec}"; then
        echo "PostgreSQL and Citus packages installed successfully."
        exit 0
    fi
done

echo "Error: failed to install exact package ${pkg_spec} after ${RETRIES} attempt(s)." >&2
exit 1
