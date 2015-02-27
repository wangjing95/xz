%global compat_ver xz-4.999.9beta

# Not needed for f21+ and probably RHEL8+
%{!?_licensedir:%global license %%doc}

Summary:	LZMA compression utilities
Name:		xz
Version:	5.2.1
Release:	1%{?dist}

# Scripts xz{grep,diff,less,more} and symlinks (copied from gzip) are
# GPLv2+, binaries are Public Domain (linked against LGPL getopt_long but its
# OK), documentation is Public Domain.
License:	GPLv2+ and Public Domain
Group:		Applications/File
# official upstream release
Source0:	http://tukaani.org/%{name}/%{name}-%{version}.tar.xz
# source created as "make dist" in checked out GIT tree
Source1:	%{compat_ver}.20100401git.tar.bz2

Source100:	colorxzgrep.sh
Source101:	colorxzgrep.csh

URL:		http://tukaani.org/%{name}/
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}

# For /usr/libexec/grepconf.sh (RHBZ#1189120).
# Unfortunately F21 has a newer version of grep which doesn't
# have grepconf, but we're only concerned with F22 here.
Requires:	grep >= 2.20-5


%description
XZ Utils are an attempt to make LZMA compression easy to use on free (as in
freedom) operating systems. This is achieved by providing tools and libraries
which are similar to use than the equivalents of the most popular existing
compression algorithms.

LZMA is a general purpose compression algorithm designed by Igor Pavlov as
part of 7-Zip. It provides high compression ratio while keeping the
decompression speed fast.

%package 	libs
Summary:	Libraries for decoding LZMA compression
Group:		System Environment/Libraries
License:	Public Domain

%description 	libs
Libraries for decoding files compressed with LZMA or XZ utils.

%package 	static
Summary:	Statically linked library for decoding LZMA compression
Group:		System Environment/Libraries
License:	Public Domain

%description 	static
Statically linked library for decoding files compressed with LZMA or
XZ utils.  Most users should *not* install this.

%package 	compat-libs
Summary:	Compatibility libraries for decoding LZMA compression
Group:		System Environment/Libraries
License:	Public Domain

%description 	compat-libs
Compatibility libraries for decoding files compressed with LZMA or XZ utils.
This particular package ships libraries from %{compat_ver} as of 1st of April 2010.

%package 	devel
Summary:	Devel libraries & headers for liblzma
Group:		Development/Libraries
License:	Public Domain
Requires:	%{name}-libs%{?_isa} = %{version}-%{release}
Requires:	pkgconfig

%description	devel
Devel libraries and headers for liblzma.

%package 	lzma-compat
Summary:	Older LZMA format compatibility binaries
Group:		Development/Libraries
# Just a set of symlinks to 'xz' + two Public Domain binaries.
License:	Public Domain
Requires:	%{name}%{?_isa} = %{version}-%{release}
Obsoletes:	lzma < %{version}
Provides:	lzma = %{version}

%description	lzma-compat
The lzma-compat package contains compatibility links for older
commands that deal with the older LZMA format.

%prep
%setup -q -a1

for i in `find . -name config.sub`; do
  perl -pi -e "s/ppc64-\*/ppc64-\* \| ppc64p7-\*/" $i
done

%build
CFLAGS="%{optflags} -D_FILE_OFFSET_BITS=64"
%ifarch %{power64}
    CFLAGS=`echo $CFLAGS | xargs -n 1 | sed 's|^-O2$|-O3|g' | xargs -n 100`
%endif
export CFLAGS

%configure
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}

pushd %{compat_ver}
%configure
sed -i 's|^hardcode_libdir_flag_spec=.*|hardcode_libdir_flag_spec=""|g' libtool
sed -i 's|^runpath_var=LD_RUN_PATH|runpath_var=DIE_RPATH_DIE|g' libtool
make %{?_smp_mflags}
popd

