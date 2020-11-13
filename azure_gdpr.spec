%global pgmajorversion 13
%global pgpackageversion 13
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname azure_gdpr

Summary:	GDPR compliant logging for Azure
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	1.0.citus
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/azure_gdpr/archive/v1.0.tar.gz
URL:		https://github.com/citusdata/azure_gdpr
BuildRequires:	postgresql%{pgmajorversion}-devel
Requires:	postgresql%{pgmajorversion}-server
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
PostgreSQL extension for GDPR compliant logging for Azure

%prep
%setup -q -n %{sname}-%{version}

%build
# make %{?_smp_mflags}
# PG_CONFIG=%{pginstdir}/bin/pg_config make %{?_smp_mflags}
# export PATH=/usr/pgsql-11/bin/pg_config:$PATH
%{__make} PG_CONFIG=%{pginstdir}/bin/pg_config USE_PGXS=1 %{?_smp_mflags}
# make %{?_smp_mflags}

%install
%make_install PG_CONFIG=%{pginstdir}/bin/pg_config
%clean
%{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%{pginstdir}/lib/%{sname}.so
%{pginstdir}/share/extension/%{sname}.control
%ifarch ppc64 ppc64le
  %else
  %if 0%{?rhel} && 0%{?rhel} <= 6
  %else
    %{pginstdir}/lib/bitcode/%{sname}*.bc
    %{pginstdir}/lib/bitcode/%{sname}/*.bc
  %endif
%endif

%changelog
* Wed Nov 11 2020 - Hanefi Önaldi <Hanefi.Onaldi@microsoft.com> 1.0.citus-1
- Official 1.0 release of Azure_gdpr
