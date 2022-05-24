%global pgmajorversion 11
%global pgpackageversion 11
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname citus-enterprise
%global pname citus
%global debug_package %{nil}
%global unencrypted_package "%{getenv:UNENCRYPTED_PACKAGE}"

Summary:	PostgreSQL-based distributed RDBMS
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	citus_%{pgmajorversion}
Conflicts:	citus_%{pgmajorversion}
Version:	10.2.6.citus
Release:	1%{dist}
License:	Commercial
Group:		Applications/Databases
Source0:	https://github.com/citusdata/citus-enterprise/archive/v10.2.6.tar.gz
URL:		https://github.com/citusdata/citus-enterprise
BuildRequires:	postgresql%{pgmajorversion}-devel libcurl-devel
Requires:	postgresql%{pgmajorversion}-server
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
Citus horizontally scales PostgreSQL across commodity servers
using sharding and replication. Its query engine parallelizes
incoming SQL queries across these servers to enable real-time
responses on large datasets.

Citus extends the underlying database rather than forking it,
which gives developers and enterprises the power and familiarity
of a traditional relational database. As an extension, Citus
supports new PostgreSQL releases, allowing users to benefit from
new features while maintaining compatibility with existing
PostgreSQL tools. Note that Citus supports many (but not all) SQL
commands.

%prep
%setup -q -n %{sname}-%{version}

%build

currentgccver="$(gcc -dumpversion)"
requiredgccver="4.8.2"
if [ "$(printf '%s\n' "$requiredgccver" "$currentgccver" | sort -V | head -n1)" != "$requiredgccver" ]; then
    echo ERROR: At least GCC version "$requiredgccver" is needed to build with security flags
    exit 1
fi

%configure PG_CONFIG=%{pginstdir}/bin/pg_config --with-extra-version="%{?conf_extra_version}" --with-security-flags CC=$(command -v gcc)
make %{?_smp_mflags}

