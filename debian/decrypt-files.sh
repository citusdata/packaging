#!/bin/sh

set -eu

pg_version=
libdir="/usr/lib/postgresql/$pg_version/lib"
secret_files_list="$libdir/pgautofailover_secret_files.metadata"

# Make sure the script is being run as root
if [ "$(id -u)" -ne "0" ]; then
    echo "ERROR: pg-auto-failover-enterprise-pg-$pg_version-setup needs to be run as root"
    echo "HINT: try running \"sudo pg-auto-failover-enterprise-pg-$pg_version-setup\" instead"
    exit 1
fi


echo "
Your use of this software is subject to the terms and conditions of the license
agreement by which you acquired this software. If you are a volume license
customer, use of this software is subject to your volume license agreement.
You may not use this software if you have not validly acquired a license for
the software from Microsoft or its licensed distributors.

BY USING THE SOFTWARE, YOU ACCEPT THIS AGREEMENT.
"

CITUS_ACCEPT_LICENSE="${CITUS_ACCEPT_LICENSE:-}"

interactive_license=false
while [ -z "$CITUS_ACCEPT_LICENSE" ]; do
    interactive_license=true
    echo "Do you accept these terms? YES/NO"
    read -r CITUS_ACCEPT_LICENSE
done

case "$CITUS_ACCEPT_LICENSE" in
    YES );;
    y|Y|Yes|yes )
        echo "ERROR: Only YES is accepted (all capital letters)"
        exit 1;
        ;;
    * )
        echo "ERROR: Terms of the software must be accepted"
        exit 1
esac

if [ $interactive_license = false ]; then
    echo "Accepted terms by using CITUS_ACCEPT_LICENSE=YES environment variable"
fi

encryption_disclaimer_text="
Since Citus is a distributed database, data is sent over the network between
nodes. It is YOUR RESPONSIBILITY as an operator to ensure that this traffic is
secure.

Since Citus version 8.1.0 (released 2018-12-17) the traffic between the
different nodes in the cluster is encrypted for NEW installations. This is done
by using TLS with self-signed certificates. This means that this does NOT
protect against Man-In-The-Middle attacks. This only protects against passive
eavesdropping on the network.

This automatic TLS setup of self-signed certificates and TLS is NOT DONE in the
following cases:
1. The Citus clusters was originally created with a Citus version before 8.1.0.
   Even when the cluster is later upgraded to version 8.1.0 or higher. This is
   to make sure partially upgraded clusters continue to work.
2. The ssl Postgres configuration option is already set to 'on'. This indicates
   that the operator has set up their own certificates.

In these cases it is assumed the operator has set up appropriate security
themselves.

So, with the default settings Citus clusters are not safe from
Man-In-The-Middle attacks. To secure the traffic completely you need to follow
the practices outlined here:
https://docs.citusdata.com/en/stable/admin_guide/cluster_management.html#connection-management

Please confirm that you have read this and understand that you should set up
TLS yourself to send traffic between nodes securely:
YES/NO?"

CITUS_ACCEPT_ENCRYPTION_DISCLAIMER="${CITUS_ACCEPT_ENCRYPTION_DISCLAIMER:-}"
while [ -z "$CITUS_ACCEPT_ENCRYPTION_DISCLAIMER" ]; do
    echo "$encryption_disclaimer_text"
    read -r CITUS_ACCEPT_ENCRYPTION_DISCLAIMER
done

case "$CITUS_ACCEPT_ENCRYPTION_DISCLAIMER" in
    YES );;
    y|Y|Yes|yes )
        echo "ERROR: Only YES is accepted (all capital letters)"
        exit 1;
        ;;
    * )
        echo "ERROR: Disclaimer about encrypted traffic must be accepted before installing"
        exit 1
esac

# create a temporary directory for gpg to use so it doesn't output warnings
temp_gnupghome="$(mktemp -d)"
CITUS_LICENSE_KEY="${CITUS_LICENSE_KEY:-}"
while [ -z "$CITUS_LICENSE_KEY" ]; do
    echo ''
    echo 'Please enter license key:'
    read -r CITUS_LICENSE_KEY
done

# Try to decrypt the first file in the list to check if the key is correct
if ! gpg --output "/dev/null" \
        --batch --no-tty --yes --quiet \
        --passphrase "$CITUS_LICENSE_KEY" \
        --homedir "$temp_gnupghome" \
        --decrypt "$(head -n 1 "$secret_files_list").gpg" 2> /dev/null; then
    echo "ERROR: Invalid license key supplied"
    exit 1
fi

echo "License key is valid"
echo "Installing..."

decrypt() {
    path_unencrypted="$1"
    path_encrypted="$path_unencrypted.gpg"
    # decrypt the encrypted file
    gpg --output "$path_unencrypted" \
        --batch --no-tty --yes --quiet \
        --passphrase "$CITUS_LICENSE_KEY" \
        --homedir "$temp_gnupghome" \
        --decrypt "$path_encrypted"

    # restore permissions and ownership
    chmod --reference "$path_encrypted" "$path_unencrypted"
    chown --reference "$path_encrypted" "$path_unencrypted"
}

# Decrypt all the encrypted files
while read -r path_unencrypted; do
    decrypt "$path_unencrypted"
done < "$secret_files_list"

decrypt /opt/pg_autoctl
mv /opt/pg_autoctl /usr/bin/pg_autoctl
chmod +x /usr/bin/pg_autoctl


# remove the temporary gpg directory
rm -rf "$temp_gnupghome"