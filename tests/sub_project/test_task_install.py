"""Tests for installing Task in the generated GitLab CI tests job."""

from __future__ import annotations

import os
import re
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.helpers import openpgp_fingerprint
from tests.sub_project.test_renovate import RENOVATE_ANNOTATION_REGEX

# Fingerprint of the Task repo's signing key on Cloudsmith, as served from
# https://dl.cloudsmith.io/public/task/task/gpg.046FD1186CA342F0.key
# A public key's fingerprint, not a secret
TASK_KEY_FINGERPRINT = 'D19803B9E1AA18999752F1CA046FD1186CA342F0'  # gitleaks:allow
TASK_REGISTRY_URL = (
    'https://dl.cloudsmith.io/public/task/task/deb/debian'
    '?suite=any-version&components=main&binaryArch=amd64'
)


def scripts_dir(sub_project: Path) -> Path:
    return sub_project / 'scripts' / 'copier-template'


def gitlab_ci_path(sub_project: Path) -> Path:
    return sub_project / '.gitlab' / 'ci' / 'copier-template' / '.gitlab-ci.yml'


def load_tests_job(sub_project: Path) -> dict[str, Any]:
    return yaml.safe_load(gitlab_ci_path(sub_project).read_text())['tests']


@pytest.mark.parametrize(
    'sub_project',
    [
        {'vcs_platform': 'gitlab'},
        {'vcs_platform': 'gitlab', 'gitlab_docker': False},
        {'vcs_platform': 'gitlab', 'gitlab_non_root_tests': True},
    ],
    indirect=True,
)
def test_tests_job_installs_task_from_script(sub_project: Path) -> None:
    """Task comes from install-task.sh, run as root before any switch of user."""
    before_script = load_tests_job(sub_project)['before_script']
    install = 'bash "scripts/copier-template/install-task.sh"'
    assert install in before_script
    switch_user = [i for i, cmd in enumerate(before_script) if 'runuser' in cmd]
    assert before_script.index(install) < min(switch_user, default=len(before_script))
    assert not any('taskfile.dev' in cmd for cmd in before_script)
    assert 'TASK_VERSION' in load_tests_job(sub_project)['variables']


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'gitlab'}, {'vcs_platform': 'gitlab', 'gitlab_docker': False}],
    indirect=True,
)
def test_install_task_script(sub_project: Path) -> None:
    """The script installs the pinned version, trusting only the committed key."""
    script = scripts_dir(sub_project) / 'install-task.sh'
    assert os.access(script, os.X_OK)
    text = script.read_text()
    assert '"task=$TASK_VERSION"' in text
    # One build serves every Debian release, so the image's release isn't used
    assert (
        'https://dl.cloudsmith.io/public/task/task/deb/debian any-version main' in text
    )
    assert 'VERSION_CODENAME' not in text
    assert '"$script_dir/task.asc"' in text
    assert 'curl' not in text
    assert 'wget' not in text

    key = scripts_dir(sub_project) / 'task.asc'
    assert openpgp_fingerprint(key.read_text()) == TASK_KEY_FINGERPRINT


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'github'}], indirect=True)
def test_no_scripts_dir_on_github(sub_project: Path) -> None:
    """GitHub installs Task with go-task/setup-task, so there are no scripts."""
    assert not (sub_project / 'scripts').exists()


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_task_version_renovate_lookup(sub_project: Path) -> None:
    """Renovate looks Task up in the same apt repo the script installs from."""
    matches = [
        match.groupdict()
        for match in re.finditer(
            RENOVATE_ANNOTATION_REGEX, gitlab_ci_path(sub_project).read_text()
        )
    ]
    task = next(match for match in matches if match['depName'] == 'go-task/task')
    assert task['datasource'] == 'deb'
    assert task['packageName'] == 'task'
    assert task['registryUrl'] == TASK_REGISTRY_URL
    assert (
        task['currentValue'] == load_tests_job(sub_project)['variables']['TASK_VERSION']
    )