%install
%make_install
# Install documentation with a better name:
%{__mkdir} -p %{buildroot}%{pginstdir}/doc/extension
%{__cp} README.md %{buildroot}%{pginstdir}/doc/extension/README-%{sname}.md
# Set paths to be packaged other than LICENSE, README & CHANGELOG.md
echo %{pginstdir}/include/server/citus_*.h >> installation_files.list
echo %{pginstdir}/include/server/distributed/*.h >> installation_files.list
echo %{pginstdir}/share/extension/citus-*.sql >> installation_files.list
[[ -f %{buildroot}%{pginstdir}/bin/pg_send_cancellation ]] && echo %{pginstdir}/bin/pg_send_cancellation >> installation_files.list
%if %{unencrypted_package} != ""
  echo %{pginstdir}/lib/citus.so >> installation_files.list
  [[ -f %{buildroot}%{pginstdir}/lib/citus_columnar.so ]] && echo %{pginstdir}/lib/citus_columnar.so >> installation_files.list
  echo %{pginstdir}/share/extension/citus.control >> installation_files.list
  %ifarch ppc64 ppc64le
    %else
    %if 0%{?rhel} && 0%{?rhel} <= 6
    %else
      echo %{pginstdir}/lib/bitcode/%{pname}*.bc >> installation_files.list
      echo %{pginstdir}/lib/bitcode/%{pname}/*.bc >> installation_files.list
      echo %{pginstdir}/lib/bitcode/%{pname}/*/*.bc >> installation_files.list

      # Columnar does not exist in Citus versions < 10.0
      # At this point, we don't have %{pginstdir},
      # so first check build directory for columnar.
      [[ -d %{buildroot}%{pginstdir}/lib/bitcode/columnar/ ]] && echo %{pginstdir}/lib/bitcode/columnar/*.bc >> installation_files.list
      [[ -d %{buildroot}%{pginstdir}/lib/bitcode/citus_columnar/ ]] && echo %{pginstdir}/lib/bitcode/citus_columnar/*.bc >> installation_files.list
      [[ -d %{buildroot}%{pginstdir}/lib/bitcode/citus_columnar/safeclib ]] && echo %{pginstdir}/lib/bitcode/citus_columnar/safeclib/*.bc >> installation_files.list
    %endif
  %endif
%else
  echo /usr/bin/citus-enterprise-pg-%{pgmajorversion}-setup >> installation_files.list
  echo %{pginstdir}/lib/citus_secret_files.metadata >> installation_files.list
  echo %{pginstdir}/lib/citus.so.gpg >> installation_files.list
  echo %{pginstdir}/share/extension/citus.control.gpg >> installation_files.list
  %ifarch ppc64 ppc64le
    %else
    %if 0%{?rhel} && 0%{?rhel} <= 6
    %else
      echo %{pginstdir}/lib/bitcode/%{pname}*.bc.gpg >> installation_files.list
      echo %{pginstdir}/lib/bitcode/%{pname}/*.bc.gpg >> installation_files.list
      echo %{pginstdir}/lib/bitcode/%{pname}/*/*.bc.gpg >> installation_files.list

      # Columnar does not exist in Citus versions < 10.0
      # At this point, we don't have %{pginstdir},
      # so first check build directory for columnar.
      [[ -d %{buildroot}%{pginstdir}/lib/bitcode/columnar/ ]] && echo %{pginstdir}/lib/bitcode/columnar/*.bc.gpg >> installation_files.list
      [[ -d %{buildroot}%{pginstdir}/lib/bitcode/citus_columnar/ ]] && echo %{pginstdir}/lib/bitcode/citus_columnar/*.bc.gpg >> installation_files.list
    %endif
  %endif
%endif
%if %{unencrypted_package} == ""

set -eu
set +x

dir="%{buildroot}"
libdir="$dir/%{pginstdir}/lib"
mkdir -p "$libdir"

# List all files to be encrypted and store it in the libdir as secret_files_list
secret_files_list="$libdir/citus_secret_files.metadata"
find "$dir" -iname "*.so" -o -iname "*.bc" -o -iname "*.control" | sed -e "s@^$dir@@g" > "$secret_files_list"

PACKAGE_ENCRYPTION_KEY="${PACKAGE_ENCRYPTION_KEY:-}"
if [ -z "$PACKAGE_ENCRYPTION_KEY" ]; then
    echo "ERROR: The PACKAGE_ENCRYPTION_KEY environment variable needs to be set"
    echo "HINT: If trying to build packages locally, just set it to 'abc' or something"
    echo "HINT: If you're trying to build unencrypted packages you should set the UNENCRYPTED_PACKAGE environment variable"
    exit 1
fi

# create a temporary directory for gpg to use so it doesn't output warnings
temp_gnupghome="$(mktemp -d)"
while read -r unencrypted_file; do
    path_unencrypted="$dir$unencrypted_file"
    path_encrypted="$path_unencrypted.gpg"

    # encrypt the files using password
    # --s2k-* options are there to make sure decrypting/encrypting doesn't
    # take minutes
    gpg --symmetric \
        --batch \
        --no-tty \
        --yes \
        --cipher-algo AES256 \
        --s2k-mode 3 \
        --s2k-count 1000000 \
        --s2k-digest-algo SHA512 \
        --passphrase-fd 0 \
        --homedir "$temp_gnupghome" \
        --output "$path_encrypted" \
        "$path_unencrypted" \
        <<< "$PACKAGE_ENCRYPTION_KEY"

    # keep permissions and ownership the same, so we can restore it later
    # when decrypting
    chmod --reference "$path_unencrypted" "$path_encrypted"
    chown --reference "$path_unencrypted" "$path_encrypted"

    # remove the unencrypted file from the package
    rm "$path_unencrypted"
done < "$secret_files_list"

# remove the temporary gpg directory
rm -rf "$temp_gnupghome"


bindir="$dir/usr/bin"
mkdir -p "$bindir"


#------- START OF DECRYPT SCRIPT --------
# Create file used to decrypt
cat > "$bindir/citus-enterprise-pg-%{pgmajorversion}-setup" << EOF
#!/bin/sh

set -eu

pg_version=%{pgmajorversion}
libdir="%{pginstdir}/lib"
secret_files_list="\$libdir/citus_secret_files.metadata"

# Make sure the script is being run as root
if [ "\$(id -u)" -ne "0" ]; then
    echo "ERROR: citus-enterprise-pg-\$pg_version-setup needs to be run as root"
    echo "HINT: try running \"sudo citus-enterprise-pg-\$pg_version-setup\" instead"
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

CITUS_ACCEPT_LICENSE="\${CITUS_ACCEPT_LICENSE:-}"

interactive_license=false
while [ -z "\$CITUS_ACCEPT_LICENSE" ]; do
    interactive_license=true
    echo "Do you accept these terms? YES/NO"
    read -r CITUS_ACCEPT_LICENSE
done

case "\$CITUS_ACCEPT_LICENSE" in
    YES );;
    y|Y|Yes|yes )
        echo "ERROR: Only YES is accepted (all capital letters)"
        exit 1;
        ;;
    * )
        echo "ERROR: Terms of the software must be accepted"
        exit 1
esac

if [ \$interactive_license = false ]; then
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

CITUS_ACCEPT_ENCRYPTION_DISCLAIMER="\${CITUS_ACCEPT_ENCRYPTION_DISCLAIMER:-}"
while [ -z "\$CITUS_ACCEPT_ENCRYPTION_DISCLAIMER" ]; do
    echo "\$encryption_disclaimer_text"
    read -r CITUS_ACCEPT_ENCRYPTION_DISCLAIMER
done

case "\$CITUS_ACCEPT_ENCRYPTION_DISCLAIMER" in
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
temp_gnupghome="\$(mktemp -d)"
CITUS_LICENSE_KEY="\${CITUS_LICENSE_KEY:-}"
while [ -z "\$CITUS_LICENSE_KEY" ]; do
    echo ''
    echo 'Please enter license key:'
    read -r CITUS_LICENSE_KEY
done

# Try to decrypt the first file in the list to check if the key is correct
if ! gpg --output "/dev/null" \
        --batch --no-tty --yes --quiet \
        --passphrase "\$CITUS_LICENSE_KEY" \
        --homedir "\$temp_gnupghome" \
        --decrypt "\$(head -n 1 "\$secret_files_list").gpg" 2> /dev/null; then
    echo "ERROR: Invalid license key supplied"
    exit 1
fi

echo "License key is valid"
echo "Installing..."

# Decrypt all the encrypted files
while read -r path_unencrypted; do
    path_encrypted="\$path_unencrypted.gpg"
    # decrypt the encrypted file
    gpg --output "\$path_unencrypted" \
        --batch --no-tty --yes --quiet \
        --passphrase "\$CITUS_LICENSE_KEY" \
        --homedir "\$temp_gnupghome" \
        --decrypt "\$path_encrypted"

    # restore permissions and ownership
    chmod --reference "\$path_encrypted" "\$path_unencrypted"
    chown --reference "\$path_encrypted" "\$path_unencrypted"
done < "\$secret_files_list"

# remove the temporary gpg directory
rm -rf "\$temp_gnupghome"
EOF

#------- END OF DECRYPT SCRIPT --------

chmod +x "$bindir/citus-enterprise-pg-%{pgmajorversion}-setup"

cat "$bindir/citus-enterprise-pg-%{pgmajorversion}-setup"



%post
installation_message="
+--------------------------------------------------------------+
Please run 'sudo citus-enterprise-pg-%{pgmajorversion}-setup'
to complete the setup of Citus Enterprise
+--------------------------------------------------------------+
"
echo "$installation_message"


%preun
libdir="%{pginstdir}/lib"

secret_files_list="$libdir/citus_secret_files.metadata"

# Cleanup all de decrypted files since these are not managed by the package
# manager and would be left around otherwise
while read -r path_unencrypted; do
    rm -f "$path_unencrypted"
done < "$secret_files_list"

%endif # encrypted packages code

%clean
%{__rm} -rf %{buildroot}

%files -f installation_files.list
%files
%defattr(-,root,root,-)
%doc CHANGELOG.md
%if 0%{?rhel} && 0%{?rhel} <= 6
%doc LICENSE
%else
%license LICENSE
%endif
%doc %{pginstdir}/doc/extension/README-%{sname}.md

%changelog
* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 10.2.6.citus-1
- Official 10.2.6 release of Citus Enterprise

* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 8.3.4.citus-1
- Official 8.3.4 release of Citus Enterprise

* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 9.0.3.citus-1
- Official 9.0.3 release of Citus Enterprise

* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 9.1.3.citus-1
- Official 9.1.3 release of Citus Enterprise

* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 9.2.9.citus-1
- Official 9.2.9 release of Citus Enterprise

* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 9.3.6.citus-1
- Official 9.3.6 release of Citus Enterprise

* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 9.4.7.citus-1
- Official 9.4.7 release of Citus Enterprise

* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 9.5.11.citus-1
- Official 9.5.11 release of Citus Enterprise

* Mon May 23 2022 - Gurkan Indibay <gindibay@microsoft.com> 10.0.7.citus-1
- Official 10.0.7 release of Citus Enterprise

* Fri May 20 2022 - Gurkan Indibay <gindibay@microsoft.com> 10.1.5.citus-1
- Official 10.1.5 release of Citus Enterprise

* Mon Apr 11 2022 - Gurkan Indibay <gindibay@microsoft.com> 11.0.1_beta.citus-1
- Official 11.0.1_beta release of Citus Enterprise

* Thu Mar 17 2022 - Gurkan Indibay <gindibay@microsoft.com> 10.2.5.citus-1
- Official 10.2.5 release of Citus Enterprise

* Tue Feb 01 2022 - Gurkan Indibay <gindibay@microsoft.com> 10.2.4.citus-1
- Official 10.2.4 release of Citus Enterprise

* Tue Feb 01 2022 - Gurkan Indibay <gindibay@microsoft.com> 10.1.4.citus-1
- Official 10.1.4 release of Citus Enterprise

* Mon Nov 29 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.2.3.citus-1
- Official 10.2.3 release of Citus Enterprise

* Fri Nov 12 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.6.citus-1
- Official 10.0.6 release of Citus Enterprise

* Mon Nov 08 2021 - Gurkan Indibay <gindibay@microsoft.com> 9.5.10.citus-1
- Official 9.5.10 release of Citus Enterprise

* Thu Nov 04 2021 - Gurkan Indibay <gindibay@microsoft.com> 9.2.8.citus-1
- Official 9.2.8 release of Citus Enterprise

* Thu Oct 14 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.2.2.citus-1
- Official 10.2.2 release of Citus Enterprise

* Fri Sep 24 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.2.1.citus-1
- Official 10.2.1 release of Citus Enterprise

* Fri Sep 17 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.1.3.citus-1
- Official 10.1.3 release of Citus Enterprise

* Thu Sep 16 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.2.0.citus-2
- Removes encryption from packages

* Wed Sep 15 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.2.0.citus-1
- Official 10.2.0 release of Citus Enterprise

* Wed Aug 18 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.1.2.citus-1
- Official 10.1.2 release of Citus Enterprise

* Tue Aug 17 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.5.citus-1
- Official 10.0.5 release of Citus Enterprise

* Tue Aug 17 2021 - Gurkan Indibay <gindibay@microsoft.com> 9.5.7.citus-1
- Official 9.5.7 release of Citus Enterprise

* Tue Aug 17 2021 - Gurkan Indibay <gindibay@microsoft.com> 9.4.6.citus-1
- Official 9.4.6 release of Citus Enterprise

* Fri Aug 06 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.1.1.citus-1
- Official 10.1.1 release of Citus Enterprise

* Fri Jul 16 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.4.citus-1
- Official 10.0.4 release of Citus Enterprise

* Mon Jul 12 2021 - Gurkan <gindibay@microsoft.com> 9.5.6.citus-1
- Official 9.5.6 release of Citus-enterprise

* Fri Jul 09 2021 - Gurkan <gindibay@microsoft.com> 9.4.5.citus-1
- Official 9.4.5 release of Citus-enterprise

* Thu Mar 18 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.3.citus-1
- Official 10.0.3 release of Citus Enterprise

* Thu Mar 4 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.2.citus-1
- Official 10.0.2 release of Citus Enterprise

* Fri Feb 19 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.1.citus-1
- Official 10.0.1 release of Citus Enterprise

* Tue Feb 16 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.0.citus-1
- Official 10.0.0 release of Citus Enterprise

* Thu Jan 28 2021 - Gurkan Indibay <gindibay@microsoft.com> 9.5.2.citus-1
- Official 9.5.2 release of Citus Enterprise

* Wed Jan 6 2021 - gurkanindibay <gindibay@microsoft.com> 9.4.4.citus-1
- Official 9.4.4 release of Citus Enterprise

* Wed Dec 2 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.5.1.citus-1
- Official 9.5.1 release of Citus Enterprise

* Tue Nov 24 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.4.3.citus-1
- Official 9.4.3 release of Citus Enterprise

* Thu Oct 22 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.4.2.citus-1
- Official 9.4.2 release of Citus Enterprise

* Wed Sep 30 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.4.1.citus-1
- Official 9.4.1 release of Citus Enterprise

* Wed Aug 19 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.4.0.citus-1
- Official 9.4.0 release of Citus Enterprise

* Mon Jul 27 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.3.5.citus-1
- Official 9.3.5 release of Citus Enterprise

* Mon Jul 13 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.3.3.citus-1
- Official 9.3.3 release of Citus Enterprise

* Wed May 27 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.3.0.citus-1
- Official 9.3.0 release of Citus Enterprise

* Tue Mar 31 2020 - Jelte Fennema <Jelte.Fennema@microsoft.com> 9.2.4.citus-1
- Update to Citus Enterprise 9.2.4

* Wed Mar 25 2020 - Jelte Fennema <Jelte.Fennema@microsoft.com> 9.2.3.citus-1
- Update to Citus Enterprise 9.2.3

* Fri Mar 6 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.0.2.citus-1
- Update to Citus Enterprise 9.0.2

* Fri Mar 6 2020 - Onur Tirtir <ontirtir@microsoft.com> 9.2.2.citus-1
- Update to Citus Enterprise 9.2.2

* Fri Feb 14 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.2.1.citus-1
- Update to Citus Enterprise 9.2.1

* Tue Feb 11 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.2.0.citus-1
- Update to Citus Enterprise 9.2.0

* Fri Dec 20 2019 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.1.1.citus-1
- Update to Citus Enterprise 9.1.1

* Wed Oct 30 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 9.0.1.citus-1
- Update to Citus Enterprise 9.0.1

* Fri Oct 18 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 9.0.0.citus-1
- Update to Citus Enterprise 9.0.0

* Fri Aug 9 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 8.3.2.citus-1
- Update to Citus Enterprise 8.3.2

* Tue Jul 30 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 8.3.1.citus-1
- Update to Citus Enterprise 8.3.1

* Thu Jul 11 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 8.3.0.citus-1
- Update to Citus Enterprise 8.3.0

* Thu Jun 13 2019 - Burak Velioglu <velioglub@citusdata.com> 8.2.2.citus-1
- Update to Citus Enterprise 8.2.2

* Thu Apr 4 2019 - Burak Velioglu <velioglub@citusdata.com> 8.1.2.citus-1
- Update to Citus Enterprise 8.1.2

* Thu Apr 4 2019 - Burak Velioglu <velioglub@citusdata.com> 8.2.1.citus-1
- Update to Citus Enterprise 8.2.1

* Fri Mar 29 2019 - Burak Velioglu <velioglub@citusdata.com> 8.2.0.citus-1
- Update to Citus Enterprise 8.2.0

* Thu Jan 10 2019 - Burak Velioglu <velioglub@citusdata.com> 8.0.3.citus-1
- Update to Citus Enterprise 8.0.3

* Tue Jan 8 2019 - Burak Velioglu <velioglub@citusdata.com> 8.1.1.citus-1
- Update to Citus Enterprise 8.1.1

* Thu Dec 20 2018 - Burak Velioglu <velioglub@citusdata.com> 8.1.0.citus-1
- Update to Citus Enterprise 8.1.0

* Fri Dec 14 2018 - Burak Velioglu <velioglub@citusdata.com> 8.0.2.citus-1
- Update to Citus Enterprise 8.0.2

* Thu Dec 13 2018 - Burak Velioglu <velioglub@citusdata.com> 7.5.4.citus-1
- Update to Citus Enterprise 7.5.4

* Wed Nov 28 2018 - Burak Velioglu <velioglub@citusdata.com> 8.0.1.citus-1
- Update to Citus Enterprise 8.0.1

* Tue Nov 27 2018 - Burak Velioglu <velioglub@citusdata.com> 7.5.3.citus-1
- Update to Citus Enterprise 7.5.3

* Thu Nov 15 2018 - Burak Velioglu <velioglub@citusdata.com> 7.5.2.citus-1
- Update to Citus Enterprise 7.5.2

* Tue Nov 6 2018 - Burak Velioglu <velioglub@citusdata.com> 8.0.0.citus-1
- Update to Citus Enterprise 8.0.0

* Wed Aug 29 2018 - Burak Velioglu <velioglub@citusdata.com> 7.5.1.citus-1
- Update to Citus Enterprise 7.5.1

* Fri Jul 27 2018 - Mehmet Furkan Sahin <furkan@citusdata.com> 7.4.2.citus-1
- Update to Citus 7.4.2

* Wed Jul 25 2018 - Mehmet Furkan Sahin <furkan@citusdata.com> 7.5.0.citus-1
- Update to Citus 7.5.0

* Thu Jun 21 2018 - Burak Velioglu <velioglub@citusdata.com> 7.4.1.citus-1
- Update to Citus Enterprise 7.4.1

* Thu May 17 2018 - Burak Velioglu <velioglub@citusdata.com> 7.2.2.citus-1
- Update to Citus Enterprise 7.2.2

* Wed May 16 2018 - Burak Velioglu <velioglub@citusdata.com> 7.4.0.citus-1
- Update to Citus Enterprise 7.4.0

* Fri Mar 16 2018 - Burak Velioglu <velioglub@citusdata.com> 7.3.0.citus-1
- Update to Citus Enterprise 7.3.0

* Wed Feb 7 2018 - Burak Velioglu <velioglub@citusdata.com> 7.2.1.citus-1
- Update to Citus Enterprise 7.2.1

* Thu Jan 18 2018 - Burak Velioglu <velioglub@citusdata.com> 7.2.0.citus-1
- Update to Citus Enterprise 7.2.0

* Fri Jan 12 2018 - Burak Velioglu <velioglub@citusdata.com> 6.2.5.citus-1
- Update to Citus Enterprise 6.2.5

* Fri Jan 05 2018 - Burak Velioglu <velioglub@citusdata.com> 7.1.2.citus-1
- Update to Citus Enterprise 7.1.2

* Tue Dec 05 2017 - Burak Velioglu <velioglub@citusdata.com> 7.1.1.citus-1
- Update to Citus Enterprise 7.1.1

* Tue Nov 14 2017 - Burak Velioglu <velioglu@citusdata.com> 7.1.0.citus-1
- Update to Citus Enterprise 7.1.0

* Mon Oct 16 2017 - Burak Yucesoy <burak@citusdata.com> 7.0.3.citus-1
- Update to Citus Enterprise 7.0.3

* Thu Sep 28 2017 - Burak Yucesoy <burak@citusdata.com> 7.0.2.citus-1
- Update to Citus Enterprise 7.0.2

* Thu Sep 28 2017 - Burak Yucesoy <burak@citusdata.com> 6.2.4.citus-1
- Update to Citus Enterprise 6.2.4

* Thu Sep 28 2017 - Burak Yucesoy <burak@citusdata.com> 6.1.3.citus-1
- Update to Citus Enterprise 6.1.3

* Tue Sep 12 2017 - Burak Yucesoy <burak@citusdata.com> 7.0.1.citus-1
- Update to Citus Enterprise 7.0.1

* Wed Aug 30 2017 - Burak Yucesoy <burak@citusdata.com> 7.0.0.citus-1
- Update to Citus Enterprise 7.0.0

* Thu Jul 13 2017 - Burak Yucesoy <burak@citusdata.com> 6.2.3.citus-1
- Update to Citus Enterprise 6.2.3

* Thu Jun 8 2017 - Burak Velioglu <velioglub@citusdata.com> 6.2.2.citus-1
- Update to Citus Enterprise 6.2.2

* Wed May 31 2017 - Jason Petersen <jason@citusdata.com> 6.1.2.citus-1
- Update to Citus Enterprise 6.1.2

* Wed May 24 2017 - Jason Petersen <jason@citusdata.com> 6.2.1.citus-1
- Update to Citus Enterprise 6.2.1

* Wed May 17 2017 - Jason Petersen <jason@citusdata.com> 6.2.0.citus-1
- Update to Citus Enterprise 6.2.0

* Wed May 10 2017 - Metin Doslu <metin@citusdata.com> 6.1.1.citus-1
- Update to Citus Enterprise 6.1.1

* Fri Feb 10 2017 - Jason Petersen <jason@citusdata.com> 6.1.0.citus-1
- Update to Citus Enterprise 6.1.0

* Fri Feb 10 2017 - Burak Yucesoy <burak@citusdata.com> 6.0.1.citus-2
- Transitional package to guide users to new package name

* Wed Nov 30 2016 - Burak Yucesoy <burak@citusdata.com> 6.0.1.citus-1
- Update to Citus Enterprise 6.0.1

* Tue Nov 8 2016 - Jason Petersen <jason@citusdata.com> 6.0.0.citus-1
- Update to Citus Enterprise 6.0.0

* Tue Nov 8 2016 - Jason Petersen <jason@citusdata.com> 5.2.2.citus-1
- Update to Citus Enterprise 5.2.2

* Tue Sep 20 2016 - Jason Petersen <jason@citusdata.com> 5.2.1.citus-1
- Update to Citus Enterprise 5.2.1

* Thu Aug 18 2016 - Jason Petersen <jason@citusdata.com> 5.2.0.citus-1
- Update to Citus Enterprise 5.2.0

* Mon Aug 1 2016 - Jason Petersen <jason@citusdata.com> 5.2.0-0.1.rc.1
- Release candidate for 5.2.

* Fri Jun 17 2016 - Jason Petersen <jason@citusdata.com> 5.1.1-1
- Update to Citus Enterprise 5.1.1

* Tue May 17 2016 - Jason Petersen <jason@citusdata.com> 5.1.0-1
- Update to Citus Enterprise 5.1.0

* Tue May 10 2016 - Jason Petersen <jason@citusdata.com> 5.1.0-0.1.rc.1
- Release candidate for 5.1.