%install
make install DESTDIR=%{buildroot}
rm -f %{buildroot}%{_libdir}/*.la

cp -r %{compat_ver}/src/liblzma/.libs/liblzma.so.0* %{buildroot}%{_libdir}

# xzgrep colorization
%global profiledir %{_sysconfdir}/profile.d
mkdir -p %{buildroot}%{profiledir}
install -p -m 644 %{SOURCE100} %{buildroot}%{profiledir}
install -p -m 644 %{SOURCE101} %{buildroot}%{profiledir}

%find_lang %name

%check
LD_LIBRARY_PATH=$PWD/src/liblzma/.libs make check

%post libs -p /sbin/ldconfig

%postun libs -p /sbin/ldconfig

%post compat-libs -p /sbin/ldconfig

%postun compat-libs -p /sbin/ldconfig

%files -f %{name}.lang
%license %{_pkgdocdir}/COPYING*
%doc %{_pkgdocdir}
%exclude %_pkgdocdir/examples*
%{_bindir}/*xz*
%{_mandir}/man1/*xz*
%{profiledir}/*

%files libs
%license %{_pkgdocdir}/COPYING
%{_libdir}/lib*.so.5*

%files static
%license %{_pkgdocdir}/COPYING
%{_libdir}/liblzma.a

%files compat-libs
%license %{_pkgdocdir}/COPYING
%{_libdir}/lib*.so.0*

%files devel
%dir %{_includedir}/lzma
%{_includedir}/lzma/*.h
%{_includedir}/lzma.h
%{_libdir}/*.so
%{_libdir}/pkgconfig/liblzma.pc
%doc %_pkgdocdir/examples*

%files lzma-compat
%{_bindir}/*lz*
%{_mandir}/man1/*lz*

%changelog
* Fri Feb 27 2015 Pavel Raiskup <praiskup@redhat.com> - 5.2.1-1
- bugfix rebase to 5.2.1, per release notes
  http://www.mail-archive.com/xz-devel@tukaani.org/msg00226.html

* Wed Feb 04 2015 Richard W.M. Jones <rjones@redhat.com> - 5.2.0-2
- Depend on grep that contains grepconf.sh (#1189120)

* Tue Dec 23 2014 Pavel Raiskup <praiskup@redhat.com> - 5.2.0-1
- rebase per upstream release notes (#1023718)
  http://www.mail-archive.com/xz-devel@tukaani.org/msg00216.html
- fedora-review fixes, documentation/license fixes in spec

* Tue Aug 26 2014 Pavel Raiskup <praiskup@redhat.com> - 5.1.2-15alpha
- xz*grep's output is colored iff grep's is (#1034846)

* Mon Aug 18 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.2-14alpha
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_22_Mass_Rebuild

* Wed Aug  6 2014 Tom Callaway <spot@fedoraproject.org> - 5.1.2-13alpha
- fix license handling

* Fri Jun 13 2014 Pavel Raiskup <praiskup@redhat.com> - 5.1.2-12alpha
- xzgrep: return 0 when at least one file matches (#1109122)

* Sun Jun 08 2014 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.2-11alpha
- Rebuilt for https://fedoraproject.org/wiki/Fedora_21_Mass_Rebuild

* Sat May 31 2014 Peter Robinson <pbrobinson@fedoraproject.org> 5.1.2-10alpha
- Drop ChangeLog, it's big and the excitement is summarised in NEWS

* Fri May 16 2014 Richard W.M. Jones <rjones@redhat.com> - 5.1.2-9alpha
- Add a -static subpackage (see RHBZ#547011).

* Wed Apr 02 2014 Pavel Raiskup <praiskup@redhat.com> - 5.1.2-8alpha
- add _isa requirements where appropriate
- better check the version of less binary (#1015924)

* Fri Jan 10 2014 Pavel Raiskup <praiskup@redhat.com> - 5.1.2-7alpha
- build with -O3 on ppc64 (private #1051078)

* Sun Aug 04 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.2-6alpha
- Rebuilt for https://fedoraproject.org/wiki/Fedora_20_Mass_Rebuild

* Tue Apr 09 2013 Pavel Raiskup <praiskup@redhat.com> - 5.1.2-5alpha
- fix manual page inconsistencies with help output (private #948533)
- enable/fix the 'xzgrep -h' (private #850898)

* Thu Feb 21 2013 Karsten Hopp <karsten@redhat.com> 5.1.2-4alpha
- add support for ppc64p7 arch (Power7 optimized)

* Fri Feb 15 2013 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.2-3alpha
- Rebuilt for https://fedoraproject.org/wiki/Fedora_19_Mass_Rebuild

* Sun Jul 22 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.2-2alpha
- Rebuilt for https://fedoraproject.org/wiki/Fedora_18_Mass_Rebuild

* Thu Jul 05 2012 Jindrich Novy <jnovy@redhat.com> 5.1.2alpha-1
- update to 5.1.2alpha

* Sat Jan 14 2012 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.1.1-2alpha
- Rebuilt for https://fedoraproject.org/wiki/Fedora_17_Mass_Rebuild

* Sun Oct 16 2011 Jindrich Novy <jnovy@redhat.com> 5.1.1alpha-1
- update to 5.1.1alpha

* Mon Jun 20 2011 Jindrich Novy <jnovy@redhat.com> 5.0.3-2
- better to have upstream tarballs in different formats than XZ
  to allow bootstrapping (#714765)

* Mon May 23 2011 Jindrich Novy <jnovy@redhat.com> 5.0.3-1
- update to 5.0.3

* Mon Apr 04 2011 Jindrich Novy <jnovy@redhat.com> 5.0.2-1
- update to 5.0.2

* Tue Feb 08 2011 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 5.0.1-2
- Rebuilt for https://fedoraproject.org/wiki/Fedora_15_Mass_Rebuild

* Sat Jan 29 2011 Jindrich Novy <jnovy@redhat.com> 5.0.1-1
- update to 5.0.1

* Tue Oct 26 2010 Jindrich Novy <jnovy@redhat.com> 5.0.0-4
- call ldconfig for compat-libs and fix description

* Mon Oct 25 2010 Jindrich Novy <jnovy@redhat.com> 5.0.0-3
- introduce compat-libs subpackage with older soname to
  resolve problems with soname bump and for packages requiring
  older xz-4.999.9beta

* Mon Oct 25 2010 Jindrich Novy <jnovy@redhat.com> 5.0.0-2
- rebuild

* Mon Oct 25 2010 Jindrich Novy <jnovy@redhat.com> 5.0.0-1
- update to the new upstream release

* Sat Oct 16 2010 Jindrich Novy <jnovy@redhat.com> 4.999.9-0.3.beta.212.gacbc
- update to latest git snapshot

* Thu Apr 01 2010 Jindrich Novy <jnovy@redhat.com> 4.999.9-0.2.20100401.beta
- sync with upstream (#578925)

* Thu Feb 18 2010 Jindrich Novy <jnovy@redhat.com> 4.999.9-0.2.20091007.beta
- move xz man pages to main package, leave lzma ones where they belong (#566484)

* Wed Oct 07 2009 Jindrich Novy <jnovy@redhat.com> 4.999.9-0.1.20091007.beta
- sync with upstream again

* Fri Oct 02 2009 Jindrich Novy <jnovy@redhat.com> 4.999.9-0.1.20091002.beta
- sync with upstream to generate the same archives on machines with different
  endianess

* Fri Aug 28 2009 Jindrich Novy <jnovy@redhat.com> 4.999.9-0.1.beta
- update to 4.999.9beta

* Mon Aug 17 2009 Jindrich Novy <jnovy@redhat.com> 4.999.8-0.10.beta.20090817git
- sync with upstream because of #517806

* Tue Aug 04 2009 Jindrich Novy <jnovy@redhat.com> 4.999.8-0.9.beta.20090804git
- update to the latest GIT snapshot

* Mon Jul 27 2009 Fedora Release Engineering <rel-eng@lists.fedoraproject.org> - 4.999.8-0.8.beta
- Rebuilt for https://fedoraproject.org/wiki/Fedora_12_Mass_Rebuild

* Fri Jul 17 2009 Bill Nottingham <notting@redhat.com> 4.999.8-0.7.beta
- tweak summary
- add %%check section (<tibbs@math.uh.edu>)
 
* Thu Jul 09 2009 Bill Nottingham <notting@redhat.com> 4.999.8-0.6.beta
- fix release versioning to match guidelines
- fix up lzma-compat summary/description
- tweak licensing

* Mon Jun 22 2009 Jindrich Novy <jnovy@redhat.com> 4.999.8beta-0.5
- introduce lzma-compat subpackage

* Fri Jun 19 2009 Jindrich Novy <jnovy@redhat.com> 4.999.8beta-0.4
- try to not to conflict with lzma

* Thu Jun 18 2009 Jindrich Novy <jnovy@redhat.com> 4.999.8beta-0.3
- obsolete but don't provide lzma, they are largely incompatible
- put beta to Release

* Wed Jun 17 2009 Jindrich Novy <jnovy@redhat.com> 4.999.8beta-0.2
- obsolete old lzma
- add Requires: pkgconfig

* Tue Jun 16 2009 Jindrich Novy <jnovy@redhat.com> 4.999.8beta-0.1
- package XZ Utils, based on LZMA Utils packaged by Per Patrice Bouchand
