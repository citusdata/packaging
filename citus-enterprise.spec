%global pgmajorversion 10
%global pgpackageversion 10
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname citus-enterprise

Summary:	PostgreSQL-based distributed RDBMS
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	citus_%{pgmajorversion}
Conflicts:	citus_%{pgmajorversion}
Version:	7.2.2.citus
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:       https://github.com/citusdata/citus-enterprise/archive/v7.2.2.tar.gz
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
%configure PG_CONFIG=%{pginstdir}/bin/pg_config --with-extra-version="%{?conf_extra_version}"
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
%{pginstdir}/lib/citus.so
%{pginstdir}/share/extension/citus-*.sql
%{pginstdir}/share/extension/citus.control

%changelog
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
