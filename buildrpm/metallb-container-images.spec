{{{$version := printf "%s.%s.%s" .major .minor .patch}}}
%if 0%{?with_debug}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%{!?registry: %global registry container-registry.oracle.com/olcne}
%global app_name metallb
%global app_version {{{$version}}}
%global oracle_release_version 1
%global arch x86_64
%global _buildhost build-ol%{?oraclelinux}-%{?_arch}.oracle.com

Name:               %{app_name}-container-image
Version:            %{app_version}
Release:            %{oracle_release_version}%{?dist}
Summary:            A network load-balancer implementation for Kubernetes using standard routing protocols
License:            Apache-2.0
URL:                https://github.com/metallb/metallb/
Source:             %{app_name}-%{version}.tar.bz2
ExclusiveArch:      %{arch}
Vendor:             Oracle America
Group:              System/Management

%description
MetalLB is a load-balancer implementation for bare metal Kubernetes clusters, using standard routing protocols.

%prep
%setup -n %{app_name}-%{version}

%build
%global rpm_name %{app_name}-%{version}-%{release}.%{arch}
yum clean all
yumdownloader --destdir=${PWD}/rpms %{rpm_name}

%__rm .dockerignore
%global dockerfile Dockerfile
%global binaries "controller" "mirror-server" "speaker"
for bin in %{binaries}
do
    %define docker_tag %{registry}/%{app_name}-${bin}:v%{version}
    docker build --pull --build-arg https_proxy=${https_proxy} \
        -t %{docker_tag} -f ./olm/builds/%{dockerfile}.${bin} .
    docker build --pull \
        --build-arg http_proxy=${https_proxy} \
        --build-arg https_proxy=${https_proxy} \
        -t %{docker_tag} -f ./olm/builds/%{dockerfile}.${bin} .
    docker save -o %{app_name}-${bin}.tar %{docker_tag}
done

%install
for bin in %{binaries}
do
    %__install -D -m 644 %{app_name}-${bin}.tar %{buildroot}/usr/local/share/olcne/%{app_name}-${bin}.tar
done

%files
%license LICENSE THIRD_PARTY_LICENSES.txt
/usr/local/share/olcne/%{app_name}-controller.tar
/usr/local/share/olcne/%{app_name}-mirror-server.tar
/usr/local/share/olcne/%{app_name}-speaker.tar

%changelog
* {{{.changelog_timestamp}}} - %{version}-1
- Added Oracle Specific Build Files for grafana
