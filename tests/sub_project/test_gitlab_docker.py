"""Tests for gitlab_docker feature."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.helpers import openpgp_fingerprint

DOCKER_PACKAGES = 'docker-ce-cli docker-buildx-plugin docker-compose-plugin'
# Docker's published fingerprint for its apt repo signing key, see
# https://docs.docker.com/engine/install/debian/
DOCKER_KEY_FINGERPRINT = '9DC858229FC7DD38854AE2D88D81803C0EBFCD88'


def scripts_dir(sub_project: Path) -> Path:
    return sub_project / 'scripts' / 'copier-template'


def load_tests_job(sub_project: Path) -> dict[str, Any]:
    gitlab_ci = sub_project / '.gitlab' / 'ci' / 'copier-template' / '.gitlab-ci.yml'
    return yaml.safe_load(gitlab_ci.read_text())['tests']


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab'}, True),
        ({'vcs_platform': 'gitlab', 'gitlab_docker': True}, True),
        ({'vcs_platform': 'gitlab', 'gitlab_docker': False}, False),
        (
            {
                'vcs_platform': 'gitlab',
                'gitlab_docker': False,
                'gitlab_non_root_tests': True,
            },
            False,
        ),
    ],
    indirect=['sub_project'],
)
def test_gitlab_docker_tests_job(sub_project: Path, expected: bool) -> None:
    """The tests job gets the dind service and Docker client only when enabled."""
    job = load_tests_job(sub_project)
    assert (job.get('services') == [{'name': 'docker:dind'}]) == expected
    assert ('DOCKER_HOST' in job['variables']) == expected
    assert (
        'bash "scripts/copier-template/install-docker-client.sh"'
        in job['before_script']
    ) == expected
    assert (scripts_dir(sub_project) / 'install-docker-client.sh').exists() == expected
    assert (scripts_dir(sub_project) / 'docker.asc').exists() == expected


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_install_docker_client_script(sub_project: Path) -> None:
    """The script installs only the client and plugins, from the committed key."""
    script = scripts_dir(sub_project) / 'install-docker-client.sh'
    assert os.access(script, os.X_OK)
    text = script.read_text()
    assert DOCKER_PACKAGES in ' '.join(text.replace('\\\n', ' ').split())
    assert 'https://download.docker.com/linux/debian' in text
    # The signing key comes from the repo, never the network
    assert '"$script_dir/docker.asc"' in text
    assert 'curl' not in text
    assert 'wget' not in text
    # The daemon runs in the dind service, so it's never installed in the job
    assert 'docker-ce ' not in text
    assert 'docker.io' not in text


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab'}, False),
        ({'vcs_platform': 'gitlab', 'gitlab_docker': False}, True),
        ({'vcs_platform': 'github'}, False),
    ],
    indirect=['sub_project'],
)
def test_gitlab_docker_recorded_only_when_opted_out(
    sub_project: Path, expected: bool
) -> None:
    """Only the non-default answer is recorded, as for other beta flags."""
    answers = yaml.safe_load(
        (sub_project / '.copier-answers.copier-template.yml').read_text()
    )
    assert ('gitlab_docker' in answers) == expected


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_gitlab_docker_apt_key_fingerprint(sub_project: Path) -> None:
    """The committed key is Docker's apt repo signing key."""
    key = scripts_dir(sub_project) / 'docker.asc'
    assert openpgp_fingerprint(key.read_text()) == DOCKER_KEY_FINGERPRINT
