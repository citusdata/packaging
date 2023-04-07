%global pgmajorversion 14
%global pgpackageversion 14
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname azure_storage

Summary:	Pg Azure storage
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	1.2.0.citus
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/pgazure/archive/v1.2.0.tar.gz
URL:		https://github.com/citusdata/pgazure
BuildRequires:	postgresql%{pgmajorversion}-devel libcurl-devel libxml2-devel libxslt-devel openssl-devel
Requires:	postgresql%{pgmajorversion}-server
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
PostgreSQL extension for Azure storage

%prep
%setup -q -n %{sname}-%{version}

%build
# make %{?_smp_mflags}
# PG_CONFIG=%{pginstdir}/bin/pg_config make %{?_smp_mflags}
# export PATH=/usr/pgsql-11/bin/pg_config:$PATH
PATH=%{pginstdir}/bin:$PATH
make %{?_smp_mflags}
# make %{?_smp_mflags}

%install
%make_install PG_CONFIG=%{pginstdir}/bin/pg_config
%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{pginstdir}/lib/%{sname}.so
%{pginstdir}/share/extension/%{sname}.control
%{pginstdir}/bin/azure_storage_cli
%{pginstdir}/bin/mock_azure_storage_cli
%{pginstdir}/share/extension/azure_storage-*.sql
%ifarch ppc64 ppc64le
  %else
  %if 0%{?rhel} && 0%{?rhel} <= 6
  %else
    %{pginstdir}/lib/bitcode/%{sname}*.bc
    %{pginstdir}/lib/bitcode/%{sname}/*/*.bc
  %endif
%endif

%changelog
* Fri Apr 7 2023 - Gledis Zeneli <gindibay@microsoft> 1.2.0.citus-1
- Official 1.2.0 release of Pg Azure Storage

* Thu Dec 22 2022 - Gledis Zeneli <glediszeneli@microsoft> 1.1.0.citus-1
- Official 1.1.0 release of Pg Azure Storage

* Fri Nov 4 2022 - Gurkan Indibay <gindibay@microsoft.com> 1.0.3.citus-1
- Official 1.0.3 release of Pg Azure Storage

* Fri Sep 30 2022 - Gurkan Indibay <gindibay@microsoft.com> 1.0.2.citus-1
- Official 1.0.2 release of Pg Azure Storage
