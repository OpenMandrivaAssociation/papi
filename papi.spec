##### VERSION NUMBERS

%define papiversion 1.0
%define papiextraversion svn-r
%define papisvnrevision 177
%define papireleaseno 0.%{papisvnrevision}.1
%define papirelease %mkrel %papireleaseno
%define papimajor 0
%define libpapi %mklibname papi %{papimajor}

##### BUILD OPTIONS

%define debug 0
%define withapache 0
%define withruby 1

##### RPM PROBLEM WORKAROUNDS

# Suppress automatically generated Requires for devel packages and
# for libpapi.so.0 (this one will be generated by update-alternatives
# in the postinstall script of libpapi)
%define _requires_exceptions devel\(.*\)\\|libpapi\.so\.%{papimajor}

# Suppress automatically generated Requires for Perl libraries.
#define _requires_exceptions perl\(.*\)

#define _unpackaged_files_terminate_build       0 
#define _missing_doc_files_terminate_build      0

##### GENERAL DEFINITIONS

Summary:	FSG OpenPrinting PAPI Implementation(s) and Applications
Name:		papi
Version:	%{papiversion}
Release:	%{papirelease}
License:	GPL/LPGL/MIT/CDDL
Group:		System/Servers
Requires:	/usr/sbin/update-alternatives
URL:		http://openprinting.sourceforge.net/


##### BUILDREQUIRES

%if %{withapache}
BuildRequires: apache-devel
%endif
%if %{withruby}
BuildRequires: ruby-devel
%endif



##### PAPI SOURCES

Source0:	http://sourceforge.net/projects/openprinting/papi-%{papiversion}%{papiextraversion}%{papisvnrevision}.tar.bz2

##### PAPI PATCHES

# Fixed acinclude.m4 so that it is also checked for the apr.h file of
# libapr-1 which is needed by the Apache headers
#Patch1:		papi-1.0-acinclude-m4-apache-apr1.patch.bz2



##### BUILD ROOT

BuildRoot:	%_tmppath/%name-%papiversion-%papirelease-root



##### PACKAGE DESCRIPTIONS

%package common
Summary: 	FSG OpenPrinting PAPI Common files and Documentation
Group: 		System/Servers
Obsoletes:	papi-doc
Provides:	papi-doc

%package commands
Summary:	FSG OpenPrinting PAPI BSD and System V printing commands
Group: 		System/Servers
Requires:	/usr/sbin/update-alternatives
Conflicts:	cups-common <= 1.2.0-2mdk

%package utils
Summary: 	FSG OpenPrinting PAPI sample tools
Group: 		System/Servers
Obsoletes:	papi-tools
Provides:	papi-tools

%if %{withruby}
%package -n ruby-papi
Summary: 	FSG OpenPrinting PAPI Ruby bindings
Group: 		System/Servers
Requires:	ruby
Obsoletes:	papi-ruby
Provides:	papi-ruby

%package -n ruby-papi-devel
Summary: 	FSG OpenPrinting PAPI Ruby bindings, development libraries
Group: 		Development/Other
Requires:	ruby-papi
%endif

%if %{withapache}
%package apache
Summary: 	FSG OpenPrinting PAPI IPP server Apache module
Group: 		System/Servers
Requires:	apache-base
%endif

%package -n %libpapi
Summary: 	FSG OpenPrinting PAPI libraries
Group: 		System/Servers
Requires:	papi-common
Provides:	libpapi.so.%{papimajor}
Obsoletes:	papi-psm
Provides:	papi-psm

%package -n %libpapi-devel
Summary: 	Headers and links to compile against the "%{libpapi}" library
Group:		Development/C
Requires: 	%{libpapi} = %{version}
Provides:	libpapi-devel
Provides:	papi-devel



##### DESCRIPTION TEXTS

%description
This package contains implentations of the Free Standards Group (FSG)
Open Printing API (PAPI) (v1.0) and client software that uses it.  The
implemenations of the API are designed so that they can be used
individually to support client application interaction with a
particular type of print service or together to interact with a
variety of different print service types.

%description common
This package contains common files like man pages, documentation, the
LPD privileged port access helper, etc. The documentation includesthe
FSG OpenPrinting PAPI specification and also information on how to use
and how to develop with this implementation of PAPI. It also contains
the source code of the papi-utils package as coding example.

