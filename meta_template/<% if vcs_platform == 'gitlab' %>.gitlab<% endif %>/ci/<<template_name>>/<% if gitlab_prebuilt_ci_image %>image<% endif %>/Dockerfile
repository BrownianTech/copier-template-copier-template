# Image for the GitLab CI tests job, with the tools its before_script would
# otherwise install every run, and the Python versions it tests with.
#
# Built by the build-*-ci-image job in the .gitlab-ci.yml next to this
# directory, with the install scripts as the build context and the versions
# pinned in that file as build args. The tests job still runs the scripts,
# which skip anything this image already has at the pinned version, so a stale
# image only costs time.
#
# Yours to extend: add whatever else your template's tests need.
FROM debian:trixie-slim@sha256:f6b08b09a05725f9431502d3b5714f5c4576e82c1a84fa1debe0c24a7e0c3ec4

ARG UV_VERSION
ARG TASK_VERSION
ARG DOCKER_CE_CLI_VERSION
ARG DOCKER_BUILDX_PLUGIN_VERSION
ARG DOCKER_COMPOSE_PLUGIN_VERSION
ARG PYTHON_VERSIONS

# Outside root's home, so the tests job's non-root user can use them too
ENV UV_PYTHON_INSTALL_DIR=/opt/uv/python

COPY . /tmp/install/
RUN apt-get update \
    && apt-get install --no-install-recommends -y ca-certificates curl git \
    && bash /tmp/install/install-uv.sh \
    && bash /tmp/install/install-task.sh \
    && bash /tmp/install/install-docker-client.sh \
    && uv python install $PYTHON_VERSIONS \
    && rm -rf /var/lib/apt/lists/* /tmp/install
