# vim:set ft=dockerfile:
FROM centos:7

# centos:7 is EOL: its mirrorlist is offline, so pin the yum repos to the CentOS
# vault. Required for any `yum` below to resolve when this image is rebuilt.
RUN sed -i -e 's|^mirrorlist=|#mirrorlist=|g' \
           -e 's|^#\?baseurl=http://mirror.centos.org|baseurl=http://vault.centos.org|g' \
           /etc/yum.repos.d/CentOS-*.repo

# FIXME: Hack around docker/docker#10180
RUN ( yum install -y yum-plugin-ovl || yum install -y yum-plugin-ovl ) \
    && yum clean all

# install signing tools
RUN yum install -y expect rpm-sign \
    && yum clean all


RUN echo '%_gpg_name Citus Data <packaging@citusdata.com>' >> /etc/rpm/macros

# Sign with a SHA-256 digest. The default (SHA-1) is rejected by EL9/OL9 crypto-policy
# ("Hash algorithm SHA1 not available" -> Signature BAD), so per-package gpgcheck would
# fail on EL9 even though the package is signed. rpm 4.11 supports SHA-256 for RSA.
RUN echo '%_gpg_digest_algo sha256' >> /etc/rpm/macros

# set PostgreSQL version, place scripts on path, and declare output volume
ENV PATH=/scripts:$PATH
COPY scripts /scripts
VOLUME /packages

ENTRYPOINT ["/scripts/import_and_sign"]
