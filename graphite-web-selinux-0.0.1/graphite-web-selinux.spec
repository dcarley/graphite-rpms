%global modulename graphiteweb
%global selinux_variants targeted
%global selinux_dirs /var/lib/graphite-web

Name            : graphite-web-selinux
Version         : 0.0.1
Release         : 1
Summary         : SELinux file contexts for graphite-web in /var/lib/graphite-web
Group           : System Environment/Base

Source0         : %{modulename}.te
Source1         : %{modulename}.fc
Source2         : %{modulename}.if
URL             : http://labs.yell.com/
Vendor          : Yell Labs
License         : BSD
Packager        : Dan Carley <dan.carley@gmail.com>

BuildArch       : noarch
BuildRoot       : %{_tmppath}/%{name}-%{version}-root
Requires        : graphite-web
Requires        : selinux-policy
Requires(post)  : /usr/sbin/semodule, /sbin/restorecon
Requires(postun): /usr/sbin/semodule, /sbin/restorecon
BuildRequires   : checkpolicy, selinux-policy-devel, hardlink

%description
SELinux file contexts to support HTTPd using Graphite's SQLite database
from the default location of /var/lib/graphite-web

%prep
%setup -cT
cp -p %{SOURCE0} %{SOURCE1} %{SOURCE2} .

%build
for selinuxvariant in %{selinux_variants}; do
    make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile
    mv %{modulename}.pp %{modulename}.pp.${selinuxvariant}
    make NAME=${selinuxvariant} -f /usr/share/selinux/devel/Makefile clean
done

%install
rm -rf %{buildroot}

for selinuxvariant in %{selinux_variants}; do
    install -d %{buildroot}%{_datadir}/selinux/${selinuxvariant}
    install -p -m 644 %{modulename}.pp.${selinuxvariant} \
        %{buildroot}%{_datadir}/selinux/${selinuxvariant}/%{modulename}.pp
done

# Consolidate multiple copies of the same file.
/usr/sbin/hardlink -cv %{buildroot}%{_datadir}/selinux

%clean
rm -rf %{buildroot}

%post
for selinuxvariant in %{selinux_variants}; do
    /usr/sbin/semodule -s ${selinuxvariant} -i \
        %{_datadir}/selinux/${selinuxvariant}/%{modulename}.pp &> /dev/null || :
done
for selinux_dir in %{selinux_dirs}; do
    [ -d ${selinux_dir} ] && /sbin/restorecon -R ${selinux_dir} &> /dev/null || :
done

%postun
if [ $1 -eq 0 ] ; then
    for selinuxvariant in %{selinux_variants}; do
        /usr/sbin/semodule -s ${selinuxvariant} -r %{modulename} &> /dev/null || :
    done
    for selinux_dir in %{selinux_dirs}; do
        [ -d ${selinux_dir} ] && /sbin/restorecon -R ${selinux_dir} &> /dev/null || :
    done
fi

%files
%defattr(-,root,root,0755)
%doc %{modulename}.*
%{_datadir}/selinux/*/%{modulename}.pp

%changelog
* Tue May 24 2011 Dan Carley <dan.carley@gmail.com> 0.1.0-1
- Initial release.
