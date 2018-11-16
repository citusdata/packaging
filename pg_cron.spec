%global pgmajorversion 11
%global pgpackageversion 11
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname pg_cron

Summary:	Periodic job scheduler for PostgreSQL
Name:		%{sname}_%{pgmajorversion}
Version:	1.1.3
Release:	1%{dist}
License:	PostgreSQL
Group:		Applications/Databases
Source0:	https://github.com/citusdata/pg_cron/archive/v1.1.3.tar.gz
URL:		https://github.com/citusdata/pg_cron
BuildRequires:	postgresql%{pgmajorversion}-devel libxml2-devel
BuildRequires:	libxslt-devel openssl-devel pam-devel readline-devel
Requires:	postgresql%{pgmajorversion}-server
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
This extension adds a periodic job scheduler to PostgreSQL to can
run many concurrent commands in the background.

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
%{pginstdir}/lib/pg_cron.so
%{pginstdir}/share/extension/pg_cron-*.sql
%{pginstdir}/share/extension/pg_cron.control
%ifarch ppc64 ppc64le
  %else
  %if %{pgmajorversion} >= 11 && %{pgmajorversion} < 90
    %if 0%{?rhel} && 0%{?rhel} <= 6
    %else
      %{pginstdir}/lib/bitcode/%{sname}/src/*.bc
      %{pginstdir}/lib/bitcode/%{sname}.index.bc
    %endif
  %endif
%endif

%changelog
* Fri Nov 16 2018 - Burak Velioglu <velioglub@citusdata.com> 1.1.3.citus-1
- PostgreSQL 11 support
* Fri Oct 6 2017 - Marco Slot <marco@citusdata.com> 1.0.2-1.citus-1
- PostgreSQL 10 support
- Restrict the maximum number of concurrent tasks
- Ensure table locks on cron.job are kept after schedule/unschedule
* Fri Jun 30 2017 - Marco Slot <marco@citusdata.com> 1.0.1-1.citus-1
- Fixes a memory leak that occurs when a connection fails immediately
- Fixes a memory leak due to switching memory context when loading metadata
- Fixes a segmentation fault that can occur when using an error message after PQclear
* Fri Jan 27 2017 - Marco Slot <marco@citusdata.com> 1.0.0-1.citus-1
- Use WaitLatch instead of pg_usleep when there are no tasks
* Thu Dec 15 2016 - Marco Slot <marco@citusdata.com> 1.0.0-rc.1.citus-1
- Initial 1.0 candidate
