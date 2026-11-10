# Image for the GitLab CI tests job, with the tools its before_script would
# otherwise install every run, and the Python versions it tests with.
#
# Built by the build-*-ci-image job in the .gitlab-ci.yml next to this
# directory, with the install scripts as the build context and the versions
# pinned in that file as build args. The tests job still runs the scripts,
# which skip anything this image already has at the pinned version, and uv
# downloads any Python it lacks, so a stale image only costs time.
#
# Yours to extend: add whatever else your template's tests need. Nothing
# reinstalls your additions, so pipelines on a stale :latest go without them
# until the image is rebuilt.
# A tag, not a digest: your Renovate pins the digest and keeps it current
FROM debian:trixie-slim

ARG UV_VERSION
ARG TASK_VERSION
ARG DOCKER_CE_CLI_VERSION
ARG DOCKER_BUILDX_PLUGIN_VERSION
ARG DOCKER_COMPOSE_PLUGIN_VERSION
ARG PYTHON_VERSIONS

COPY . /tmp/install/
RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl git \
    && bash /tmp/install/install-uv.sh \
    && bash /tmp/install/install-task.sh \
    && bash /tmp/install/install-docker-client.sh \
    # Outside root's home and on PATH, so the tests job's non-root user finds
    # them too. Set for this install only: uv then puts a Python the image
    # lacks in the job user's own directory, rather than this root-owned one
    && UV_PYTHON_INSTALL_DIR=/opt/uv/python UV_PYTHON_BIN_DIR=/usr/local/bin \
        uv python install $PYTHON_VERSIONS \
    && rm -rf /var/lib/apt/lists/* /tmp/install
