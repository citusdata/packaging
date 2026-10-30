#!/usr/bin/env bash
set -euo pipefail

source pkgvars
source supported-postgres
case "$pkgname" in
    citus) extension=citus; package_suffix="citus-$(cut -d. -f1,2 <<< "$pkglatest")" ;;
    hll) extension=hll; package_suffix=hll ;;
    postgresql-topn) extension=topn; package_suffix=topn ;;
    *) echo "Unsupported Resolute verification package: $pkgname" >&2; exit 1 ;;
esac

IFS=, read -ra pg_versions <<< "$release_versions"
mapfile -t files < <(find packages -type f -name '*.deb' | sort)
test "${#files[@]}" -eq "$((2 * ${#pg_versions[@]}))"
specs=()
for file in "${files[@]}"; do
    test "$(dpkg-deb -f "$file" Version)" = "$pkglatest"
    test "$(dpkg-deb -f "$file" Architecture)" = "$(dpkg --print-architecture)"
    specs+=("$(dpkg-deb -f "$file" Package)=$pkglatest")
done
for pg in "${pg_versions[@]}"; do
    for suffix in "" "-dbgsym"; do
        printf '%s\n' "${specs[@]}" | grep -Fx "postgresql-$pg-$package_suffix$suffix=$pkglatest"
    done
done

docker run --rm -i -e DEBIAN_FRONTEND=noninteractive \
    -e EXTENSION="$extension" -e PG_VERSIONS="$release_versions" \
    ubuntu:resolute bash -se -- "${specs[@]}" <<'EOF'
apt-get update
apt-get install -y --no-install-recommends ca-certificates curl
curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc -o /usr/share/keyrings/pgdg.asc
curl -fsSL https://packagecloud.io/citusdata/community/gpgkey -o /usr/share/keyrings/citus.asc
echo 'deb [signed-by=/usr/share/keyrings/pgdg.asc] https://apt.postgresql.org/pub/repos/apt resolute-pgdg main 19' > /etc/apt/sources.list.d/pgdg.list
echo 'deb [signed-by=/usr/share/keyrings/citus.asc] https://packagecloud.io/citusdata/community/ubuntu/ resolute main' > /etc/apt/sources.list.d/citus.list
apt-get update
apt-get install -y --no-install-recommends "$@"
IFS=, read -ra versions <<< "$PG_VERSIONS"
for pg in "${versions[@]}"; do
    bindir="/usr/lib/postgresql/$pg/bin"
    datadir="/tmp/verify-pg$pg"
    install -d -o postgres -g postgres "$datadir"
    runuser -u postgres -- "$bindir/initdb" -D "$datadir" -A trust
    preload=""
    if [ "$EXTENSION" = citus ]; then preload="-c shared_preload_libraries=citus"; fi
    runuser -u postgres -- "$bindir/pg_ctl" -D "$datadir" -o "-p 55432 $preload" -w start
    runuser -u postgres -- "$bindir/psql" -p 55432 -v ON_ERROR_STOP=1 \
        -c "CREATE EXTENSION $EXTENSION;" \
        -c "SELECT extname, extversion FROM pg_extension WHERE extname = '$EXTENSION';"
    runuser -u postgres -- "$bindir/pg_ctl" -D "$datadir" -m fast -w stop
done
EOF
