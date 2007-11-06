#
# TODO:
#		- utils/scripts, eagleconfig
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	up		# don't build UP module
%bcond_without	userspace	# don't build userspace tools
%bcond_without	cmvs
%bcond_with	verbose		# verbose build (V=1)
%bcond_with	grsec_kernel	# build for kernel-grsecurity

%ifarch sparc
# no USB in sparc(32) kernel; just build userspace to use with sparc64 kernel
%undefine	with_kernel
%endif

%if %{without kernel}
%undefine	with_dist_kernel
%endif
%if %{with kernel} && %{with dist_kernel} && %{with grsec_kernel}
%define	alt_kernel	grsecurity
%endif
%if "%{_alt_kernel}" != "%{nil}"
%undefine	with_userspace
%endif

%define		_rel	57
%define		pname	eagle-usb
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...) modems
Summary(pl):	Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st 800/840/908/...)
Name:		eagle-usb
Version:	2.3.3
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://download.gna.org/eagleusb/eagle-usb-2.3.0/%{pname}-%{version}.tar.bz2
# Source0-md5:	6c961a5022274aff870e49e2f0f922fc
Patch1:		%{pname}-eu_types.patch
Patch2:		%{pname}-vpivci-info.patch
Patch3:		%{pname}-opt.patch
Patch4:		%{pname}-signal.patch
Patch5:		%{pname}-usb_kill_urb.patch
Patch6:		%{pname}-kernel_sources_checking_hack.patch
# Workaround for obsolete kernel API. To be removed...
Patch7:		%{pname}-spin_lock_unlocked.patch
Patch8:		%{pname}-kill_owner.patch
Patch9:		%{pname}-module_param.patch
URL:		http://gna.org/projects/eagleusb/
BuildRequires:	autoconf
BuildRequires:	automake
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel%{_alt_kernel}-module-build >= 3:2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.330
%endif
BuildRequires:	SysVinit
BuildRequires:	net-tools
Requires:	ppp >= 2.4.1
Obsoletes:	eagle-utils
Conflicts:	eagle-usb24
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...)
modems.

%description -l pl
Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st
800/840/908/...).

%package -n kernel%{_alt_kernel}-usb-eagle
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...) modems
Summary(pl):	Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st 800/840/908/...)
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Provides:	kernel-usb(eagle) = %{version}-%{_rel}
%if "%{_alt_kernel}" == "%{_nil}"
Obsoletes:	kernel-usb-fast800
%endif

%description -n kernel%{_alt_kernel}-usb-eagle
Linux driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...)
modems.

%description -n kernel%{_alt_kernel}-usb-eagle -l pl
Sterownik dla Linuksa do modemów Eagle 8051 Analog (sagem f@st
800/840/908/...).

%package -n kernel%{_alt_kernel}-smp-usb-eagle
Summary:	Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...) modems
Summary(pl):	Sterownik dla Linuksa SMP do modemów Eagle 8051 Analog (sagem f@st 800/840/908/...)
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Provides:	kernel-usb(eagle) = %{version}-%{_rel}
%if "%{_alt_kernel}" == "%{_nil}"
Obsoletes:	kernel-smp-usb-fast800
%endif

%description -n kernel%{_alt_kernel}-smp-usb-eagle
Linux SMP driver for the Eagle 8051 Analog (sagem f@st
800/840/908/...) modems.

%description -n kernel%{_alt_kernel}-smp-usb-eagle -l pl
Sterownik dla Linuksa SMP do modemów Eagle 8051 Analog (sagem f@st
800/840/908/...).

%prep
%setup -q
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p1
%patch5 -p1
%patch6 -p1
%patch7 -p1
%patch8 -p1
%patch9 -p1

%ifnarch %{ix86}
# invalid not only for ppc
sed -i 's/-mpreferred-stack-boundary=2//' driver/Makefile
%endif

%build
%if %{with kernel}
%build_kernel_modules -C driver -m eagle-usb \
	USE_CMVS=%{?with_cmvs:1}%{!?with_cmvs:0}
%endif

%if %{with userspace}
%{__aclocal} -I .
%{__autoconf}
%configure \
	%{!?with_cmvs:--disable-cmvs} \
	--with-dsp-dir=%{_datadir}/misc

%{__make} -C driver/firmware \
	CC="%{__cc}" \
	OPT="%{rpmcflags}"
%{__make} -C driver/user \
	CC="%{__cc}" \
	OPT="%{rpmcflags}"
%{__make} -C pppoa \
	CC="%{__cc}" \
	OPT="%{rpmcflags}"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
%install_kernel_modules -m driver/eagle-usb -d kernel/drivers/usb/net
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{analog,hotplug,ppp} \
	$RPM_BUILD_ROOT{%{_sbindir},%{_libdir}/hotplug/eagle}
%{__make} -C driver/firmware install \
	EU_DSP_DIR=$RPM_BUILD_ROOT%{_datadir}/misc
%{__make} -C driver/user install \
	EU_DIR=$RPM_BUILD_ROOT%{_sysconfdir}/eagle-usb \
	EU_SCRIPT_DIR=$RPM_BUILD_ROOT%{_sysconfdir}/eagle-usb \
	SBINDIR=$RPM_BUILD_ROOT%{_sbindir}
mv $RPM_BUILD_ROOT%{_sysconfdir}/eagle-usb/eagle-usb.conf{.template,}
%{__make} -C pppoa install \
	SBINDIR=$RPM_BUILD_ROOT%{_sbindir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel%{_alt_kernel}-usb-eagle
%depmod %{_kernel_ver}

%postun -n kernel%{_alt_kernel}-usb-eagle
%depmod %{_kernel_ver}

%post -n kernel%{_alt_kernel}-smp-usb-eagle
%depmod %{_kernel_ver}smp

%postun -n kernel%{_alt_kernel}-smp-usb-eagle
%depmod %{_kernel_ver}smp

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README
%dir %{_sysconfdir}/eagle-usb
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/eagle-usb/eagle-usb.conf
%attr(640,root,root) %config(noreplace) %verify(not md5 mtime size) %{_sysconfdir}/eagle-usb/*.txt
%attr(755,root,root) %{_sbindir}/*
%{_datadir}/misc/*.bin
%endif

%if %{with kernel}
%if %{with up} || %{without dist_kernel}
%files -n kernel%{_alt_kernel}-usb-eagle
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net/*.ko*
%endif

%if %{with smp} && %{with dist_kernel}
%files -n kernel%{_alt_kernel}-smp-usb-eagle
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/net/*.ko*
%endif
%endif
