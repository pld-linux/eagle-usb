#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
#
%define		_orig_name	eagle
%define		no_install_post_compress_modules 1
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st 800...)
Name:		eagle-usb
Version:	1.9.6
Release:	0.1
License:	GPL
Group:		Base/Kernel
Source0: 	http://dl.sourceforge.net/sourceforge/eagle-usb/%{name}-%{version}.tar.bz2
# Source0-md5:	d2d94f396132e34417fa1b26bcde7287
Patch0:		eagle-Makefile.patch
URL:		http://fast800.tuxfamily.org/
BuildRequires:	autoconf
BuildRequires:	automake
%if %{with kernel}
%{?with_dist_kernel:BuildRequires: kernel-module-build >= 2.6}
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
%endif
Requires:	ppp >= 2.4.1
Obsoletes:	eagle-utils
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -l pl
Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st
800...).

%package -n kernel-usb-%{_orig_name}
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st 800...)
Release:	%{_snap}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod

%description -n kernel-usb-%{_orig_name}
Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -n kernel-usb-%{_orig_name} -l pl
Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st
800...).

%package -n kernel-smp-usb-%{_orig_name}
Summary:	Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa SMP do modemów Eagle 8051 Analog (sagem f@st 800...)
Release:	%{_snap}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-usb-%{_orig_name}
Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -n kernel-smp-usb-%{_orig_name} -l pl
Sterownik dla Linuksa SMP do modemów Eagle 8051 Analog (sagem f@st
800...).

%prep
%setup -q 
%patch0 -p1

%build
%{__aclocal} -I .
%{__autoconf}

%configure
%if %{with userspace}
%{__make} -C pppoa \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -Wall -ansi -pedantic \$(DEFINES) \$(PATHS)"
%{__make} -C driver/firmware \
	CFLAGS="%{rpmcflags} -pipe -Wall -pedantic"
%{__make} -C driver/user \
	CFLAGS="%{rpmcflags} -Wall -DLINUX -DCONF_DIR=\"%{_sysconfdir}/eagle-usb\" -DBIN_DIR=\"\$(EAGLEUSB_BINDIR)\""
%endif

%if %{with kernel}
cd driver
ln -sf %{_kernelsrcdir}/config-up .config
install -d include/{linux,config}
ln -sf %{_kernelsrcdir}/include/asm-%{_arch} include/asm
ln -sf %{_kernelsrcdir}/include/linux/autoconf.h include/linux/autoconf.h
touch include/config/MARKER
%{__make} -C %{_kernelsrcdir} modules \
	SUBDIRS=$PWD \
	O=$PWD \
	V=1
mv eagle-usb.ko eagle-usb.ko-done

%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 mrproper

ln -sf %{_kernelsrcdir}/config-smp .config
rm -rf  include
install -d include/{linux,config}
ln -sf %{_kernelsrcdir}/include/asm-%{_arch} include/asm
ln -sf %{_kernelsrcdir}/include/linux/autoconf.h include/linux/autoconf.h
touch include/config/MARKER

%{__make} -C %{_kernelsrcdir} modules \
	SUBDIRS=$PWD \
	O=$PWD \
	V=1
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with userspace}
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/eagle-usb,%{_sbindir},%{_datadir}/misc}

install pppoa/pppoa $RPM_BUILD_ROOT%{_sbindir}
install driver/firmware/*.bin $RPM_BUILD_ROOT%{_datadir}/misc
install driver/user/eagle-usb.conf $RPM_BUILD_ROOT%{_sysconfdir}/eagle-usb
install driver/user/eaglestat $RPM_BUILD_ROOT%{_sbindir}
install driver/user/eaglectrl $RPM_BUILD_ROOT%{_sbindir}
%endif

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/usb/net

install driver/eagle-usb.ko-done $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net/eagle-usb.ko
install driver/eagle-usb.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/net
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-usb-%{_orig_name}
%depmod %{_kernel_ver}

%postun -n kernel-usb-%{_orig_name}
%depmod %{_kernel_ver}

%post	-n kernel-smp-usb-%{_orig_name}
%depmod %{_kernel_ver}smp

%postun -n kernel-smp-usb-%{_orig_name}
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc BUGS Changelog FAQ TODO readme.txt
%dir %{_sysconfdir}/eagle-usb
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/eagle-usb/eagle-usb.conf
%attr(755,root,root) %{_sbindir}/*
%{_datadir}/misc/*.bin
%endif

%if %{with kernel}
%files -n kernel-usb-%{_orig_name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net/*

%files -n kernel-smp-usb-%{_orig_name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/*
%endif
