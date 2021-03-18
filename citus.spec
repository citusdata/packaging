%global pgmajorversion 11
%global pgpackageversion 11
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname citus

Summary:	PostgreSQL-based distributed RDBMS
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	10.0.3.citus
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/citus/archive/v10.0.3.tar.gz
URL:		https://github.com/citusdata/citus
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
* Thu Mar 18 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.3.citus-1
- Official 10.0.3 release of Citus

* Thu Mar 4 2021 - Gurkan Indibay <gindibay@microsoft.com> 10.0.2.citus-1
- Official 10.0.2 release of Citus

* Wed Jan 27 2021 - gurkanindibay <gindibay@microsoft.com> 9.5.2.citus-1
- Official 9.5.2 release of Citus

* Tue Jan 5 2021 - gurkanindibay <gindibay@microsoft.com> 9.4.4.citus-1
- Official 9.4.4 release of Citus

* Wed Dec 2 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.5.1.citus-1
- Official 9.5.1 release of Citus

* Tue Nov 24 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.4.3.citus-1
- Official 9.4.3 release of Citus

* Wed Nov 11 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.5.0.citus-1
- Official 9.5.0 release of Citus

* Thu Oct 22 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.4.2.citus-1
- Official 9.4.2 release of Citus

* Wed Sep 30 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.4.1.citus-1
- Official 9.4.1 release of Citus

* Tue Jul 28 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.4.0.citus-1
- Official 9.4.0 release of Citus

* Mon Jul 27 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.3.5.citus-1
- Official 9.3.5 release of Citus

* Wed Jul 22 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.3.4.citus-1
- Official 9.3.4 release of Citus

* Mon Jul 13 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.3.3.citus-1
- Official 9.3.3 release of Citus

* Thu May 7 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.3.0.citus-1
- Update to Citus 9.3.0

* Tue Mar 31 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.2.4.citus-1
- Update to Citus 9.2.4

* Thu Mar 26 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.2.3.citus-1
- Update to Citus 9.2.3

* Fri Mar 6 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> 9.0.2.citus-1
- Update to Citus 9.0.2

* Fri Mar 6 2020 - Onur Tirtir <ontirtir@microsoft.com> 9.2.2.citus-1
- Update to Citus 9.2.2

* Fri Feb 14 2020 - Onur Tirtir <ontirtir@microsoft.com> 9.2.1.citus-1
- Update to Citus 9.2.1

* Mon Feb 10 2020 - Onur Tirtir <ontirtir@microsoft.com> 9.2.0.citus-1
- Update to Citus 9.2.0

* Wed Dec 18 2019 - Onur Tirtir <ontirtir@microsoft.com> 9.1.1.citus-1
- Update to Citus 9.1.1

* Thu Nov 28 2019 - Onur Tirtir <ontirtir@microsoft.com> 9.1.0.citus-1
- Update to Citus 9.1.0

* Wed Oct 30 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 9.0.1.citus-1
- Update to Citus 9.0.1

* Thu Oct 10 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 9.0.0.citus-1
- Update to Citus 9.0.0

* Fri Aug 9 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 8.3.2.citus-1
- Update to Citus 8.3.2

* Mon Jul 29 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 8.3.1.citus-1
- Update to Citus 8.3.1

* Wed Jul 10 2019 - Burak Velioglu <velioglub@citusdata.com> 8.3.0.citus-1
- Update to Citus 8.3.0

* Wed Jun 12 2019 - Burak Velioglu <velioglub@citusdata.com> 8.2.2.citus-1
- Update to Citus 8.2.2

* Wed Apr 3 2019 - Burak Velioglu <velioglub@citusdata.com> 8.2.1.citus-1
- Update to Citus 8.2.1

* Wed Apr 3 2019 - Burak Velioglu <velioglub@citusdata.com> 8.1.2.citus-1
- Update to Citus 8.1.2

* Thu Mar 28 2019 - Burak Velioglu <velioglub@citusdata.com> 8.2.0.citus-1
- Update to Citus 8.2.0

* Wed Jan 9 2019 - Burak Velioglu <velioglub@citusdata.com> 8.0.3.citus-1
- Update to Citus 8.0.3

* Mon Jan 7 2019 - Burak Velioglu <velioglub@citusdata.com> 8.1.1.citus-1
- Update to Citus 8.1.1

