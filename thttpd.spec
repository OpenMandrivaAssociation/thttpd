%define _default_patch_fuzz 2

%define	name	thttpd
%define	version	2.25b
%define	release	%mkrel 10

Summary:	Throttleable lightweight httpd server
Name:		%{name}
Version:	%{version}
Release:	%{release}
License:	BSD
Group:		System/Servers
URL:		http://www.acme.com/software/thttpd
Source0:	%{name}-%{version}.tar.bz2
Source1:	%{name}.init
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Source4:	%{name}.sysconfig
Source5:	%{name}-index.html
# http://rekl.yi.org/thttpd/pub/patch-thttpd-2.25b-re1
Patch0:		patch-thttpd-2.25b-re1
# http://jonas.fearmuffs.net/software/thttpd/thttpd-2.25b+impan-pl5.diff.gz
Patch1:		thttpd-2.25b+impan-pl5.diff
# http://www.ogris.de/thttpd/thttpd-2.25b.access.patch.diff
Patch2:		thttpd-2.25b.access.patch.diff
Patch3:		thttpd-2.25b-getline_conflict_fix.diff
Requires(post,preun):	rpm-helper
Provides:	webserver
BuildRequires:	zlib-devel
BuildRoot:	%{_tmppath}/%{name}-buildroot

%description
Thttpd is a very compact no-frills httpd serving daemon that can
handle very high loads.  While lacking many of the advanced
features of Apachee, thttpd operates without forking and is
extremely efficient in memory use.  Basic support for cgi scripts,
authentication, and ssi is provided for. Advanced features include
the ability to throttle traffic.

%prep

%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p0

# tag the default index.html page
perl -pi -e "s|_NAME_-_VERSION_|%{name}-%{version}|g" %{name}-index.html

echo "# put some css in here for directory listings" > dirlist.css 
echo "# put some css in here for custom error messages" > error.css
echo "<b>This directory contains 'el cheapo' style web links.</b>" > .description

%build

%configure

%make \
    prefix=%{_prefix} \
    BINDIR=%{_sbindir} \
    MANDIR=%{_mandir} \
    WEBDIR=/var/lib/%{name} \
    WEBGROUP=%{name} \
    CGIBINDIR=/var/lib/%{name}/cgi-bin

%install
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

# make some directories
install -d %{buildroot}%{_initrddir}
install -d %{buildroot}%{_sysconfdir}/{sysconfig,logrotate.d}
install -d %{buildroot}/var/lib/%{name}/{cgi-bin,errors,styles,links}
install -d %{buildroot}/var/log/%{name}
install -d %{buildroot}/var/run/%{name}
install -d %{buildroot}%{_sbindir}
install -d %{buildroot}%{_mandir}/man{1,8}

# install binaries
install -m0755 %{name} %{buildroot}%{_sbindir}/%{name}
install -m0755 extras/htpasswd %{buildroot}%{_sbindir}/%{name}-htpasswd
install -m0755 extras/makeweb %{buildroot}%{_sbindir}/
install -m0755 extras/syslogtocern %{buildroot}%{_sbindir}/
install -m0755 cgi-bin/printenv %{buildroot}/var/lib/%{name}/cgi-bin/printenv.cgi
install -m0755 cgi-src/phf %{buildroot}/var/lib/%{name}/cgi-bin/
install -m0755 cgi-src/redirect %{buildroot}/var/lib/%{name}/cgi-bin/
install -m0755 cgi-src/ssi %{buildroot}/var/lib/%{name}/cgi-bin/

# install man pages
install -m0644 cgi-src/redirect.8 %{buildroot}%{_mandir}/man8/
install -m0644 cgi-src/ssi.8 %{buildroot}%{_mandir}/man8/
install -m0644 extras/htpasswd.1 %{buildroot}%{_mandir}/man1/%{name}-htpasswd.1
install -m0644 extras/makeweb.1 %{buildroot}%{_mandir}/man1/
install -m0644 extras/syslogtocern.8 %{buildroot}%{_mandir}/man8/
install -m0644 thttpd.8 %{buildroot}%{_mandir}/man8/

# install config files
install -m0755 %{SOURCE1} %{buildroot}%{_initrddir}/%{name}
install -m0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/%{name}.conf
install -m0644 %{SOURCE3} %{buildroot}%{_sysconfdir}/logrotate.d/%{name}
install -m0644 %{SOURCE4} %{buildroot}%{_sysconfdir}/sysconfig/%{name}

# install web contents
install -m0644 %{SOURCE5} %{buildroot}/var/lib/%{name}/index.html
install -m0644 dirlist.css %{buildroot}/var/lib/%{name}/styles/
install -m0644 error.css %{buildroot}/var/lib/%{name}/styles/
install -m0644 .description %{buildroot}/var/lib/%{name}/links/

ln -snf "http://rekl.yi.org/thttpd/pub/patch-thttpd-2.25b-re1" \
    %{buildroot}/var/lib/%{name}/links/patch-thttpd-2.25b-re1
ln -snf "http://jonas.fearmuffs.net/software/thttpd/thttpd-2.25b+impan-pl5.diff.gz" \
    %{buildroot}/var/lib/%{name}/links/thttpd-2.25b+impan-pl5.diff.gz
ln -snf "http://www.acme.com/software/thttpd/thttpd-2.25b.tar.gz" \
    %{buildroot}/var/lib/%{name}/links/thttpd-2.25b.tar.gz

%clean
[ "%{buildroot}" != "/" ] && rm -rf %{buildroot}

%post
%_post_service %{name}

%preun
%_preun_service %{name}

%pre 
%_pre_useradd %{name} /var/lib/%{name} /bin/sh

%postun
%_postun_userdel %{name}

%files
%defattr(-,root,root)
%doc README TODO
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/%{name}.conf
%config(noreplace) %attr(0755,root,root) %{_initrddir}/%{name}
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/logrotate.d/%{name}
%config(noreplace) %attr(0644,root,root) %{_sysconfdir}/sysconfig/%{name}
%config(noreplace) %attr(0644,root,root) /var/lib/%{name}/styles/*.css
%config(noreplace) %attr(0644,root,root) /var/lib/%{name}/index.html
%attr(2755,%{name},%{name}) %{_sbindir}/makeweb
%attr(0755,root,root) %{_sbindir}/%{name}-htpasswd
%attr(0755,root,root) %{_sbindir}/syslogtocern
%attr(0755,root,root) %{_sbindir}/%{name}
%attr(0755,%{name},%{name}) %dir /var/lib/%{name}
%attr(0755,%{name},%{name}) %dir /var/lib/%{name}/cgi-bin
%attr(0755,%{name},%{name}) %dir /var/log/%{name}
%attr(0755,%{name},%{name}) %dir /var/run/%{name}
%attr(0755,root,root) /var/lib/%{name}/cgi-bin/printenv.cgi
%attr(0755,root,root) /var/lib/%{name}/cgi-bin/phf
%attr(0755,root,root) /var/lib/%{name}/cgi-bin/redirect
%attr(0755,root,root) /var/lib/%{name}/cgi-bin/ssi
%attr(0644,root,root) %{_mandir}/man*/*
%attr(0644,%{name},%{name}) /var/lib/%{name}/links/.description
%attr(0644,%{name},%{name}) /var/lib/%{name}/links/*


