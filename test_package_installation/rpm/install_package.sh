#!/bin/bash

# Installs PostgreSQL and Citus packages on an EL/OL (RPM-based) system.
#
# Note: need to run this as root
#
# Usage: install_package.sh <pg_major_version> <citus_full_version> <os_version>
# Example: install_package.sh 18 14.0.0 8

set -euo pipefail

if [ "$#" -ne 3 ]; then
    echo "Error: some arguments are missing." >&2
    echo "Usage: $0 <pg_major_version> <citus_full_version> <os_version>" >&2
    exit 1
fi

PG_MAJOR_VERSION="$1"
CITUS_FULL_VERSION="$2"
OS_VERSION="$3"

yum -y update

## install postgres

echo "Installing PostgreSQL ..."

yum install -y https://download.postgresql.org/pub/repos/yum/reporpms/EL-${OS_VERSION}-x86_64/pgdg-redhat-repo-latest.noarch.rpm

# disable the built-in PostgreSQL module
yum -qy module disable postgresql

yum install -y postgresql${PG_MAJOR_VERSION}-server

## install citus

echo "Installing Citus ..."

curl --fail https://install.citusdata.com/community/rpm.sh > add-citus-repo.sh
bash add-citus-repo.sh

citus_major_minor_version="${CITUS_FULL_VERSION%.*}"
citus_major_minor_version_without_dot="${citus_major_minor_version//./}"

yum install -y citus${citus_major_minor_version_without_dot}_${PG_MAJOR_VERSION}-${CITUS_FULL_VERSION}.citus-1.el${OS_VERSION}

echo "PostgreSQL and Citus packages installed successfully."
