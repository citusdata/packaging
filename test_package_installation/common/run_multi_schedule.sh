#!/bin/bash

# Runs "make check-multi" (multi_schedule).
#
# Expects the Citus source to be cloned at /citus and pg_regress
# to be available in the PostgreSQL binary path.
#
# Usage: run_multi_schedule.sh <pg_binary_path>
# Example: run_multi_schedule.sh /usr/lib/postgresql/18/bin

set -euo pipefail

if [ "$#" -ne 1 ]; then
    echo "Error: some arguments are missing." >&2
    echo "Usage: $0 <pg_binary_path>" >&2
    exit 1
fi

PG_BIN="$1"

## suppress some of the regression test failures

# On rpm based distros, Postgres package might be linked against a newer ICU
# than the one used to generate expected test output. To avoid test failures
# due to this, patch the expected output to match the newer ICU version.
# Without this, today pg18.sql fails.
echo 's/und-u-kc-true-ks-level1/und-u-kc-ks-level1/g' >> /citus/src/test/regress/bin/normalize.sed

## run "make check-multi"

export PATH="${PG_BIN}:${PATH}"

cd /citus

# we don't need lz4 and zstd as none of the tests in multi_schedule depend on them
./configure PG_CONFIG="${PG_BIN}/pg_config" --without-libcurl --without-lz4 --without-zstd

chown -R postgres:postgres /citus

echo "Running make check-multi ..."

if ! su - postgres -c "make check-multi -C /citus/src/test/regress"; then
    echo "make check-multi failed. Printing regression.diffs ..."
    cat /citus/src/test/regress/regression.diffs
    exit 1
fi

echo "make check-multi completed successfully."
