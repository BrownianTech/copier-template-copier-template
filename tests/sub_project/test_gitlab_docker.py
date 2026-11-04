"""Tests for gitlab_docker feature."""

from __future__ import annotations

import base64
import hashlib
import os
from pathlib import Path
from typing import Any

import pytest
import yaml

DOCKER_PACKAGES = 'docker-ce-cli docker-buildx-plugin docker-compose-plugin'
# Docker's published fingerprint for its apt repo signing key, see
# https://docs.docker.com/engine/install/debian/
DOCKER_KEY_FINGERPRINT = '9DC858229FC7DD38854AE2D88D81803C0EBFCD88'


def scripts_dir(sub_project: Path) -> Path:
    return sub_project / 'scripts' / 'copier-template'


def load_tests_job(sub_project: Path) -> dict[str, Any]:
    gitlab_ci = sub_project / '.gitlab' / 'ci' / 'copier-template' / '.gitlab-ci.yml'
    return yaml.safe_load(gitlab_ci.read_text())['tests']


def openpgp_fingerprint(armored: str) -> str:
    """V4 fingerprint of the primary key in an ASCII-armored public key block."""
    lines = armored.strip().splitlines()
    body = lines[lines.index('') + 1 :]
    base64_lines = [line for line in body if not line.startswith(('=', '-'))]
    data = base64.b64decode(''.join(base64_lines))
    tag = data[0]
    assert tag & 0x80, 'not an OpenPGP packet'
    if tag & 0x40:  # new-format header
        packet_tag, length_octet = tag & 0x3F, data[1]
        assert length_octet in range(192, 224), 'unsupported packet length'
        length = ((length_octet - 192) << 8) + data[2] + 192
        start = 3
    else:  # old-format header, only 2-byte lengths are used for keys this size
        packet_tag = (tag >> 2) & 0x0F
        assert tag & 0x03 == 1, 'unsupported packet length'
        length = int.from_bytes(data[1:3])
        start = 3
    assert packet_tag == 6, 'first packet is not a public key'
    packet = data[start : start + length]
    assert packet[0] == 4, 'not a v4 key'
    # V4 fingerprints are defined as SHA-1, this only compares against a known value
    digest = hashlib.sha1(b'\x99' + length.to_bytes(2) + packet, usedforsecurity=False)
    return digest.hexdigest().upper()


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
    services = [service['name'] for service in job.get('services', [])]
    assert (
        len(services) == 1 and services[0].startswith('docker:dind@sha256:')
    ) == expected
    assert ('DOCKER_HOST' in job['variables']) == expected
    assert (
        'bash "scripts/copier-template/install-docker-client.sh"'
        in job['before_script']
    ) == expected
    assert (scripts_dir(sub_project) / 'install-docker-client.sh').exists() == expected
    assert (scripts_dir(sub_project) / 'docker.asc').exists() == expected


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'gitlab', 'gitlab_docker': False}, {'vcs_platform': 'github'}],
    indirect=True,
)
def test_no_scripts_dir_without_gitlab_docker(sub_project: Path) -> None:
    """Copier doesn't leave an empty scripts/ behind when nothing renders into it."""
    assert not (sub_project / 'scripts').exists()


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
