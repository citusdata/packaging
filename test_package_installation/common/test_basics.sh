#!/bin/bash

# Sets up a multi-node Citus cluster, creates a distributed table,
# rebalances shards, and verifies even distribution.
#
# Note: need to run this as root
#
# Usage: test_basics.sh <expected_pg_major_version> <expected_citus_full_version> <pg_binary_path>
# Example: test_basics.sh 18 14.0.0 /usr/lib/postgresql/17/bin

set -euo pipefail

if [ "$#" -ne 3 ]; then
    echo "Error: some arguments are missing." >&2
    echo "Usage: $0 <expected_pg_major_version> <expected_citus_full_version> <pg_binary_path>" >&2
    exit 1
fi

EXPECTED_PG_MAJOR_VERSION="$1"
EXPECTED_CITUS_FULL_VERSION="$2"
PG_BIN="$3"

## constants and helpers

NODE_COUNT=3
SHARDS_PER_NODE=5
FIRST_NODE_PORT=9700

run_psql_cmd() {
    if [ "$#" -ne 2 ]; then
        echo "Error: some arguments are missing." >&2
        echo "Usage: run_psql_cmd <port_number> <sql_command>" >&2
        exit 1
    fi

    PORT_NUMBER="$1"
    SQL_COMMAND="$2"

    su - postgres -c "${PG_BIN}/psql -X -qAt -p ${PORT_NUMBER} -c \"${SQL_COMMAND}\""
}

## initialize all nodes and create citus extension on them

echo "Initializing nodes and creating citus extension on them ..."

mkdir -p /test_cluster
chown postgres:postgres /test_cluster
chmod 755 /test_cluster

for i in $(seq 0 $((NODE_COUNT - 1))); do
    node_name="node${i}"
    echo "Creating node: $node_name"

    su - postgres -c "mkdir -p /test_cluster/${node_name}"

    port_number=$((FIRST_NODE_PORT + i))

    su - postgres -c "${PG_BIN}/initdb -D /test_cluster/${node_name}"
    su - postgres -c "echo \"shared_preload_libraries = 'citus'\" >> /test_cluster/${node_name}/postgresql.conf"
    su - postgres -c "${PG_BIN}/pg_ctl -D /test_cluster/${node_name} -o \"-p $port_number\" -l /test_cluster/${node_name}/logfile start"
    run_psql_cmd "$port_number" "CREATE EXTENSION citus;"
done

## verify PG version

pg_version=$(run_psql_cmd "$FIRST_NODE_PORT" "SELECT version();")
if [[ "$pg_version" != "PostgreSQL ${EXPECTED_PG_MAJOR_VERSION}."* ]]; then
    echo "Error: PostgreSQL version verification failed. Expected version to start with 'PostgreSQL ${EXPECTED_PG_MAJOR_VERSION}.', got: $pg_version" >&2
    exit 1
else
    echo "Verified PostgreSQL version: $pg_version"
fi

## verify Citus extension version

citus_version=$(run_psql_cmd "$FIRST_NODE_PORT" "SHOW citus.version;")
if [[ "$citus_version" != "${EXPECTED_CITUS_FULL_VERSION}"* ]]; then
    echo "Error: Citus version verification failed. Expected version to start with '${EXPECTED_CITUS_FULL_VERSION}', got: $citus_version" >&2
    exit 1
else
    echo "Verified Citus version: $citus_version"
fi

## create a distributed table

echo "Creating a distributed table ..."

shard_count=$((NODE_COUNT * SHARDS_PER_NODE))
run_psql_cmd "$FIRST_NODE_PORT" "CREATE TABLE test_table (id INT); SELECT create_distributed_table('test_table', 'id', shard_count => $shard_count);"

## add worker nodes

echo "Adding worker nodes ..."

for i in $(seq 1 $((NODE_COUNT - 1))); do
    port_number=$((FIRST_NODE_PORT + i))
    run_psql_cmd "$FIRST_NODE_PORT" "SELECT citus_add_node('localhost', $port_number);"
done

## run rebalancer

echo "Running shard rebalancer ..."

run_psql_cmd "$FIRST_NODE_PORT" "SELECT rebalance_table_shards(shard_transfer_mode =>'block_writes');"

## verify that shards are distributed evenly across nodes

echo "Verifying that shards are distributed evenly across nodes ..."

result=$(
    run_psql_cmd "$FIRST_NODE_PORT" "
        SELECT bool_and(cnt = $SHARDS_PER_NODE)
        FROM (
            SELECT nodeport,
                   COUNT(shardid) AS cnt
            FROM pg_dist_node
            LEFT JOIN pg_dist_shard_placement USING (nodeport)
            GROUP BY nodeport
        ) t;
    "
)

if [ "$result" = "t" ]; then
    echo "Verified cluster creation, distributed table creation and shard rebalancing. Shards are distributed evenly across nodes."
else
    echo "Error: Failed. Shards are not distributed evenly across nodes, see below for details:" >&2
    run_psql_cmd "$FIRST_NODE_PORT" "
        SELECT nodeport,
               COUNT(shardid) AS cnt
        FROM pg_dist_node
        LEFT JOIN pg_dist_shard_placement USING (nodeport)
        GROUP BY nodeport;
    "
    exit 1
fi
