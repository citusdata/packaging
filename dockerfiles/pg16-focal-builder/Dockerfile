# vim:set ft=dockerfile:
#
# Builder image for PostgreSQL 16 *core* packages targeting Ubuntu 20.04 (focal).
#
# Why this exists:
#   apt.postgresql.org (PGDG) no longer ships PostgreSQL 16 binaries for focal
#   (focal reached EOL standard support 2025-04; the last official focal build
#   was 16.9-1.pgdg20.04+1). To get a newer 16.x on focal we rebuild the official
#   Debian source package ourselves.
#
# Strategy (validated):
#   - Upstream tarball: postgresql-16_<NEW>.orig.tar.bz2  (e.g. 16.14)
#   - Debian packaging: the focal-era debian/ from 16.9-1.pgdg20.04+1, because its
#     build profile uses focal's *default* toolchain (clang/llvm-dev = LLVM 10),
#     so the resulting JIT depends on focal's libllvm10 (installable on focal),
#     unlike newer packaging which requires clang-19/llvm-19.
#   - Build tooling (debhelper 13, dh-exec, postgresql-common-dev) is restored from
#     the PGDG *archive* (apt-archive.postgresql.org), which keeps the removed
#     focal-pgdg suite.
#
# The heavy lifting lives in scripts/build_pg16_focal (the entrypoint).
FROM ubuntu:20.04
ARG DEBIAN_FRONTEND=noninteractive

# PGDG repository signing key fingerprint:
#   B97B 0AFC AA1A 47F0 44F2  44A0 7FCC 7D46 ACCC 4CF8
RUN set -ex; \
    apt-get update; \
    apt-get install -y --no-install-recommends ca-certificates curl gnupg; \
    install -d /usr/share/keyrings; \
    curl -fsSL https://www.postgresql.org/media/keys/ACCC4CF8.asc \
      | gpg --dearmor -o /usr/share/keyrings/pgdg-archive.gpg; \
    echo "deb [signed-by=/usr/share/keyrings/pgdg-archive.gpg] https://apt-archive.postgresql.org/pub/repos/apt focal-pgdg main 16" \
      > /etc/apt/sources.list.d/pgdg-archive.list; \
    # make sure 'universe' is enabled (clang / llvm-dev live there on focal)
    sed -i 's/^# deb \(.*universe\)/deb \1/' /etc/apt/sources.list; \
    apt-get update; \
    # base build tooling; the per-build Build-Depends are resolved at run time
    # by scripts/build_pg16_focal via mk-build-deps against debian/control.
    apt-get install -y --no-install-recommends \
        build-essential \
        devscripts \
        equivs \
        fakeroot \
        quilt \
        dpkg-dev \
        debhelper \
        dh-exec \
        postgresql-common-dev \
        xz-utils \
        bzip2; \
    rm -rf /var/lib/apt/lists/*

# Fail the image build early if the archived focal-pgdg debhelper (>= 13) is not
# what we picked up (debhelper-compat (= 13) is required by the packaging).
RUN dpkg-query -W -f='${Package} ${Version}\n' debhelper postgresql-common-dev dh-exec

COPY scripts/build_pg16_focal /usr/local/bin/build_pg16_focal
RUN chmod +x /usr/local/bin/build_pg16_focal

VOLUME /packages
ENTRYPOINT ["/usr/local/bin/build_pg16_focal"]
