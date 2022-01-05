%global pgmajorversion 13
%global pgpackageversion 13
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname azure_gdpr

Summary:	GDPR compliant logging for Azure
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	1.7.citus
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/azure_gdpr/archive/v1.7.tar.gz
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
* Wed Jan 05 2022 - Philip Dubé <phdub@microsoft.com> 1.7.citus-1
- Truncate strings to 1MB, as mdsd rejects strings which are long

* Thu Sep 16 2021 - Philip Dubé <phdub@microsoft.com> 1.6.citus-1
- Avoid leaking resources on OOM, cache resources to improve perf

* Thu Aug 19 2021 - Philip Dubé <phdub@microsoft.com> 1.5.citus-1
- Don't stop sending logs to mdsd after log hook raises error (like from OOM)

* Tue Apr 20 2021 - Gurkan Indibay  <gindibay@microsoft.com> 1.4.citus-1
- Official 1.4 release of Azure_gdpr

* Tue Apr 20 2021 - Gurkan Indibay <gindibay@microsoft.com> 1.3.citus-1
- Official 1.3 release of Azure_gdpr

* Sat Jan 9 2021 - Philip Dubé <phdub@microsoft.com> 1.2.citus-1
- Fix PG13 PG_MODULE_MAGIC

* Fri Nov 13 2020 - Hanefi Önaldi <Hanefi.Onaldi@microsoft.com> 1.1.citus-1
- Official 1.1 release of Azure_gdpr

* Wed Nov 11 2020 - Hanefi Önaldi <Hanefi.Onaldi@microsoft.com> 1.0.citus-1
- Official 1.0 release of Azure_gdpr
