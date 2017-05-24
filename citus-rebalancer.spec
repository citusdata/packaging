%global pgmajorversion 96
%global pgpackageversion 9.6
%global pginstdir /usr/pgsql-%{pgpackageversion}
%global sname citus-rebalancer

Summary:	Dynamic shard balancer for Citus
Name:		%{sname}%{?pkginfix}_%{pgmajorversion}
Provides:	%{sname}_%{pgmajorversion}
Conflicts:	%{sname}_%{pgmajorversion}
Version:	6.2.0.citus
Release:	1%{dist}
License:	AGPLv3
Group:		Applications/Databases
Source0:	https://github.com/citusdata/shard_rebalancer/archive/v6.2.0.tar.gz
URL:		https://github.com/citusdata/shard_rebalancer
BuildRequires:	postgresql%{pgmajorversion}-devel libxml2-devel
BuildRequires:	libxslt-devel openssl-devel pam-devel readline-devel
BuildRequires:	citus_%{pgmajorversion} >= 6.0.0
Requires:	postgresql%{pgmajorversion}-server citus-enterprise%{?pkginfix}_%{pgmajorversion} >= 6.2.0
BuildRoot:	%{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
This extension implements a set of functions for rebalancing
and replicating shards in Citus clusters.

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
%{pginstdir}/lib/shard_rebalancer.so
%{pginstdir}/share/extension/shard_rebalancer-*.sql
%{pginstdir}/share/extension/shard_rebalancer.control

%changelog
* Wed May 24 2017 - Jason Petersen <jason@citusdata.com> 6.2.0.citus-1
- Official release for 6.2.0

* Wed Feb 15 2017 - Jason Petersen <jason@citusdata.com> 6.1.0.citus-1
- Official release for 6.1.0

* Wed Feb 15 2017 - Burak <burak@citusdata.com> 6.0.0.citus-2
- Transitional package to guide users to new package name

* Thu Nov 10 2016 - Jason Petersen <jason@citusdata.com> 6.0.0.citus-1
- Official release for 6.0.0

* Wed Sep 28 2016 - Jason Petersen <jason@citusdata.com> 5.2.0.citus-1
- Official release for 5.2.0

* Wed Sep 28 2016 - Jason Petersen <jason@citusdata.com> 5.2.0-0.1.rc.1
- Release candidate for 5.2.

* Thu Jun 30 2016 - Jason Petersen <jason@citusdata.com> 5.1.0-1
- Official release for 5.1.0

* Tue May 10 2016 - Jason Petersen <jason@citusdata.com> 5.1.0-0.1.rc.1
- Release candidate for 5.1.
