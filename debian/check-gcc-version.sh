#!/bin/bash
set -euxo pipefail

currentgccver="$($(pg_config --cc) -dumpversion)"
requiredgccver="4.8.2"
if [ "$(printf '%s\n' "$requiredgccver" "$currentgccver" | sort -V | tail -n1)" = "$requiredgccver" ]; then
    echo ERROR: At least GCC version "$requiredgccver" is needed
    exit 1
fi
