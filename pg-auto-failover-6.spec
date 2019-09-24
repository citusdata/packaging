%global pgmajorversion 11
%global pgpackageversion 11
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname pg-auto-failover
%global extname pgautofailover

Summary:	Postgres extension for automated failover and high-availability
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	1.0.5
Release:	1%{dist}
License:	PostgreSQL
Group:		Applications/Databases
Source0:	https://github.com/citusdata/pg_auto_failover/archive/v1.0.5.tar.gz
URL:		https://github.com/citusdata/pg_auto_failover
BuildRequires:	postgresql%{pgmajorversion}-devel postgresql%{pgmajorversion}-server libxml2-devel
BuildRequires:	libxslt-devel openssl-devel pam-devel readline-devel
Requires:	postgresql%{pgmajorversion}-server
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
This extension implements a set of functions to provide High Availability to
Postgres.

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
%{__cp} README.md %{buildroot}%{pginstdir}/doc/extension/README-%{extname}.md

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc %{pginstdir}/doc/extension/README-%{extname}.md
%{pginstdir}/lib/%{extname}.so
%{pginstdir}/share/extension/%{extname}-*.sql
%{pginstdir}/share/extension/%{extname}.control
%{pginstdir}/bin/pg_autoctl
%ifarch ppc64 ppc64le
  %else
  %if %{pgmajorversion} >= 11 && %{pgmajorversion} < 90
    %if 0%{?rhel} && 0%{?rhel} <= 6
    %else
      %{pginstdir}/lib/bitcode/%{extname}*.bc
      %{pginstdir}/lib/bitcode/%{extname}/*.bc
    %endif
  %endif
%endif


%changelog
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
