%global pgmajorversion 11
%global pgpackageversion 11
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname citus

Summary:	PostgreSQL-based distributed RDBMS
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	9.4.5.citus-enterprise
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/citus-enterprise/archive/v10.0.3.tar.gz
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
