#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	userspace	# don't build userspace tools
#
%define		_orig_name	fast800
%define		_update_usb /sbin/update-usb.usermap
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st 800...)
Name:		eagle-usb
Version:	1.0.4
%define	_rel	7
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://fast800.tuxfamily.org/pub/IMG/gz/eagle-%{version}.tar.gz
# Source0-md5:	fc52cf1eff6ab9f20e9c2cb3e7e2f1e8
Patch0:		eagle-Makefile.patch
Patch1:		eagle-firmware.patch
Patch2:		%{name}-user2.6.patch
URL:		http://fast800.tuxfamily.org/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-headers < 2.5}
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
%endif
Requires:	ppp >= 2.4.1
%{?with_dist_kernel:Requires:	kernel-usb-%{_orig_name} = %{version}-%{_rel}@%{_kernel_ver_str}}
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
Release:	%{_rel}@%{_kernel_ver_str}
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
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
%{?with_dist_kernel:Provides:	kernel-usb-%{_orig_name}}
Requires(post,postun):	/sbin/depmod

%description -n kernel-smp-usb-%{_orig_name}
Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -n kernel-smp-usb-%{_orig_name} -l pl
Sterownik dla Linuksa SMP do modemów Eagle 8051 Analog (sagem f@st
800...).

%prep
%setup -q -n eagle-%{version}
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
%if %{with kernel}
install -d kernel-{up,smp}

# UP
%{__make} clean
%{__make} -C driver \
	CC=%{kgcc} \
%ifarch %{ix86} 
	OPT="-I/usr/src/linux/include/asm-i386/mach-default" \
%endif
	KERNELSRC="%{_kernelsrcdir}"
install driver/adiusbadsl.o kernel-up

# SMP
CONFIG_SMP=y; export CONFIG_SMP
%{__make} -C driver clean
%{__make} -C driver \
	CC=%{kgcc} \
%ifarch %{ix86} 
	OPT="-I/usr/src/linux/include/asm-i386/mach-default -DSMP -D__SMP__" \
%else
	OPT="-D__SMP__ -DSMP" \
%endif
	KERNELSRC="%{_kernelsrcdir}"
install driver/adiusbadsl.o kernel-smp
%endif

%if %{with userspace}
%{__make} -C driver binaryfirmware adiuser \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -Wall -DLINUX"

%{__make} -C pppoa \
	CC="%{__cc}" \
	CFLAGS="%{rpmcflags} -Wall -ansi \$(DEFINES) \$(PATHS)"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/usb
install kernel-up/*.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb
install kernel-smp/*.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT/etc/{analog,hotplug,ppp} \
	$RPM_BUILD_ROOT{%{_sbindir},%{_libdir}/hotplug/eagle}

install scripts/hotplug/usb.usermap $RPM_BUILD_ROOT%{_libdir}/hotplug/eagle

%{__make} -C driver/firmware install \
	CONFIGDIR=$RPM_BUILD_ROOT/etc/analog \
	DESTDIR=$RPM_BUILD_ROOT

%{__make} -C driver/user install \
	INSTALLDIR=%{_sbindir} \
	CONFIGDIR=/etc/analog \
	DESTDIR=$RPM_BUILD_ROOT

install pppoa/pppoa $RPM_BUILD_ROOT%{_sbindir}
echo 'n


n
n
' | %{__make} -C scripts install \
	INSTALLDIR=%{_sbindir} \
	CONFIGDIR=/etc/analog \
	HOTPLUGDIR=/etc/hotplug \
	PPPDIR=/etc/ppp \
	DESTDIR=$RPM_BUILD_ROOT
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post
if [ -x %{_update_usb} ]; then
	/sbin/update-usb.usermap
fi

%postun
if [ -x %{_update_usb} ]; then
	/sbin/update-usb.usermap
fi

%post -n kernel-usb-%{_orig_name}
%depmod %{_kernel_ver}
if [ -x %{_update_usb} ]; then
	/sbin/update-usb.usermap
fi

%postun -n kernel-usb-%{_orig_name}
%depmod %{_kernel_ver}
if [ -x %{_update_usb} ]; then
	/sbin/update-usb.usermap
fi

%post	-n kernel-smp-usb-%{_orig_name}
%depmod %{_kernel_ver}smp
if [ -x %{_update_usb} ]; then
	/sbin/update-usb.usermap
fi

%postun -n kernel-smp-usb-%{_orig_name}
%depmod %{_kernel_ver}smp
if [ -x %{_update_usb} ]; then
	/sbin/update-usb.usermap
fi

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc BUGS Changelog FAQ TODO readme.txt
%dir %{_sysconfdir}/analog
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/analog/adiusbadsl.conf
%{_sysconfdir}/analog/CMV*
%attr(755,root,root) %{_sysconfdir}/hotplug/usb/*
%{_libdir}/hotplug/eagle
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/ppp/*.adsl
%attr(755,root,root) %{_sbindir}/*
%{_datadir}/misc/*.bin
%endif

%if %{with kernel}
%files -n kernel-usb-%{_orig_name}
%defattr(644,root,root,755)
%doc readme.txt
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/*

%files -n kernel-smp-usb-%{_orig_name}
%defattr(644,root,root,755)
%doc readme.txt
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/*
%endif