%description commands
Implementations of the BSD and SYSV printing commands layered on top
of the PAPI.  The command implementation are intended to be reasonably
faithful to their counterparts on a Solaris system.  They should be
reasonably faithful to pretty much any implementation of these
commands.  This should allow them to be dropped on a system and used
in place of any prior version of the commands without causing layered
scripts and software to break.  The commands covered are:

     BSD:    lpr(1), lpq(1), lprm(1), lpc(8)
     SYSV:   lp(1), lpstat(1), cancel(1), accept(8), reject(8),
             enable(8), disable(8)

%description utils
Sample tools that makes use of the API to do marginally interesting
things.

%if %{withruby}
%description -n ruby-papi
Ruby bindings for the PAPI libraries

%description -n ruby-papi-devel
This package contains the .la files for the ruby bindings for
PAPI. It's likely nobody will ever need these.
%endif

%if %{withapache}
%description apache
Apache module to make Apache working as IPP server
%endif

%description -n %libpapi
This package contains libraries which provide PAPI implementation

%description -n %libpapi-devel
This package contains the static library and the header files needed
to compile applications using the PAPI shared libraries.



%prep

# remove old directory
rm -rf $RPM_BUILD_DIR/papi

##### PAPI

%setup -q -n papi
#patch1 -p0 -b .apache-apr1

# Let other names be used for the libraries, to express that they work all
# directly as a libpapi and not only as plug-ins for libpapi-dynamic.
perl -p -i -e 's:psm([_\-])lpd:libpapi${1}lpd:' source/libpapi-lpd/Makefile.am
perl -p -i -e 's:psm([_\-])ipp:libpapi${1}ipp:' source/libpapi-ipp/Makefile.am
perl -p -i -e 's:\"/psm(-%s.so)\":\"/libpapi$1\":' source/libpapi-dynamic/psm.c
# Add lines to the source/libpapi-dynamic/Makefile.am so that libpapi.so is
# built twice, once with the name libpapi.so and second as
# libpapi-dynamic.so. We will include only libpapi-dynamic.so (and make a
# symbolic link named libpapi.so to the library we actually want to use).
# The libpapi.so which we build here only serves to satisfy the compilation
# process of the other parts of this package. After having run "make
# install" we delete it.
# There are three calls of Perl to modify the Makefile.am: The first joins 
# continuation lines ('\' in the end of a line to continue the line in the 
# next line), so that it is easier to manipilate and copy lines. The second
# copies all lines beginning with "libpapi_la" and replaces the "libpapi_la"
# in the copy by "libpapi_dynamic_la". The third Perl call adds
# "libpapi-dynamic.la" to the "lib_LTLIBRARIES" line.
cat source/libpapi-dynamic/Makefile.am | perl -e 'my $f = join("", <>); $f =~ s:\s*\\\n\s*: :sm; print $f' | perl -p -e 's:(^libpapi_la(.*)$):$1\nlibpapi_dynamic_la$2:' | perl -p -e 's:(libpapi\.la):$1 libpapi-dynamic.la:' > source/libpapi-dynamic/Makefile.am.new
mv -f source/libpapi-dynamic/Makefile.am.new source/libpapi-dynamic/Makefile.am
# Let library files have a version number
perl -p -i -e 's:\s*-avoid-version::' source/libpapi-lpd/Makefile.am source/libpapi-ipp/Makefile.am
# Move all libraries into libdir (no libraries in libexecdir any more)
perl -p -i -e 's:(libdir\s*=\s*\$\(libexecdir\)):\#$1:' source/libpapi-lpd/Makefile.am source/libpapi-ipp/Makefile.am
perl -p -i -e 's:libexecdir:libdir:g' source/libpapi-dynamic/Makefile.am
# Move lpd-port into /usr/bin
perl -p -i -e 's:libexecdir:bindir:' source/libpapi-lpd/Makefile.am
perl -p -i -e 's:libexec_(PROGRAMS):bin_$1:' source/libpapi-lpd/Makefile.am
perl -p -i -e 's:(SUID_LPD_PORT=\"\$\{)libexecdir(\}/lpd-port\"):$1bindir$2:' configure.in



%build

