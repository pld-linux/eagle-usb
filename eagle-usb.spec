#
# TODO:
#		- utils/scripts, eagleconfig
#
# Conditional build:
%bcond_without	dist_kernel	# without distribution kernel
%bcond_without	kernel		# don't build kernel modules
%bcond_without	smp		# don't build SMP module
%bcond_without	userspace	# don't build userspace tools
%bcond_with	verbose		# verbose build (V=1)
#
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...) modems
Summary(pl):	Sterownik dla Linuksa do modem�w Eagle 8051 Analog (sagem f@st 800/840/908/...)
Name:		eagle-usb
Version:	1.9.6
%define		_rel	0.6
Release:	%{_rel}
License:	GPL v2
Group:		Base/Kernel
Source0:	http://download.gna.org/eagleusb/%{name}-%{version}.tar.bz2
# Source0-md5:	d2d94f396132e34417fa1b26bcde7287
Patch0:		%{name}-eu_main.patch
Patch1:		%{name}-eu_types.patch
Patch2:		%{name}-ppc.patch
Patch3:		%{name}-vpivci-info.patch
Patch4:		%{name}-wait.patch
URL:		http://gna.org/projects/eagleusb/
%if %{with kernel}
%{?with_dist_kernel:BuildRequires:	kernel-module-build >= 2.6.7}
BuildRequires:	rpmbuild(macros) >= 1.153
%endif
Requires:	ppp >= 2.4.1
Requires:	kernel-usb-eagle = %{version}-%{_rel}@%{_kernel_ver_str}}
Obsoletes:	eagle-utils
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...)
modems.

%description -l pl
Sterownik dla Linuksa do modem�w Eagle 8051 Analog (sagem f@st
800/840/908/...).

%package -n kernel-usb-eagle
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...) modems
Summary(pl):	Sterownik dla Linuksa do modem�w Eagle 8051 Analog (sagem f@st 800/840/908/...)
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod
Obsoletes:	kernel-usb-fast800

%description -n kernel-usb-eagle
Linux driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...)
modems.

%description -n kernel-usb-eagle -l pl
Sterownik dla Linuksa do modem�w Eagle 8051 Analog (sagem f@st
800/840/908/...).

%package -n kernel-smp-usb-eagle
Summary:	Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800/840/908/...) modems
Summary(pl):	Sterownik dla Linuksa SMP do modem�w Eagle 8051 Analog (sagem f@st 800/840/908/...)
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{?with_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod
Provides:	kernel-usb-eagle
Obsoletes:	kernel-smp-usb-fast800

%description -n kernel-smp-usb-eagle
Linux SMP driver for the Eagle 8051 Analog (sagem f@st
800/840/908/...) modems.

%description -n kernel-smp-usb-eagle -l pl
Sterownik dla Linuksa SMP do modem�w Eagle 8051 Analog (sagem f@st
800/840/908/...).

%prep
%setup -q
%patch0 -p1
%patch1 -p1
%patch2 -p1
%patch3 -p1
%patch4 -p0

%ifnarch %{ix86}
# invalid not only for ppc
sed -i 's/-mpreferred-stack-boundary=2//' driver/Makefile
%endif

%build
%if %{with kernel}
cd driver
for cfg in %{?with_dist_kernel:%{?with_smp:smp} up}%{!?with_dist_kernel:nondist}; do
    if [ ! -r "%{_kernelsrcdir}/config-$cfg" ]; then
	exit 1
    fi
    rm -rf include
    install -d include/{config,linux}
    ln -sf %{_kernelsrcdir}/config-up .config
    ln -sf %{_kernelsrcdir}/include/linux/autoconf-up.h include/linux/autoconf.h
    ln -sf %{_kernelsrcdir}/include/asm-%{_target_base_arch} include/asm
    touch include/config/MARKER
    %{__make} -C %{_kernelsrcdir} modules \
	RCS_FIND_IGNORE="-name '*.ko' -o" \
	M=$PWD O=$PWD \
	%{?with_verbose:V=1}
    mv eagle-usb{,-$cfg}.ko
done
cd -
%endif

%if %{with userspace}
%{__aclocal} -I .
%{__autoconf}
%configure
%{__make} -C driver/firmware \
	CFLAGS="%{rpmcflags}"
%{__make} -C driver/user \
	CFLAGS="%{rpmcflags} -DBIN_DIR=\"\\\"%{_datadir}/misc\\\"\" -DCONF_DIR=\"\\\"%{_sysconfdir}/eagle-usb\\\"\""
%{__make} -C pppoa \
	CFLAGS="%{rpmcflags}"
%endif

%install
rm -rf $RPM_BUILD_ROOT

%if %{with kernel}
cd driver
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}{,smp}/kernel/drivers/usb/net
install eagle-usb-%{?with_dist_kernel:up}%{!?with_dist_kernel:nondist}.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net/eagle-usb.ko
%if %{with smp} && %{with dist_kernel}
install eagle-usb-smp.ko \
	$RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/net/eagle-usb.ko
%endif
cd -
%endif

%if %{with userspace}
install -d $RPM_BUILD_ROOT%{_sysconfdir}/{analog,hotplug,ppp} \
	$RPM_BUILD_ROOT{%{_sbindir},%{_libdir}/hotplug/eagle}
%{__make} -C driver/firmware install \
	EU_DSP_DIR=$RPM_BUILD_ROOT%{_datadir}/misc
%{__make} -C driver/user install \
	EU_SCRIPT_DIR=$RPM_BUILD_ROOT%{_sysconfdir}/eagle-usb \
	SBINDIR=$RPM_BUILD_ROOT%{_sbindir}
mv $RPM_BUILD_ROOT%{_sysconfdir}/eagle-usb/eagle-usb.conf{.template,}
%{__make} -C pppoa install \
	SBINDIR=$RPM_BUILD_ROOT%{_sbindir}
%endif

%clean
rm -rf $RPM_BUILD_ROOT

%post -n kernel-usb-eagle
%depmod %{_kernel_ver}

%postun -n kernel-usb-eagle
%depmod %{_kernel_ver}

%post -n kernel-smp-usb-eagle
%depmod %{_kernel_ver}

%postun -n kernel-smp-usb-eagle
%depmod %{_kernel_ver}

%if %{with userspace}
%files
%defattr(644,root,root,755)
%doc README
%dir %{_sysconfdir}/eagle-usb
%attr(640,root,root) %config(noreplace) %verify(not size mtime md5) %{_sysconfdir}/eagle-usb/eagle-usb.conf
%attr(755,root,root) %{_sbindir}/*
%{_datadir}/misc/*.bin
%endif

%if %{with kernel}
%files -n kernel-usb-eagle
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net/*.ko*

%if %{with smp} && %{with dist_kernel}
%files -n kernel-smp-usb-eagle
%defattr(644,root,root,755)
/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/net/*.ko*
%endif
%endif
