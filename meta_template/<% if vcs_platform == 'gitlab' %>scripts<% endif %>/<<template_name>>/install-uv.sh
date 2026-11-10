#!/usr/bin/env bash
# Installs uv (https://docs.astral.sh/uv/) at $UV_VERSION into /usr/local/bin,
# for the GitLab CI jobs.
#
# The archive and its .sha256 come from uv's GitHub release, rather than
# running astral.sh's install script. Astral's releases are immutable, so a
# version can't be swapped for different files once published. The checksum
# comes from the same release, so checking it catches a corrupt download, but
# doesn't prove who published the release.
#
# UV_VERSION is set in the CI file, where Renovate keeps it up to date.
set -euo pipefail

: "${UV_VERSION:?UV_VERSION must be set, e.g. 0.13.7}"

# Prints the first x.y.z version in a command's output, or nothing
installed_version() {
    "$@" 2> /dev/null | grep -oE '[0-9]+\.[0-9]+\.[0-9]+' | head -n 1 || true
}

# Fails unless the command that runs now reports the version just installed.
# The install can succeed and still not be what runs, when another install
# comes first, e.g. earlier on PATH
check_installed() {
    local name=$1 want=$2 got
    shift 2
    hash -r
    got="$(installed_version "$@")"
    if [[ "$got" != "$want" ]]; then
        echo "Installed $name $want, but '$*' reports ${got:-no version}" \
            "($(command -v "$1" || echo "$1 isn't on PATH")), so another" \
            "install comes first" >&2
        exit 1
    fi
}

# Nothing to do when the image already has it, e.g. a prebuilt CI image
if [[ "$(installed_version uv --version)" == "$UV_VERSION" ]] \
    && [[ "$(installed_version uvx --version)" == "$UV_VERSION" ]]; then
    echo "uv $UV_VERSION is already installed"
    exit 0
fi

case "$(uname -m)" in
    x86_64) target=x86_64-unknown-linux-gnu ;;
    aarch64 | arm64) target=aarch64-unknown-linux-gnu ;;
    *)
        echo "No uv build for $(uname -m)" >&2
        exit 1
        ;;
esac

# Missing from slim images. CI installs them first, which saves an
# apt-get update here
if ! command -v curl > /dev/null || [[ ! -e /etc/ssl/certs/ca-certificates.crt ]]; then
    apt-get update
    apt-get install --no-install-recommends -y ca-certificates curl
fi

archive="uv-$target.tar.gz"
url="https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$archive"
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT

curl --fail --silent --show-error --location --retry 3 -o "$tmp/$archive" "$url"
curl --fail --silent --show-error --location --retry 3 -o "$tmp/$archive.sha256" "$url.sha256"
(cd "$tmp" && sha256sum --check --strict "$archive.sha256")

tar -xzf "$tmp/$archive" -C "$tmp"
install -m 0755 "$tmp/uv-$target/uv" "$tmp/uv-$target/uvx" /usr/local/bin/

# Only sees the PATH this script is run with, so the CI file puts
# ~/.local/bin, where Astral's installer puts uv, on PATH first
check_installed uv "$UV_VERSION" uv --version
check_installed uvx "$UV_VERSION" uvx --version