# Change compiler flags for debugging when in debug mode
%if %debug
export DONT_STRIP=1
export CFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export CXXFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export RPM_OPT_FLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
%endif

##### PAPI

# We have a Subversion version and also have heavily manipulated the
# Makefile.am files, so we must re-generate "configure"
./autogen.sh

%if %{withapache}
WITH_APACHE=" --with-apache=%{_prefix}"
%else
WITH_APACHE=" --without-apache"
%endif
%if %{withruby}
WITH_RUBY=""
%else
WITH_RUBY=" --without-ruby"
%endif

export LDFLAGS="$LDFLAGS -L$RPM_BUILD_DIR/papi/source/libpapi-dynamic/.libs"
export CFLAGS="$CFLAGS -DDEFAULT_PRINT_SERVICE=\\\"ipp\\\""
%configure$WITH_APACHE$WITH_RUBY
make



%install

rm -rf %{buildroot}

# Change compiler flapapi for debugging when in debug mode
%if %debug
export DONT_STRIP=1
export CFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export CXXFLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
export RPM_OPT_FLAGS="`echo %optflags |sed -e 's/-O3/-g/' |sed -e 's/-O2/-g/'`"
%endif

##### PAPI

%makeinstall \
	ruby_sitearchdir=%{buildroot}`ls -d %{_prefix}/lib*/ruby/site_ruby/*/*-linux-gnu*` \
	ruby_sitelibdir=%{buildroot}`ls -d %{_prefix}/lib*/ruby/site_ruby/*`

# entry for xinetd (disabled by default)
install -d %{buildroot}%{_sysconfdir}/xinetd.d
cat <<EOF >%{buildroot}%{_sysconfdir}/xinetd.d/papi-lpd
# default: off
# description: The cups-lpd mini daemon enable cups accepting jobs from a \
#       remote LPD client (for example a machine with an older distribution \
#       than Linux Mandrake 7.2 or with a commercial Unix).
service papi-lpd
{
        socket_type     = stream
        protocol        = tcp
        wait            = no
        user            = lp
        group           = sys
        server          = %{_sbindir}/in.lpd
        passenv         =
        env             =
        disable         = yes
}
EOF

# Prepare the commands conflicting with actual print spooling systems
# for the update-alternatives treatment
# Move also the admin man pages into chapter 8
install -d %{buildroot}%{_mandir}/man8
( cd %{buildroot}%{_bindir}
  mv lpr lpr-papi
  mv lpq lpq-papi
  mv lprm lprm-papi
  mv lp lp-papi
  mv cancel cancel-papi
  mv lpstat lpstat-papi
)
( cd %{buildroot}%{_sbindir}
  mv accept accept-papi
  mv disable disable-papi
  mv enable enable-papi
  mv lpc lpc-papi
  mv lpmove lpmove-papi
  mv reject reject-papi
)
( cd %{buildroot}%{_mandir}/man1
  mv ../man*/lpr.* lpr-papi.1
  mv ../man*/lpq.* lpq-papi.1
  mv ../man*/lprm.* lprm-papi.1
  mv ../man*/lp.* lp-papi.1
  mv ../man*/cancel.* cancel-papi.1
  mv ../man*/lpstat.* lpstat-papi.1
)
( cd %{buildroot}%{_mandir}/man8
  mv ../man*/accept.* accept-papi.8
  mv ../man*/disable.* disable-papi.8
  mv ../man*/enable.* enable-papi.8
  mv ../man*/lpc.* lpc-papi.8
  mv ../man*/lpmove.* lpmove-papi.8
  mv ../man*/reject.* reject-papi.8
)

# Remove the /usr/lib/libpapi.* files, as at their place we use symlinks
# generated by update-alternatives. These symlinks point to the libpapi
# library we want to use for our actual printing system.
( cd %{buildroot}%{_libdir}
  rm -f libpapi.*
)

