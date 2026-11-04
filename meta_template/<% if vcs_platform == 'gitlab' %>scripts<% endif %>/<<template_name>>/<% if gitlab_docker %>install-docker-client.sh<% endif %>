#!/usr/bin/env bash
# Installs the Docker CLI with the buildx and compose plugins, for the GitLab
# CI tests job. Client only: the job's docker:dind service runs the daemon.
#
# The packages come from Docker's apt repo, which keeps them in step with
# docker:dind (Debian's own packages lag behind). apt verifies them against
# docker.asc, Docker's signing key committed next to this script, rather than
# a key fetched at runtime.
set -euo pipefail

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
keyring=/etc/apt/keyrings/docker.asc

# Needed to reach Docker's repo over HTTPS, and missing from slim images
apt-get update
apt-get install --no-install-recommends -y ca-certificates

install -D -m 0644 "$script_dir/docker.asc" "$keyring"

arch="$(dpkg --print-architecture)"
# shellcheck source=/dev/null
codename="$(. /etc/os-release && echo "$VERSION_CODENAME")"
echo "deb [arch=$arch signed-by=$keyring] https://download.docker.com/linux/debian $codename stable" \
    > /etc/apt/sources.list.d/docker.list

apt-get update
apt-get install --no-install-recommends -y \
    docker-ce-cli docker-buildx-plugin docker-compose-plugin
