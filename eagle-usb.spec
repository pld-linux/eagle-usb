#
# Conditional build:
# _without_dist_kernel		without distribution kernel
#
%define		_orig_name	fast800
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st 800...)
Name:		eagle
Version:	1.0.4
%define	_rel	4
Release:	%{_rel}
License:	GPL
Group:		Base/Kernel
Source0:	http://fast800.tuxfamily.org/pub/IMG/gz/%{name}-%{version}.tar.gz
# Source0-md5:	fc52cf1eff6ab9f20e9c2cb3e7e2f1e8
Patch0:		%{name}-Makefile.patch
Patch1:		%{name}-firmware.patch
Patch2:		%{name}-stopadsl.patch
URL:		http://fast800.tuxfamily.org/
%{!?_without_dist_kernel:BuildRequires:	kernel-headers }
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
Requires(post,postun):	/sbin/depmod
Requires(post,postun):	/sbin/update-usb.usermap
Requires:	ppp >= 2.4.1
Requires:	hotplug
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
Requires(post,postun):	/sbin/update-usb.usermap

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
Requires(post,postun):	/sbin/depmod
Requires(post,postun):	/sbin/update-usb.usermap

%description -n kernel-smp-usb-%{_orig_name}
Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -n kernel-smp-usb-%{_orig_name} -l pl
Sterownik dla Linuksa SMP do modemów Eagle 8051 Analog (sagem f@st
800...).

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1

%build
install -d kernel-{up,smp}

# UP
%{__make} clean
%{__make} -C driver \
	CC=%{kgcc} \
	KERNELSRC="%{_kernelsrcdir}"
install driver/adiusbadsl.o kernel-up

# SMP
CONFIG_SMP=y; export CONFIG_SMP
%{__make} -C driver clean
%{__make} -e -C driver \
	CC=%{kgcc} \
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
install -d $RPM_BUILD_ROOT{%{_sbindir},%{_libdir}/hotplug/%{name}}

install kernel-up/*.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb
install kernel-smp/*.o $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb

install scripts/hotplug/usb.usermap $RPM_BUILD_ROOT%{_libdir}/hotplug/%{name}

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
[ -x /sbin/update-usb.usermap ] && /sbin/update-usb.usermap

%postun
[ -x /sbin/update-usb.usermap ] && /sbin/update-usb.usermap

%post -n kernel-usb-%{_orig_name}
%depmod %{_kernel_ver}
[ -x /sbin/update-usb.usermap ] && /sbin/update-usb.usermap

%postun -n kernel-usb-%{_orig_name}
%depmod %{_kernel_ver}
[ -x /sbin/update-usb.usermap ] && /sbin/update-usb.usermap

%post	-n kernel-smp-usb-%{_orig_name}
%depmod %{_kernel_ver}smp
[ -x /sbin/update-usb.usermap ] && /sbin/update-usb.usermap

%postun -n kernel-smp-usb-%{_orig_name}
%depmod %{_kernel_ver}smp
[ -x /sbin/update-usb.usermap ] && /sbin/update-usb.usermap

%files
%defattr(644,root,root,755)
%doc BUGS Changelog FAQ TODO readme.txt
%dir %{_sysconfdir}/analog
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/analog/adiusbadsl.conf
%{_sysconfdir}/analog/CMV*
%attr(755,root,root) %{_sysconfdir}/hotplug/usb/*
%{_libdir}/hotplug/%{name}
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