# Install documentation
install -d %{buildroot}%{_docdir}/%{name}-%{version}
mv %{buildroot}%{_datadir}/examples %{buildroot}/%{_docdir}/%{name}-%{version}
cp docs/*.pdf docs/README* %{buildroot}/%{_docdir}/%{name}-%{version}
cp README %{buildroot}/%{_docdir}/%{name}-%{version}/README.devel
cp *.txt ChangeLog INSTALL LICENSE TODO %{buildroot}/%{_docdir}/%{name}-%{version}



##### PRE/POSTINSTALL SCRIPTS

%post -n %{libpapi}
# Set up update-alternatives entries
libversion=`\ls %{_libdir}/libpapi-dynamic.so.* | egrep 'so\.%{papimajor}\.[0-9]+\.[0-9]+$' | perl -p -e 's:^.*\.so\.::'`
%{_sbindir}/update-alternatives --install %{_libdir}/libpapi.so libpapi.so %{_libdir}/libpapi-dynamic.so 10 --slave %{_libdir}/libpapi.so.%{papimajor} libpapi.so.%{papimajor} %{_libdir}/libpapi-dynamic.so.%{papimajor} --slave %{_libdir}/libpapi.so.$libversion libpapi.so.$libversion %{_libdir}/libpapi-dynamic.so.$libversion
%{_sbindir}/update-alternatives --install %{_libdir}/libpapi.so libpapi.so %{_libdir}/libpapi-ipp.so 30 --slave %{_libdir}/libpapi.so.%{papimajor} libpapi.so.%{papimajor} %{_libdir}/libpapi-ipp.so.%{papimajor} --slave %{_libdir}/libpapi.so.$libversion libpapi.so.$libversion %{_libdir}/libpapi-ipp.so.$libversion
%{_sbindir}/update-alternatives --install %{_libdir}/libpapi.so libpapi.so %{_libdir}/libpapi-lpd.so 20 --slave %{_libdir}/libpapi.so.%{papimajor} libpapi.so.%{papimajor} %{_libdir}/libpapi-lpd.so.%{papimajor} --slave %{_libdir}/libpapi.so.$libversion libpapi.so.$libversion %{_libdir}/libpapi-lpd.so.$libversion

/sbin/ldconfig



%post commands
# Set up update-alternatives entries
%{_sbindir}/update-alternatives --install %{_bindir}/lpr lpr %{_bindir}/lpr-papi 100 --slave %{_mandir}/man1/lpr.1.bz2 lpr.1.bz2 %{_mandir}/man1/lpr-papi.1.bz2
%{_sbindir}/update-alternatives --install %{_bindir}/lpq lpq %{_bindir}/lpq-papi 100 --slave %{_mandir}/man1/lpq.1.bz2 lpq.1.bz2 %{_mandir}/man1/lpq-papi.1.bz2
%{_sbindir}/update-alternatives --install %{_bindir}/lprm lprm %{_bindir}/lprm-papi 100 --slave %{_mandir}/man1/lprm.1.bz2 lprm.1.bz2 %{_mandir}/man1/lprm-papi.1.bz2
%{_sbindir}/update-alternatives --install %{_bindir}/lp lp %{_bindir}/lp-papi 100 --slave %{_mandir}/man1/lp.1.bz2 lp.1.bz2 %{_mandir}/man1/lp-papi.1.bz2
%{_sbindir}/update-alternatives --install %{_bindir}/cancel cancel %{_bindir}/cancel-papi 100 --slave %{_mandir}/man1/cancel.1.bz2 cancel.1.bz2 %{_mandir}/man1/cancel-papi.1.bz2
%{_sbindir}/update-alternatives --install %{_bindir}/lpstat lpstat %{_bindir}/lpstat-papi 100 --slave %{_mandir}/man1/lpstat.1.bz2 lpstat.1.bz2 %{_mandir}/man1/lpstat-papi.1.bz2
%{_sbindir}/update-alternatives --install %{_sbindir}/accept accept %{_sbindir}/accept-papi 100 --slave %{_mandir}/man8/accept.8.bz2 accept.8.bz2 %{_mandir}/man8/accept-papi.8.bz2
%{_sbindir}/update-alternatives --install %{_sbindir}/disable disable %{_sbindir}/disable-papi 100 --slave %{_mandir}/man8/disable.8.bz2 disable.8.bz2 %{_mandir}/man8/disable-papi.8.bz2
%{_sbindir}/update-alternatives --install %{_sbindir}/enable enable %{_sbindir}/enable-papi 100 --slave %{_mandir}/man8/enable.8.bz2 enable.8.bz2 %{_mandir}/man8/enable-papi.8.bz2
%{_sbindir}/update-alternatives --install %{_sbindir}/lpc lpc %{_sbindir}/lpc-papi 100 --slave %{_mandir}/man8/lpc.8.bz2 lpc.8.bz2 %{_mandir}/man8/lpc-papi.8.bz2
%{_sbindir}/update-alternatives --install %{_sbindir}/lpmove lpmove %{_sbindir}/lpmove-papi 100 --slave %{_mandir}/man8/lpmove.8.bz2 lpmove.8.bz2 %{_mandir}/man8/lpmove-papi.8.bz2
%{_sbindir}/update-alternatives --install %{_sbindir}/reject reject %{_sbindir}/reject-papi 100 --slave %{_mandir}/man8/reject.8.bz2 reject.8.bz2 %{_mandir}/man8/reject-papi.8.bz2



%preun -n %{libpapi}
if [ "$1" = 0 ]; then
  # Remove update-alternatives entries
  %{_sbindir}/update-alternatives --remove libpapi.so %{_libdir}/libpapi-dynamic.so
  %{_sbindir}/update-alternatives --remove libpapi.so %{_libdir}/libpapi-ipp.so
  %{_sbindir}/update-alternatives --remove libpapi.so %{_libdir}/libpapi-lpd.so
fi



%preun commands
if [ "$1" = 0 ]; then
  # Remove update-alternatives entries
  %{_sbindir}/update-alternatives --remove lpr %{_bindir}/lpr-papi
  %{_sbindir}/update-alternatives --remove lpq %{_bindir}/lpq-papi
  %{_sbindir}/update-alternatives --remove lprm %{_bindir}/lprm-papi
  %{_sbindir}/update-alternatives --remove lp %{_bindir}/lp-papi
  %{_sbindir}/update-alternatives --remove cancel %{_bindir}/cancel-papi
  %{_sbindir}/update-alternatives --remove lpstat %{_bindir}/lpstat-papi
  %{_sbindir}/update-alternatives --remove accept %{_sbindir}/accept-papi
  %{_sbindir}/update-alternatives --remove disable %{_sbindir}/disable-papi
  %{_sbindir}/update-alternatives --remove enable %{_sbindir}/enable-papi
  %{_sbindir}/update-alternatives --remove lpc %{_sbindir}/lpc-papi
  %{_sbindir}/update-alternatives --remove lpmove %{_sbindir}/lpmove-papi
  %{_sbindir}/update-alternatives --remove reject %{_sbindir}/reject-papi
fi



%postun -n %{libpapi} -p /sbin/ldconfig



%clean
rm -rf %{buildroot}



##### FILES

%files common
%defattr(-,root,root)
# This must be SUID root to access LPD port 515
%attr(4755,root,root) %{_bindir}/lpd-port
%{_mandir}/man*/psm-*
%{_mandir}/man4/*
%{_docdir}/%{name}-%{version}

%files commands
%defattr(-,root,root)
%{_bindir}/*papi
%{_sbindir}/*papi
%{_sbindir}/in.lpd
%{_mandir}/man*/*-papi.[0-9n]*
%attr(644,root,root) %config(noreplace) %{_sysconfdir}/xinetd.d/papi-lpd

%files utils
%defattr(-,root,root)
%{_bindir}/add-modify-printer
%{_bindir}/ipp
%{_bindir}/print-test
%{_bindir}/printer-query
%{_bindir}/printers-list
%{_bindir}/remove-printer

%if %{withruby}
%files -n ruby-papi
%defattr(-,root,root)
%{_prefix}/lib*/ruby/site_ruby/*/*.rb
%{_prefix}/lib*/ruby/site_ruby/*/*/*.so.*

%files -n ruby-papi-devel
%defattr(-,root,root)
%{_prefix}/lib*/ruby/site_ruby/*/*/*.so
%{_prefix}/lib*/ruby/site_ruby/*/*/*.*a
%endif

%if %{withapache}
%files apache
%defattr(-,root,root)

%endif

%files -n %{libpapi}
%defattr(-,root,root)
%{_libdir}/lib*.so.*
%{_libdir}/lib*.so

%files -n %{libpapi}-devel
%defattr(-,root,root)
%{_libdir}/lib*.la
%{_libdir}/pkgconfig/*
%{_includedir}/papi
