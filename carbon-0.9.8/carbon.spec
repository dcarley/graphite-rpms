%define ver  0.9.8
%define rel  1
%define dist cja

%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define __getent   /usr/bin/getent
%define __useradd  /usr/sbin/useradd
%define __userdel  /usr/sbin/userdel
%define __groupadd /usr/sbin/groupadd
%define __touch    /bin/touch
%define __service  /sbin/service

Name:          carbon
Version:       %{ver}
Release:       %{rel}%{?dist:.%{dist}}
Summary:       Backend data caching and persistence daemon for Graphite
Group:         Applications/Internet
License:       Apache Software License 2.0
URL:           https://launchpad.net/graphite
Vendor:        Chris Davis <chrismd@gmail.com>
Packager:      Chris Abernethy <cabernet@chrisabernethy.com>
Source0:       %{name}-%{version}.tar.gz
Patch0:        %{name}-setup.patch
Patch1:        %{name}-scripts.patch
Patch2:        %{name}-config.patch
Source1:       %{name}.init
Source2:       %{name}.sysconfig
BuildRoot:     %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:     noarch

BuildRequires: python python-devel python-setuptools
Requires:      python python-twisted-core whisper

%description
The backend for Graphite. Carbon is a data collection and storage agent.  

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} -c 'import setuptools; execfile("setup.py")' build

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}
%{__python} -c 'import setuptools; execfile("setup.py")' install --skip-build --root %{buildroot}

# Create log and var directories
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/%{name}
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/%{name}

# Install system configuration and init scripts
%{__install} -Dp -m0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
%{__install} -Dp -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# Install default configuration files
%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
%{__install} -Dp -m0644 conf/carbon.conf.example %{buildroot}%{_sysconfdir}/%{name}/carbon.conf
%{__install} -Dp -m0644 conf/storage-schemas.conf.example %{buildroot}%{_sysconfdir}/%{name}/storage-schemas.conf

# Create transient files in buildroot for ghosting
%{__mkdir_p} %{buildroot}%{_localstatedir}/lock/subsys
%{__touch} %{buildroot}%{_localstatedir}/lock/subsys/%{name}

%{__mkdir_p} %{buildroot}%{_localstatedir}/run
%{__touch} %{buildroot}%{_localstatedir}/run/%{name}.pid

%pre
%{__getent} group %{name} >/dev/null || %{__groupadd} -r %{name}
%{__getent} passwd %{name} >/dev/null || \
    %{__useradd} -r -g %{name} -d %{_localstatedir}/lib/%{name} \
    -s /sbin/nologin -c "Carbon cache daemon" %{name}
exit 0

%preun
%{__service} %{name} stop
exit 0

%postun
if [ $1 = 0 ]; then
  %{__getent} passwd %{name} >/dev/null && \
      %{__userdel} -r %{name} 2>/dev/null
fi
exit 0

%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc LICENSE PKG-INFO conf/*

%{python_sitelib}/*
/usr/bin/*
%{_initrddir}/%{name}

%config %{_sysconfdir}/%{name}
%config %{_sysconfdir}/sysconfig/%{name}

%attr(-,%name,%name) %{_localstatedir}/log/%{name}
%attr(-,%name,%name) %{_localstatedir}/lib/%{name}

%ghost %{_localstatedir}/lock/subsys/%{name}
%ghost %{_localstatedir}/run/%{name}.pid

%changelog
* Tue Apr 19 2011 Chris Abernethy <cabernet@chrisabernethy.com> - 0.9.8-1
- Update source to upstream v0.9.8
- Minor updates to spec file

* Thu Mar 17 2011 Daniel Aharon <daharon@sazze.com> - 0.9.7-1
- Add dependencies, description, init script and sysconfig file.
