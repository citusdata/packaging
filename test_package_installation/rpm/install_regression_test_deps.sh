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

yum -y update

## install pg_regress

echo "Installing pg_regress via postgresql${PG_MAJOR_VERSION}-devel ..."

# enable PowerTools/CRB/CodeReady repo for dependencies like perl-IPC-Run
if yum repolist --all | grep -qi 'powertools'; then
    yum config-manager --set-enabled powertools
elif yum repolist --all | grep -qi 'crb'; then
    yum config-manager --set-enabled crb
elif yum repolist --all | grep -qi 'codeready'; then
    repo_id=$(yum repolist --all | grep -i 'codeready' | awk '{print $1}')
    yum config-manager --set-enabled "$repo_id"
fi

yum install -y postgresql${PG_MAJOR_VERSION}-devel

## install contrib extensions needed by regression tests

echo "Installing postgresql${PG_MAJOR_VERSION}-contrib ..."

yum install -y postgresql${PG_MAJOR_VERSION}-contrib

## clone citus repository

echo "Cloning Citus repository (tag v${CITUS_FULL_VERSION}) ..."

CITUS_TAG="v${CITUS_FULL_VERSION}"
CITUS_REPO_DIR="/citus"

yum install -y git
yum groupinstall -y "Development Tools"
git clone --depth 1 --branch "$CITUS_TAG" https://github.com/citusdata/citus "$CITUS_REPO_DIR"

echo "Regression test dependencies installed successfully."