* Tue Dec 18 2018 - Burak Velioglu <velioglub@citusdata.com> 8.1.0.citus-1
- Update to Citus 8.1.0

* Thu Dec 13 2018 - Burak Velioglu <velioglub@citusdata.com> 8.0.2.citus-1
- Update to Citus 8.0.2

* Wed Dec 12 2018 - Burak Velioglu <velioglub@citusdata.com> 7.5.4.citus-1
- Update to Citus 7.5.4

* Wed Nov 28 2018 - Burak Velioglu <velioglub@citusdata.com> 8.0.1.citus-1
- Update to Citus 8.0.1

* Wed Nov 28 2018 - Burak Velioglu <velioglub@citusdata.com> 7.5.3.citus-1
- Update to Citus 7.5.3

* Wed Nov 14 2018 - Burak Velioglu <velioglub@citusdata.com> 7.5.2.citus-1
- Update to Citus 7.5.2

* Fri Nov 02 2018 - Burak Velioglu <velioglub@citusdata.com> 8.0.0.citus-1
- Update to Citus 8.0.0

* Wed Aug 29 2018 - Burak Velioglu <velioglub@citusdata.com> 7.5.1.citus-1
- Update to Citus 7.5.1

* Fri Jul 27 2018 - Mehmet Furkan Sahin <furkan@citusdata.com> 7.4.2.citus-1
- Update to Citus 7.4.2

* Wed Jul 25 2018 - Mehmet Furkan Sahin <furkan@citusdata.com> 7.5.0.citus-1
- Update to Citus 7.5.0

* Wed Jun 20 2018 - Burak Velioglu <velioglub@citusdata.com> 7.4.1.citus-1
- Update to Citus 7.4.1

* Thu May 17 2018 - Burak Velioglu <velioglub@citusdata.com> 7.2.2.citus-1
- Update to Citus 7.2.2

* Tue May 15 2018 - Burak Velioglu <velioglub@citusdata.com> 7.4.0.citus-1
- Update to Citus 7.4.0

* Thu Mar 15 2018 - Burak Velioglu <velioglub@citusdata.com> 7.3.0.citus-1
- Update to Citus 7.3.0

* Tue Feb 6 2018 - Burak Velioglu <velioglub@citusdata.com> 7.2.1.citus-1
- Update to Citus 7.2.1

* Tue Jan 16 2018 - Burak Velioglu <velioglub@citusdata.com> 7.2.0.citus-1
- Update to Citus 7.2.0

* Thu Jan 11 2018 - Burak Velioglu <velioglub@citusdata.com> 6.2.5.citus-1
- Update to Citus 6.2.5

* Fri Jan 05 2018 - Burak Velioglu <velioglub@citusdata.com> 7.1.2.citus-1
- Update to Citus 7.1.2

* Tue Dec 05 2017 - Burak Velioglu <velioglub@citusdata.com> 7.1.1.citus-1
- Update to Citus 7.1.1

* Wed Nov 15 2017 - Burak Velioglu <velioglub@citusdata.com> 7.1.0.citus-1
- Update to Citus 7.1.0

* Mon Oct 16 2017 - Burak Yucesoy <burak@citusdata.com> 7.0.3.citus-1
- Update to Citus 7.0.3

* Thu Sep 28 2017 - Burak Yucesoy <burak@citusdata.com> 7.0.2.citus-1
- Update to Citus 7.0.2

* Thu Sep 28 2017 - Burak Yucesoy <burak@citusdata.com> 6.2.4.citus-1
- Update to Citus 6.2.4

* Thu Sep 28 2017 - Burak Yucesoy <burak@citusdata.com> 6.1.3.citus-1
- Update to Citus 6.1.3

* Tue Sep 12 2017 - Burak Yucesoy <burak@citusdata.com> 7.0.1.citus-1
- Update to Citus 7.0.1

* Tue Aug 29 2017 - Burak Yucesoy <burak@citusdata.com> 7.0.0.citus-1
- Update to Citus 7.0.0

* Thu Jul 13 2017 - Burak Yucesoy <burak@citusdata.com> 6.2.3.citus-1
- Update to Citus 6.2.3

* Wed Jun 7 2017 - Burak Velioglu <velioglub@citusdata.com> 6.2.2.citus-1
- Update to Citus 6.2.2

* Wed Jun 7 2017 - Jason Petersen <jason@citusdata.com> 6.1.2.citus-1
- Update to Citus 6.1.2

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
