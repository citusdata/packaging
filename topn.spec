%global pgmajorversion 12
%global pgpackageversion 12
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname topn

Summary:	Counter Based Implementation for top-n Approximation
Name:		%{sname}_%{pgmajorversion}
Version:	2.5.0.citus
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/postgresql-topn/archive/v2.5.0.tar.gz
URL:		https://github.com/citusdata/posgresql-topn
BuildRequires:	postgresql%{pgmajorversion}-devel libxml2-devel
BuildRequires:	libxslt-devel openssl-devel pam-devel readline-devel
Requires:	postgresql%{pgmajorversion}-server
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
This extension is used to make approximations on top-n. It uses
JSONB objects to store and read the data frequency and provides
a chance to run real-time top-n queries on aggregated data.

%prep
%setup -q -n %{sname}-%{version}

%build
PATH=%{pginstdir}/bin:$PATH
make %{?_smp_mflags}

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
%doc %{pginstdir}/doc/extension/README-%{sname}.md
%{pginstdir}/lib/topn.so
%{pginstdir}/share/extension/topn-*.sql
%{pginstdir}/share/extension/topn.control
%ifarch ppc64 ppc64le
 %else
 %if %{pgmajorversion} >= 11 && %{pgmajorversion} < 90
  %if 0%{?rhel} && 0%{?rhel} <= 6
  %else
   %{pginstdir}/lib/bitcode/%{sname}/%{sname}*.bc
   %{pginstdir}/lib/bitcode/%{sname}*.bc
  %endif
 %endif
%endif

%changelog
* Fri Aug 26 2022 - Gurkan Indibay <gindibay@Microsoft.com> 2.5.0.citus-1
- Support for PostgreSQL 15

* Mon Sep 13 2021 - Hanefi Onaldi <Hanefi.Onaldi@Microsoft.com> 2.4.0.citus-1
- Support for PostgreSQL 14

* Mon Nov 30 2020 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 2.3.1.citus-1
- Support for PostgreSQL 13, parallel queries/aggregates and bug fixes

* Thu Oct 31 2019 - Hanefi Onaldi <Hanefi.Onaldi@microsoft.com> 2.3.0.citus-1
- Adds PostgreSQL 12 support

* Thu Dec 21 2018 - Furkan Sahin <furkan@citusdata.com> 2.2.2.citus-1
- PG11 beautified

* Thu Dec 20 2018 - Hanefi Onaldi <hanefi@citusdata.com> 2.2.1.citus-1
- Packaging fixes

* Fri Nov 02 2018 - Burak Velioglu <velioglub@citusdata.com> 2.2.0.citus-1
- Upgrade PG to 11

* Mon Jul 09 2018 - Furkan Sahin <furkan@citusdata.com> 2.1.0.citus-1
- Adds a return type for `topn` function

* Thu Mar 29 2018 - Burak Velioglu <velioglub@citusdata.com> 2.0.2.citus-1
- Fixes a bug for using with window functions

* Mon Nov 27 2017 - Marco Slot <marco@citusdata.com> 2.0.1.citus-1
- Ensure the number of elements does not exceed number_of_counters at the end of aggregation
- Fixes a character escaping issue

* Wed Nov 22 2017 - Burak Yucesoy <burak@citusdata.com> 2.0.0.citus-1
- Initial release

