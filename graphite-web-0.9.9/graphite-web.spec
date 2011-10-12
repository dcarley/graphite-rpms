%{!?python_sitelib: %define python_sitelib %(%{__python} -c "from distutils.sysconfig import get_python_lib; print get_python_lib()")}

%define __touch    /bin/touch
%define __service  /sbin/service

Name:           graphite-web
Version:        0.9.9
Release:        1
Summary:        Enterprise scalable realtime graphing
Group:          Applications/Internet
License:        Apache License
URL:            https://launchpad.net/graphite
Vendor:         Chris Davis <chrismd@gmail.com>
Packager:       Dan Carley <dan.carley@gmail.com>
Source0:        http://launchpad.net/graphite/0.9/%{version}/+download/%{name}-%{version}.tar.gz
Patch0:         graphite-web-setup.patch
Patch1:         graphite-web-settings.patch
Patch2:         graphite-web-vhost.patch
Patch3:         graphite-web-wsgi.patch
BuildRoot:      %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)
BuildArch:      noarch
BuildRequires:  python python-devel python-setuptools
Requires:       Django django-tagging httpd mod_wsgi pycairo python-sqlite2 python-simplejson

%description
Graphite consists of a storage backend and a web-based visualization frontend.
Client applications send streams of numeric time-series data to the Graphite
backend (called carbon), where it gets stored in fixed-size database files
similar in design to RRD. The web frontend provides 2 distinct user interfaces
for visualizing this data in graphs as well as a simple URL-based API for
direct graph generation.

Graphite's design is focused on providing simple interfaces (both to users and
applications), real-time visualization, high-availability, and enterprise
scalability.

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1

%build
CFLAGS="$RPM_OPT_FLAGS" %{__python} -c 'import setuptools; execfile("setup.py")' build

%install
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}
%{__python} -c 'import setuptools; execfile("setup.py")' install --skip-build --root %{buildroot}

# Create var directory with ghost files
%{__mkdir_p} %{buildroot}%{_localstatedir}/lib/%{name}
%{__touch} %{buildroot}%{_localstatedir}/lib/%{name}/graphite.db

# Create log directory with ghost files
%{__mkdir_p} %{buildroot}%{_localstatedir}/log/%{name}
%{__touch} %{buildroot}%{_localstatedir}/log/%{name}/access.log
%{__touch} %{buildroot}%{_localstatedir}/log/%{name}/error.log
%{__touch} %{buildroot}%{_localstatedir}/log/%{name}/exception.log
%{__touch} %{buildroot}%{_localstatedir}/log/%{name}/info.log

# Create config directory and install configuration files
%{__mkdir_p} %{buildroot}%{_sysconfdir}/%{name}
%{__install} -Dp -m0644 conf/dashboard.conf.example %{buildroot}%{_sysconfdir}/%{name}/dashboard.conf
%{__install} -Dp -m0644 webapp/graphite/local_settings.py.example %{buildroot}%{_sysconfdir}/%{name}/local_settings.py

# Install the example wsgi controller and vhost configuration
%{__install} -Dp -m0755 conf/graphite.wsgi.example %{buildroot}/usr/share/graphite/%{name}.wsgi
%{__install} -Dp -m0644 examples/example-graphite-vhost.conf %{buildroot}%{_sysconfdir}/httpd/conf.d/%{name}.conf

# Create local_settings symlink
%{__ln_s} %{_sysconfdir}/%{name}/local_settings.py %{buildroot}%{python_sitelib}/graphite/local_settings.py

%post
# Initialize the database
%{__python} %{python_sitelib}/graphite/manage.py syncdb --noinput >/dev/null
%{__chown} apache:apache %{_localstatedir}/lib/%{name}/graphite.db


%clean
[ "%{buildroot}" != "/" ] && %{__rm} -rf %{buildroot}

%files
%defattr(-,root,root,-)
%doc INSTALL LICENSE PKG-INFO README conf/* examples/*

%{python_sitelib}/*
/usr/bin/*
/usr/share/graphite
/etc/httpd/conf.d/%{name}.conf

%config %{_sysconfdir}/%{name}

%attr(775,root,apache) %dir %{_localstatedir}/log/%{name}
%ghost %{_localstatedir}/log/%{name}/access.log
%ghost %{_localstatedir}/log/%{name}/error.log
%ghost %{_localstatedir}/log/%{name}/exception.log
%ghost %{_localstatedir}/log/%{name}/info.log

%attr(775,root,apache) %dir %{_localstatedir}/lib/%{name}
%ghost %{_localstatedir}/lib/%{name}/graphite.db

%changelog
* Sat Oct 8 2011 Dan Carley <dan.carley@gmail.com> - 0.9.9-1
- New upstream version.

* Mon May 23 2011 Dan Carley <dan.carley@gmail.com> - 0.9.8-2
- Repackage with some tidying.
- Move state directory to /var/lib
- Remove debug print to stdout.
- Don't restart Apache. Kind of obtrusive.

* Tue Apr 19 2011 Chris Abernethy <cabernet@chrisabernethy.com> - 0.9.8-1
- Update source to upstream v0.9.8
- Minor updates to spec file

* Tue Mar 23 2010 Ilya Zakreuski <izakreuski@gmail.com> 0.9.5-1
- Initial release.
