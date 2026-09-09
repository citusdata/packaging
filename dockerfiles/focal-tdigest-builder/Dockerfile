# vim:set ft=dockerfile:
#
# Builder image for tdigest packages targeting Ubuntu 20.04 (focal). One image
# builds every focal-buildable PostgreSQL major at once (PG 12..16 by default);
# like PostGIS -- and unlike PostgreSQL core -- the tdigest Debian packaging is
# multi-version by design (debian/pgversions + the pgxs_loop debhelper addon
# drive pg_buildext), so a single source build emits postgresql-<major>-tdigest
# for each major in one pass.
#
# Why this exists:
#   apt.postgresql.org (PGDG) no longer ships focal binaries -- focal-pgdg 404s
#   and the frozen apt-archive mirror tops out at tdigest 1.4.3. Anything newer
#   (e.g. 1.4.5 for the memory-safety fixes) has to be rebuilt from upstream
#   source.
#
# Strategy (mirrors dockerfiles/focal-postgis-builder/Dockerfile):
#   - Upstream source: tdigest-<version>.tar.gz from GitHub, sha256-pinned.
#   - Debian packaging: the frozen focal-era debian/ from PGDG's last focal
#     tdigest source package (1.4.3-1.pgdg20.04+1), fetched with `apt-get source`
#     so it is authenticated by the archive's signed Release.
#   - Build tooling restored from the PGDG *archive*, which keeps the removed
#     focal-pgdg suite.
#
# The heavy lifting lives in scripts/build_tdigest_focal (the entrypoint).
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
    # 'main' carries the build tooling and the tdigest source package; each
    # PostgreSQL major is a separate component. tdigest supports PG12+ here and
    # Marlin still ships PG12, so component 12 is listed even though
    # focal-pg-builder omits it.
    echo "deb [signed-by=/usr/share/keyrings/pgdg-archive.gpg] https://apt-archive.postgresql.org/pub/repos/apt focal-pgdg main 12 13 14 15 16" \
      > /etc/apt/sources.list.d/pgdg-archive.list; \
    echo "deb-src [signed-by=/usr/share/keyrings/pgdg-archive.gpg] https://apt-archive.postgresql.org/pub/repos/apt focal-pgdg main 12 13 14 15 16" \
      >> /etc/apt/sources.list.d/pgdg-archive.list; \
    apt-get update; \
    # base build tooling; per-build Build-Depends are resolved at run time by
    # scripts/build_tdigest_focal via mk-build-deps against debian/control.
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
        postgresql-server-dev-all \
        xz-utils; \
    rm -rf /var/lib/apt/lists/*

# Fail the image build early if the archived focal-pgdg debhelper (>= 13) is not
# what we picked up (debhelper-compat (= 13) is required by the packaging).
RUN dpkg-query -W -f='${Package} ${Version}\n' debhelper postgresql-common-dev dh-exec

COPY scripts/build_tdigest_focal /usr/local/bin/build_tdigest_focal
RUN chmod +x /usr/local/bin/build_tdigest_focal

VOLUME /packages
ENTRYPOINT ["/usr/local/bin/build_tdigest_focal"]
