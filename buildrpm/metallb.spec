{{{$version := printf "%s.%s.%s" .major .minor .patch}}}
%if 0%{?with_debug}
# https://bugzilla.redhat.com/show_bug.cgi?id=995136#c12
%global _dwz_low_mem_die_limit 0
%else
%global debug_package   %{nil}
%endif

%global app_name metallb
%global app_version {{{$version}}}
%global oracle_release_version 1
%global golang_version 1.20.10
%ifarch %{arm} arm64 aarch64
%global arch aarch64
%else
%global arch x86_64
%endif
%global _buildhost build-ol%{?oraclelinux}-%{?_arch}.oracle.com

Name:               %{app_name}
Version:            %{app_version}
Release:            %{oracle_release_version}%{?dist}
Summary:            A network load-balancer implementation for Kubernetes using standard routing protocols
License:            Apache 2.0
URL:                https://github.com/metallb/metallb/
Source:             %{name}-%{version}.tar.bz2
Vendor:             Oracle America
Group:              System/Management
BuildRequires:      golang >= %{golang_version}

%description
MetalLB is a load-balancer implementation for bare metal Kubernetes clusters, using standard routing protocols.

%prep
%setup -n %{name}-%{version}
cd %{_builddir}
mkdir -p src/github.com/metallb/
rm -rf src/github.com/metallb/%{name}
mv %{name}-%{version} src/github.com/metallb/%{name}
ln -sf src/github.com/metallb/%{name} %{name}-%{version}

%build -n src/github.com/metallb/%{name}
export GOPATH=%{_builddir}
export GOOS="linux"
export GO111MODULE="on"
export CGO_ENABLED="0"
%global commit $(git describe --dirty --always)
%global branch $(git rev-parse --abbrev-ref HEAD)
%global ldflags "-X main.version=%{app_version} -X 'go.universe.tf/metallb/internal/version.gitCommit=%{commit}' -X 'go.universe.tf/metallb/internal/version.gitBranch=%{branch}'"

{{{- if semverCompare "<0.13.6" $version }}}
%global binaries "controller" "mirror-server" "speaker" "configmaptocrs"
{{{- else }}}
%global binaries "controller" "speaker" "configmaptocrs"
{{{- end }}}

for bin in %{binaries}
do
    mkdir -p src/github.com/metallb/%{name}/build/%{arch}/${bin}
    go build -v -o build/%{arch}/${bin}/${bin} -ldflags %{ldflags} -trimpath=false go.universe.tf/metallb/${bin}
done

%install
install -d -p %{buildroot}/usr/local/share/olcne/metallb/%{name}
for bin in %{binaries}
do
    cp -a %{_builddir}/src/github.com/metallb/%{name}/build/%{arch}/${bin} %{buildroot}/usr/local/share/olcne/metallb/%{name}/
done

%files
%license LICENSE DCO THIRD_PARTY_LICENSES.txt SECURITY.md
/usr/local/share/olcne/metallb/%{name}

%clean
rm -rf src

%changelog
* {{{.changelog_timestamp}}} - %{version}-1
- Added configmaptocrs to binaries list
