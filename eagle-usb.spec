#
# Conditional build:
# _without_dist_kernel		without distribution kernel
#
%define		_orig_name	fast800
%define		_update_usb /sbin/update-usb.usermap
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st 800...)
Name:		eagle-utils
Version:	1.0.4
%define	_rel	7
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://fast800.tuxfamily.org/pub/IMG/gz/eagle-%{version}.tar.gz
# Source0-md5:	fc52cf1eff6ab9f20e9c2cb3e7e2f1e8
Patch0:		eagle-Makefile.patch
Patch1:		eagle-firmware.patch
URL:		http://fast800.tuxfamily.org/
%{!?_without_dist_kernel:BuildRequires:	kernel-headers }
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
Requires(post,postun):	/sbin/depmod
Requires:	ppp >= 2.4.1
%{!?_without_dist_kernel:Requires:	kernel-usb-%{_orig_name} = %{version}-%{_rel}@%{_kernel_ver_str}}
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
%{!?_without_dist_kernel:%requires_releq_kernel_up}
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
%{!?_without_dist_kernel:%requires_releq_kernel_smp}
%{!?_without_dist_kernel:Provides:	kernel-usb-%{_orig_name}}
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

%build
install -d kernel-{up,smp}

# UP
%{__make} clean
%{__make} -C driver \
	CC=%{__cc} \
%ifarch %{ix86} 
	OPT="-I/usr/src/linux/include/asm-i386/mach-default" \
%endif
	KERNELSRC="%{_kernelsrcdir}"
install driver/adiusbadsl.o kernel-up

# SMP
CONFIG_SMP=y; export CONFIG_SMP
%{__make} -C driver clean
%{__make} -C driver \
	CC=%{__cc} \
%ifarch %{ix86} 
	OPT="-I/usr/src/linux/include/asm-i386/mach-default -DSMP -D__SMP__" \
%else
	OPT="-D__SMP__ -DSMP" \
%endif
	KERNELSRC="%{_kernelsrcdir}"
install driver/adiusbadsl.o kernel-smp/

# Rest
%{__make} \
	KERNELSRC="%{_kernelsrcdir}"

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb
install -d $RPM_BUILD_ROOT/etc/{analog,hotplug,ppp}
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_libdir}/hotplug/eagle}

install kernel-up/*.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb
install kernel-smp/*.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb

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

%files -n kernel-usb-%{_orig_name}
%defattr(644,root,root,755)
%doc readme.txt
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/*

%files -n kernel-smp-usb-%{_orig_name}
%defattr(644,root,root,755)
%doc readme.txt
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/*
