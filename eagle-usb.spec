#
# Conditional build:
# _without_dist_kernel          without distribution kernel
#

%define		_snap	031117
%define		_orig_name	eagle
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa do modem�w Eagle 8051 Analog (sagem f@st 800...)
Name:		eagle
Version:	1.0.5
Release:	0.%{_snap}.1
License:	GPL
Group:		Base/Kernel
#Source0:	http://fast800.tuxfamily.org/pub/IMG/gz/%{name}-%{version}.tar.gz
Source0:	http://www.kernel.pl/~djurban/pld/%{name}-usb.tar.bz2
# Source0-md5:	d0afb3de2e5e3c04b40809d623244bfb
Patch0:		%{name}-Makefile.patch
URL:		http://fast800.tuxfamily.org/
%{!?_without_dist_kernel:BuildRequires:	kernel-headers }
BuildRequires:	%{kgcc_package}
BuildRequires:	rpmbuild(macros) >= 1.118
Requires(post,postun):	/sbin/depmod
Requires:	ppp >= 2.4.1
BuildRoot:	%{tmpdir}/%{name}-%{version}-root-%(id -u -n)

%description
Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -l pl
Sterownik dla Linuksa do modem�w Eagle 8051 Analog (sagem f@st
800...).

%package -n kernel-usb-%{_orig_name}
Summary:	Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa do modem�w Eagle 8051 Analog (sagem f@st 800...)
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{!?_without_dist_kernel:%requires_releq_kernel_up}
Requires(post,postun):	/sbin/depmod


%description -n kernel-usb-%{_orig_name}
Linux driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -n kernel-usb-%{_orig_name} -l pl
Sterownik dla Linuksa do modem�w Eagle 8051 Analog (sagem f@st
800...).

%package -n kernel-smp-usb-%{_orig_name}
Summary:	Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800...) modems
Summary(pl):	Sterownik dla Linuksa SMP do modem�w Eagle 8051 Analog (sagem f@st 800...)
Release:	%{_rel}@%{_kernel_ver_str}
Group:		Base/Kernel
%{!?_without_dist_kernel:%requires_releq_kernel_smp}
Requires(post,postun):	/sbin/depmod


%description -n kernel-smp-usb-%{_orig_name}
Linux SMP driver for the Eagle 8051 Analog (sagem f@st 800...) modems.

%description -n kernel-smp-usb-%{_orig_name} -l pl
Sterownik dla Linuksa SMP do modem�w Eagle 8051 Analog (sagem f@st
800...).

%prep
%setup -q -n eagle-usb 
%patch0 -p1

%build
install -d kernel-{up,smp}

%{__aclocal} -I .
%{__autoconf}

%configure --with-eagle-usb-bindir=%{_datadir}/misc/
%{__make}

# There should be a way to build smp too, but noidea how.


%install
rm -rf $RPM_BUILD_ROOT
%{__make} install DESTDIR=$RPM_BUILD_ROOT
install -d $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net

mv $RPM_BUILD_ROOT/lib/modules/%{__kernel_ver}/misc/eagle-usb.ko $RPM_BUILD_ROOT/lib/modules/%{_kernel_ver}/kernel/drivers/usb/net/

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

#%%%if %{with smp}
#%%%files -n kernel-smp-usb-%{_orig_name}
#%%%defattr(644,root,root,755)
#%%/lib/modules/%{_kernel_ver}smp/kernel/drivers/usb/*
#%%%endif
