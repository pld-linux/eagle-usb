%bcond_without	dist_kernel
%bcond_without	smp
%define		_snap	040113
%define		_orig_name	eagle
%define		no_install_post_compress_modules 1
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st 800...)
Name:		eagle
Version:	1.9.3
Release:	0.%{_snap}.1
License:	GPL
Group:		Base/Kernel
#Source0:	http://fast800.tuxfamily.org/pub/IMG/gz/%{name}-%{version}.tar.gz
Source0:	http://ep09.pld-linux.org/~djurban/pld/%{name}-usb-%{_snap}.tar.bz2
# Source0-md5:	2d15ce31e185042b4971733b8b345a88	
Patch0:		%{name}-Makefile.patch
URL:		http://fast800.tuxfamily.org/
%{?with_dist_kernel:BuildRequires: kernel-headers }
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
Requires(post,postun):	/sbin/depmod
Requires:	ppp >= 2.4.1
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
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod


%description -n kernel-smp-usb-%{_orig_name}
Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -n kernel-smp-usb-%{_orig_name} -l pl
Sterownik dla Linuksa SMP do modemów Eagle 8051 Analog (sagem f@st
800...).

%prep
%setup -q -n eagle-usb 
%patch0 -p1

%build
%{__aclocal} -I .
%{__autoconf}

%configure 
make -C pppoa; make -C driver/firmware; make -C driver/user

cd driver
ln -sf %{_kernelsrcdir}/config-up .config
install -d include/linux
ln -sf %{_kernelsrcdir}/include/asm-%{_arch} include/asm
ln -sf %{_kernelsrcdir}/include/linux/autoconf.h include/linux/autoconf.h
%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 modules
mv eagle-usb.ko eagle-usb.ko-done

ln -sf %{_kernelsrcdir}/config-smp .config

%{__make} -C %{_kernelsrcdir} SUBDIRS=$PWD O=$PWD V=1 clean modules

%install
rm -rf $RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT{%{_sysconfdir}/eagle-usb,%{_sbindir},%{_datadir}/misc}

install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/usb/net

cp pppoa/pppoa $RPM_BUILD_ROOT%{_sbindir}/
cp driver/firmware/*.bin $RPM_BUILD_ROOT%{_datadir}/misc/

cp driver/user/eagle-usb.conf $RPM_BUILD_ROOT%{_sysconfdir}/eagle-usb/

install driver/user/eaglestat $RPM_BUILD_ROOT%{_sbindir}
install driver/user/eaglectrl $RPM_BUILD_ROOT%{_sbindir}

install driver/eagle-usb.ko-done $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net/eagle-usb.ko

install driver/eagle-usb.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/net/

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


%files
%defattr(644,root,root,755)
%doc BUGS Changelog FAQ TODO readme.txt
%dir %{_sysconfdir}/eagle-usb
%config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/eagle-usb/eagle-usb.conf
%attr(755,root,root) %{_sbindir}/
%{_datadir}/misc/*.bin

%files -n kernel-usb-%{_orig_name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net/*

%if %{with smp}
%files -n kernel-smp-usb-%{_orig_name}
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/*
%endif
