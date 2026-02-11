#!/bin/bash

# Installs dependencies needed to run Citus regression tests.
#
# Note: need to run this as root
#
# Usage: install_regression_test_deps.sh <pg_major_version> <citus_full_version>
# Example: install_regression_test_deps.sh 18 14.0.0

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

## install autoreconf

echo "Installing autoreconf and other build tools ..."

apt-get -y install autoconf automake libtool

## install pg_regress

echo "Installing pg_regress via postgresql-server-dev-${PG_MAJOR_VERSION} ..."

apt-get -y install postgresql-server-dev-${PG_MAJOR_VERSION}

## clone citus repository

echo "Cloning Citus repository (tag v${CITUS_FULL_VERSION}) ..."

CITUS_TAG="v${CITUS_FULL_VERSION}"
CITUS_REPO_DIR="/citus"

apt-get -y install git build-essential
git clone --depth 1 --branch "$CITUS_TAG" https://github.com/citusdata/citus "$CITUS_REPO_DIR"

echo "Regression test dependencies installed successfully."
