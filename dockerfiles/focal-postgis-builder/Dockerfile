# vim:set ft=dockerfile:
#
# Builder image for PostGIS packages targeting Ubuntu 20.04 (focal). One image
# builds every focal-buildable PostgreSQL major at once (PG 12..16 by default);
# unlike PostgreSQL core, the PostGIS Debian packaging is multi-version by
# design (debian/pgversions + pg_buildext), so a single source build emits
# postgresql-<major>-postgis-3 for each major in one pass.
#
# Why this exists:
#   apt.postgresql.org (PGDG) no longer ships focal binaries -- focal-pgdg 404s
#   and the frozen apt-archive mirror tops out at PostGIS 3.5.3. Anything newer
#   (e.g. 3.6.x for a CVE fix) has to be rebuilt from upstream source.
#
# Strategy (validated):
#   - Upstream source: postgis-<version>.tar.gz from download.osgeo.org,
#     sha256-pinned.
#   - Debian packaging: the frozen focal-era debian/ from PGDG's last focal
#     postgis source package (3.5.3+dfsg-1~exp1.pgdg20.04+1), fetched with
#     `apt-get source` so it is authenticated by the archive's signed Release.
#   - Build tooling restored from the PGDG *archive*, which keeps the removed
#     focal-pgdg suite.
#
# The heavy lifting lives in scripts/build_postgis_focal (the entrypoint).
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
    # 'main' carries the build tooling; each PostgreSQL major is a separate
    # component. PostGIS 3.6 supports PG12+, and Marlin still ships PG12, so
    # component 12 is listed here even though focal-pg-builder omits it.
    echo "deb [signed-by=/usr/share/keyrings/pgdg-archive.gpg] https://apt-archive.postgresql.org/pub/repos/apt focal-pgdg main 12 13 14 15 16" \
      > /etc/apt/sources.list.d/pgdg-archive.list; \
    echo "deb-src [signed-by=/usr/share/keyrings/pgdg-archive.gpg] https://apt-archive.postgresql.org/pub/repos/apt focal-pgdg main 12 13 14 15 16" \
      >> /etc/apt/sources.list.d/pgdg-archive.list; \
    # 'universe' holds the geo stack (libgeos-dev, libgdal-dev, libsfcgal-dev)
    sed -i 's/^# deb \(.*universe\)/deb \1/' /etc/apt/sources.list; \
    sed -i 's/^# deb-src \(.*\)/deb-src \1/' /etc/apt/sources.list; \
    apt-get update; \
    # base build tooling; per-build Build-Depends are resolved at run time by
    # scripts/build_postgis_focal via mk-build-deps against debian/control.
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

COPY scripts/build_postgis_focal /usr/local/bin/build_postgis_focal
RUN chmod +x /usr/local/bin/build_postgis_focal

VOLUME /packages
ENTRYPOINT ["/usr/local/bin/build_postgis_focal"]
