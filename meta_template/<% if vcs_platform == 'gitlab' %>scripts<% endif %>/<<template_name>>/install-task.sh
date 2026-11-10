#!/usr/bin/env bash
# Installs Task (https://taskfile.dev) at $TASK_VERSION, for the GitLab CI
# tests job.
#
# The package comes from the Task team's apt repo on Cloudsmith. apt verifies
# it against task.asc, the repo's signing key committed next to this script,
# rather than a key fetched at runtime. That proves the package came through
# this repo, not that it's the same build as when TASK_VERSION was pinned:
# Task publishes with GoReleaser's republish option, which replaces a package
# of the same version.
#
# Cloudsmith's setup.deb.sh and taskfile.dev/install.sh are avoided as they're
# scripts fetched and run at job time.
#
# TASK_VERSION is set in the CI file, where Renovate keeps it up to date.
set -euo pipefail

: "${TASK_VERSION:?TASK_VERSION must be set, e.g. 3.54.0}"

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
if [[ "$(installed_version task --version)" == "$TASK_VERSION" ]]; then
    echo "Task $TASK_VERSION is already installed"
    exit 0
fi

script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
keyring=/etc/apt/keyrings/task.asc

# Needed to reach the repo over HTTPS, and missing from slim images. CI
# installs it first, which saves an apt-get update here
if [[ ! -e /etc/ssl/certs/ca-certificates.crt ]]; then
    apt-get update
    apt-get install --no-install-recommends -y ca-certificates
fi

install -D -m 0644 "$script_dir/task.asc" "$keyring"

# One build of Task serves every Debian release, which Cloudsmith publishes
# under the any-version suite
echo "deb [signed-by=$keyring] https://dl.cloudsmith.io/public/task/task/deb/debian any-version main" \
    | install -D -m 0644 /dev/stdin /etc/apt/sources.list.d/task.list

# Without --error-on=any, an unreachable repo is only a warning, and the
# install below then fails as if the pinned version didn't exist
apt-get update --error-on=any
# Downgrades too, for an image with a newer version than the CI file pins
apt-get install --no-install-recommends --allow-downgrades -y "task=$TASK_VERSION"

check_installed Task "$TASK_VERSION" task --version
