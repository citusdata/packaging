%global pgmajorversion 12
%global pgpackageversion 12
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname hll

Summary:	HyperLogLog extension for PostgreSQL
Name:		%{sname}_%{pgmajorversion}
Version:	2.18.citus
Release:	1%{dist}
License:	ASL 2.0
Group:		Applications/Databases
Source0:	https://github.com/citusdata/postgresql-hll/archive/v2.18.tar.gz
URL:		https://github.com/citusdata/postgresql-hll
BuildRequires:	postgresql%{pgmajorversion}-devel libxml2-devel
BuildRequires:	libxslt-devel openssl-devel pam-devel readline-devel
Requires:	postgresql%{pgmajorversion}-server
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
HyperLogLog extension for PostgreSQL.

%prep
%setup -q -n %{sname}-%{version}

%build
PATH=%{pginstdir}/bin:$PATH
make %{?_smp_mflags} SHLIB_LINK=-lstdc++

%install
PATH=%{pginstdir}/bin:$PATH
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
%{pginstdir}/lib/%{sname}.so
%{pginstdir}/share/extension/%{sname}-*.sql
%{pginstdir}/share/extension/%{sname}.control
%ifarch ppc64 ppc64le
 %else
 %if %{pgmajorversion} >= 11 && %{pgmajorversion} < 90
  %if 0%{?rhel} && 0%{?rhel} <= 6
  %else
   %{pginstdir}/lib/bitcode/%{sname}*.bc
   %{pginstdir}/lib/bitcode/%{sname}/src/*.bc
  %endif
 %endif
%endif

%changelog
* Fri Sep 1 2023 - Gurkan Indibay <gindibay@Microsoft.com> 2.18.citus-1
- Support for PostgreSQL 16

* Fri Aug 26 2022 - Gurkan Indibay <gindibay@Microsoft.com> 2.17.citus-1
- Support for PostgreSQL 15

* Mon Sep 13 2021 - Hanefi Onaldi <Hanefi.Onaldi@Microsoft.com> 2.16.citus-1
- Support for PostgreSQL 14

* Thu Nov 26 2020 - Hanefi Onaldi <Hanefi.Onaldi@Microsoft.com> 2.15.citus-1
- Support for PostgreSQL 13, parallel queries/aggregates and bug fixes

* Fri Nov 15 2019 - Hanefi Onaldi <Hanefi.Onaldi@Microsoft.com> 2.14.citus-1
- Bug fixes

* Wed Nov 6 2019 - Hanefi Onaldi <Hanefi.Onaldi@Microsoft.com> 2.13.citus-1
- Support for PostgreSQL 12

* Sat Nov 3 2018 - Burak Yucesoy <burak@citusdata.com> 2.12.citus-1
- Support for PostgreSQL 11

* Thu Oct 5 2017 - Jason Petersen <jason@citusdata.com> 2.10.2.citus-1
- Support for testing PostgreSQL 10

* Thu Sep 22 2016 - Jason Petersen <jason@citusdata.com> 2.10.1.citus-1
- First Citus-packaged release

* Fri Jan 10 2014 Timon Karnezos <timon.karnezos@gmail.com> - 2.10.0-0
- added binary IO type for hll

* Mon Dec 16 2013 Timon Karnezos <timon.karnezos@gmail.com> - 2.9.0-0
- bitstream_pack fixed to write one byte at a time to avoid writing to unallocated memory

* Tue Jul 16 2013 Timon Karnezos <timon.karnezos@gmail.com> - 2.8.0-0
- hll_add_agg now returns hll_empty on input of an empty set

* Wed Jun 12 2013 Timon Karnezos <timon.karnezos@gmail.com> - 2.7.1-0
- Build fixes for OS X and Debian.
- Documentation fixes.
- Small changes to test format to improve stability across psql versions.

* Tue Dec 11 2012 Ken Sedgwick <ken@bonsai.com> - 2.7-0
- Initial version.
