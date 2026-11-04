#!/usr/bin/env bash
# Installs uv (https://docs.astral.sh/uv/) at $UV_VERSION into /usr/local/bin,
# for the GitLab CI jobs.
#
# The archive and its .sha256 come from uv's GitHub release, rather than
# running astral.sh's install script. Astral's releases are immutable, so
# neither file can be replaced once published, and checking one against the
# other is enough to trust the download.
#
# UV_VERSION is set in the CI file, where Renovate keeps it up to date.
set -euo pipefail

: "${UV_VERSION:?UV_VERSION must be set, e.g. 0.13.7}"

case "$(uname -m)" in
    x86_64) target=x86_64-unknown-linux-gnu ;;
    aarch64 | arm64) target=aarch64-unknown-linux-gnu ;;
    *)
        echo "No uv build for $(uname -m)" >&2
        exit 1
        ;;
esac

# Missing from slim images
if ! command -v curl > /dev/null; then
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
