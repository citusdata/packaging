%global pgmajorversion 11
%global pgpackageversion 11
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname pg-auto-failover
%global extname pgautofailover
%global debug_package %{nil}

Summary:	Postgres extension for automated failover and high-availability
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	v1.4.0
Release:	1%{dist}
License:	PostgreSQL
Group:		Applications/Databases
Source0:	https://github.com/citusdata/pg-auto-failover/archive/vv1.4.0.tar.gz
URL:		https://github.com/citusdata/pg_auto_failover
BuildRequires:	postgresql%{pgmajorversion}-devel postgresql%{pgmajorversion}-server libxml2-devel
BuildRequires:	libxslt-devel openssl-devel pam-devel readline-devel
Requires:	postgresql%{pgmajorversion}-server openssl
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
This extension implements a set of functions to provide High Availability to
Postgres.

%prep
%setup -q -n %{sname}-%{version}

%build
PATH=%{pginstdir}/bin:$PATH
make %{?_smp_mflags}
%if 0%{?rhel} && 0%{?rhel} <= 6
%else
  export PYTHONPATH=$(echo /usr/local/lib64/python3.*/site-packages):$(echo /usr/local/lib/python3.*/site-packages)
  make man
%endif

%install
PATH=%{pginstdir}/bin:$PATH
%make_install
# Install documentation with a better name:
%{__mkdir} -p %{buildroot}%{pginstdir}/doc/extension
%{__cp} README.md %{buildroot}%{pginstdir}/doc/extension/README-%{extname}.md

# install man pages
%if 0%{?rhel} && 0%{?rhel} <= 6
%else
  %{__mkdir} -p %{buildroot}/usr/share/man/man1
  %{__cp} docs/_build/man/pg_auto_failover.1 %{buildroot}/usr/share/man/man1/
  %{__cp} docs/_build/man/pg_autoctl.1 %{buildroot}/usr/share/man/man1/
  %{__mkdir} -p %{buildroot}/usr/share/man/man5
  %{__cp} docs/_build/man/pg_autoctl.5 %{buildroot}/usr/share/man/man5/
%endif

%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc %{pginstdir}/doc/extension/README-%{extname}.md
%if 0%{?rhel} && 0%{?rhel} <= 6
%else
  %doc /usr/share/man/man1/pg_auto_failover.1.gz
  %doc /usr/share/man/man1/pg_autoctl.1.gz
  %doc /usr/share/man/man5/pg_autoctl.5.gz
%endif
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
* Wed Sep 23 2020 - Onur Tirtir <Onur.Tirtir@microsoft.com> v1.4.0-1
- Official v1.4.0 release of pg_auto_failover

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
