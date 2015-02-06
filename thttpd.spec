%define _default_patch_fuzz 2
%define webroot /var/lib/thttpd

Summary:	Throttleable lightweight httpd server

Name:		thttpd
Version:	2.25b
Release:	14
License:	BSD
Group:		System/Servers
URL:		http://www.acme.com/software/thttpd
Source0:	%{name}-%{version}.tar.bz2
Source1:	%{name}.service
Source2:	%{name}.conf
Source3:	%{name}.logrotate
Source4:	%{name}.sysconfig
Source5:	%{name}-index.html
Source11:	%{name}_powered_3.png
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
# Hacks :-)
perl -pi -e 's/-o bin -g bin//g' Makefile
perl -pi -e 's/-m 444/-m 644/g; s/-m 555/-m 755/g' Makefile
perl -pi -e 's/.*chgrp.*//g; s/.*chmod.*//g' extras/Makefile
# Config changes
%{?_without_indexes:      perl -pi -e 's/#define GENERATE_INDEXES/#undef GENERATE_INDEXES/g' config.h}
%{!?_with_showversion:    perl -pi -e 's/#define SHOW_SERVER_VERSION/#undef SHOW_SERVER_VERSION/g' config.h}
%{!?_with_expliciterrors: perl -pi -e 's/#define EXPLICIT_ERROR_PAGES/#undef EXPLICIT_ERROR_PAGES/g' config.h}

# (list SUBDIRS to exclude "cgi-src")
%make \
    SUBDIRS="extras" \
    WEBDIR=%{webroot} \
    STATICFLAG="" \
    CCOPT="%{optflags} -D_FILE_OFFSET_BITS=64"


%install
# make some directories
# Prepare required directories
mkdir -p %{buildroot}%{webroot}
mkdir -p %{buildroot}%{_mandir}/man{1,8}
mkdir -p %{buildroot}%{_sbindir}
mkdir -p %{buildroot}%{_unitdir}

# Install init script and logrotate entry
install -Dpm 0644 %{SOURCE1} %{buildroot}%{_unitdir}/
install -Dpm 0644 %{SOURCE2} %{buildroot}%{_sysconfdir}/logrotate.d/thttpd

# Main install (list SUBDIRS to exclude "cgi-src")
%make install SUBDIRS="extras" \
    BINDIR=%{buildroot}%{_sbindir} \
    MANDIR=%{buildroot}%{_mandir} \
    WEBDIR=%{buildroot}%{webroot}

# Rename htpasswd in case apache is installed too
mkdir -p %{buildroot}%{_bindir}
mv %{buildroot}%{_sbindir}/htpasswd \
        %{buildroot}%{_bindir}/thtpasswd
mv %{buildroot}%{_mandir}/man1/htpasswd.1 \
        %{buildroot}%{_mandir}/man1/thtpasswd.1

# Install the default index.html and related files
install -pm 0644 %{SOURCE5} %{SOURCE11} \
    %{buildroot}%{webroot}/

# Symlink for the powered-by-$DISTRO image
%{__ln_s} %{_datadir}/pixmaps/poweredby.png \
    %{buildroot}%{webroot}/poweredby.png

# Install a default configuration file
cat << EOF > %{buildroot}%{_sysconfdir}/thttpd.conf
# BEWARE : No empty lines are allowed!
# This section overrides defaults
dir=%{webroot}
chroot
user=thttpd         # default = nobody
logfile=/var/log/thttpd.log
pidfile=/var/run/thttpd.pid
# This section _documents_ defaults in effect
# port=80
# nosymlink         # default = !chroot
# novhost
# nocgipat
# nothrottles
# host=0.0.0.0
# charset=iso-8859-1
EOF


%post
%systemd_post %{name}

%preun
%systemd_preun %{name}

%pre 
%_pre_useradd %{name} /var/lib/%{name} /bin/sh

%postun
%_postun_userdel %{name}

%files
%doc README TODO
%{_unitdir}/thttpd.service
%config(noreplace) %{_sysconfdir}/logrotate.d/thttpd
%config(noreplace) %{_sysconfdir}/thttpd.conf
%{_bindir}/thtpasswd
%{_sbindir}/syslogtocern
%{_sbindir}/thttpd
%{webroot}/
%attr(2755,%{name},%{name}) %{_sbindir}/makeweb
%{_mandir}/man?/*
