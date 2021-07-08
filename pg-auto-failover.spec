%global pgmajorversion 11
%global pgpackageversion 11
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname citus

Summary:	PostgreSQL-based distributed RDBMS
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	1.6.1.pg_auto_failover
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/pg_auto_failover/archive/v10.0.3.tar.gz
URL:		https://github.com/citusdata/pg_auto_failover
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
%configure PG_CONFIG=%{pginstdir}/bin/pg_config --with-extra-version="%{?conf_extra_version}" --with-security-flags
make %{?_smp_mflags}

%install
%make_install
# Install documentation with a better name:
%{__mkdir} -p %{buildroot}%{pginstdir}/doc/extension
%{__cp} README.md %{buildroot}%{pginstdir}/doc/extension/README-%{sname}.md
# Set paths to be packaged other than LICENSE, README & CHANGELOG.md
echo %{pginstdir}/include/server/citus_*.h >> installation_files.list
echo %{pginstdir}/include/server/distributed/*.h >> installation_files.list
echo %{pginstdir}/lib/%{sname}.so >> installation_files.list
echo %{pginstdir}/share/extension/%{sname}-*.sql >> installation_files.list
echo %{pginstdir}/share/extension/%{sname}.control >> installation_files.list
%ifarch ppc64 ppc64le
  %else
  %if 0%{?rhel} && 0%{?rhel} <= 6
  %else
    echo %{pginstdir}/lib/bitcode/%{sname}/*.bc >> installation_files.list
    echo %{pginstdir}/lib/bitcode/%{sname}*.bc >> installation_files.list
    echo %{pginstdir}/lib/bitcode/%{sname}/*/*.bc >> installation_files.list
    
    # Columnar does not exist in Citus versions < 10.0
    # At this point, we don't have %{pginstdir},
    # so first check build directory for columnar.
    [[ -d %{buildroot}%{pginstdir}/lib/bitcode/columnar/ ]] && echo %{pginstdir}/lib/bitcode/columnar/*.bc >> installation_files.list
  %endif
%endif

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
* Thu Jul 08 2021 - Gurkan <gindibay@microsoft.com> 1.6.1.-1
- Official 1.6.1 release of Pg_auto_failover

* Fri May 21 2021 - Gurkan Indibay <gindibay@microsoft.com> 1.5.2-1
- Official 1.5.2 release of pg_auto_failover

* Thu Mar 25 2021 - Gurkan Indibay <gindibay@microsoft.com> 1.5.1-1
- Official 1.5.1 release of pg_auto_failover

* Thu Feb 11 2021 - Gurkan Indibay <gindibay@microsoft.com> 1.4.2-2
- Official 1.4.2 release of pg_auto_failover

* Thu Feb 4 2021 - Gurkan Indibay <gindibay@microsoft.com> 1.4.2-1
- Official 1.4.2 release of pg_auto_failover

* Thu Dec 3 2020 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 1.4.1-1
- Official 1.4.1 release of pg_auto_failover

* Wed Sep 23 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 1.4.0-1
- Official 1.4.0 release of pg_auto_failover

* Thu May 7 2020 - Jelte Fennema <Jelte.Fennema@microsoft.com> 1.3.1-1
- Official 1.3.1 release of pg_auto_failover

* Mon Mar 16 2020 - Murat Tuncer <murat.tuncer@microsoft.com> 1.2
- Official release for 1.2

* Wed Feb 12 2020 - Murat Tuncer <murat.tuncer@microsoft.com> 1.0.6
- Official release for 1.0.6

* Fri Sep 20 2019 - Murat Tuncer <murat.tuncer@microsoft.com> 1.0.5
- Official release for 1.0.5

* Thu Sep 5 2019 - Murat Tuncer <murat.tuncer@microsoft.com> 1.0.4
- Official release for 1.0.4

* Tue Jul 30 2019 - Murat Tuncer <murat.tuncer@microsoft.com> 1.0.3
- Official release for 1.0.3

* Thu May 23 2019 - Nils Dijk <nils@citusdata.com> 1.0.2
- Official release for 1.0.2

* Fri May 3 2019 - Nils Dijk <nils@citusdata.com> 1.0.1
- Official release for 1.0.1

* Thu May 2 2019 - Nils Dijk <nils@citusdata.com> 1.0.0
- Official release for 1.0.0
