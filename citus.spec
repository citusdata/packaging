%global pgmajorversion 96
%global pgpackageversion 9.6
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname citus

Summary:	PostgreSQL-based distributed RDBMS
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	6.2.2.citus
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/citus/archive/v6.2.2.tar.gz
URL:		https://github.com/citusdata/citus
BuildRequires:	postgresql%{pgmajorversion}-devel
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
%configure PG_CONFIG=%{pginstdir}/bin/pg_config
make %{?_smp_mflags}

%install
%make_install
# Install documentation with a better name:
%{__mkdir} -p %{buildroot}%{pginstdir}/doc/extension
%{__cp} README.md %{buildroot}%{pginstdir}/doc/extension/README-%{sname}.md

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc CHANGELOG.md
%if 0%{?rhel} && 0%{?rhel} <= 6
%doc LICENSE
%else
%license LICENSE
%endif
%doc %{pginstdir}/doc/extension/README-%{sname}.md
%{pginstdir}/include/server/citus_*.h
%{pginstdir}/include/server/distributed/*.h
%{pginstdir}/lib/%{sname}.so
%{pginstdir}/share/extension/%{sname}-*.sql
%{pginstdir}/share/extension/%{sname}.control

%changelog
* Wed Jun 7 2017 - Burak Velioglu <velioglub@citusdata.com> 6.2.2.citus-1
- Update to Citus 6.2.2

* Wed May 24 2017 - Jason Petersen <jason@citusdata.com> 6.2.1.citus-1
- Update to Citus 6.2.1

* Tue May 16 2017 - Burak Yucesoy <burak@citusdata.com> 6.2.0.citus-1
- Update to Citus 6.2.0

* Fri May 5 2017 - Metin Doslu <metin@citusdata.com> 6.1.1.citus-1
- Update to Citus 6.1.1

* Thu Feb 9 2017 - Burak Yucesoy <burak@citusdata.com> 6.1.0.citus-1
- Update to Citus 6.1.0

* Wed Feb 8 2017 - Jason Petersen <jason@citusdata.com> 6.0.1.citus-2
- Transitional package to guide users to new package name

* Wed Nov 30 2016 - Burak Yucesoy <burak@citusdata.com> 6.0.1.citus-1
- Update to Citus 6.0.1

* Tue Nov 8 2016 - Jason Petersen <jason@citusdata.com> 6.0.0.citus-1
- Update to Citus 6.0.0

* Tue Nov 8 2016 - Jason Petersen <jason@citusdata.com> 5.2.2.citus-1
- Update to Citus 5.2.2

* Tue Sep 6 2016 - Jason Petersen <jason@citusdata.com> 5.2.1.citus-1
- Update to Citus 5.2.1

* Wed Aug 17 2016 - Jason Petersen <jason@citusdata.com> 5.2.0.citus-1
- Update to Citus 5.2.0

* Mon Aug 1 2016 - Jason Petersen <jason@citusdata.com> 5.2.0-0.1.rc.1
- Release candidate for 5.2

* Fri Jun 17 2016 - Jason Petersen <jason@citusdata.com> 5.1.1-1
- Update to Citus 5.1.1

* Tue May 17 2016 - Jason Petersen <jason@citusdata.com> 5.1.0-1
- Update to Citus 5.1.0

* Mon May 16 2016 - Jason Petersen <jason@citusdata.com> 5.1.0-0.2.rc.2
- Fix EXPLAIN output when FORMAT JSON in use

* Wed May 4 2016 - Jason Petersen <jason@citusdata.com> 5.1.0-0.1.rc.1
- Release candidate for 5.1

* Fri Apr 15 2016 - Jason Petersen <jason@citusdata.com> 5.0.1-1
- Fixes issues on 32-bit systems

* Fri Mar 25 2016 - Devrim Gündüz <devrim@gunduz.org> 5.0.0-1
- Initial RPM packaging for PostgreSQL RPM Repository,
  based on the spec file of Jason Petersen @ Citus.
