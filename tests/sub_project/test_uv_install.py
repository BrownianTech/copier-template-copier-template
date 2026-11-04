"""Tests for installing uv in the generated GitLab CI jobs."""

from __future__ import annotations

import os
from pathlib import Path
from typing import Any

import pytest
import yaml

INSTALL_UV = 'bash "scripts/copier-template/install-uv.sh"'


def load_gitlab_ci(sub_project: Path) -> dict[str, Any]:
    gitlab_ci = sub_project / '.gitlab' / 'ci' / 'copier-template' / '.gitlab-ci.yml'
    return yaml.safe_load(gitlab_ci.read_text())


@pytest.mark.parametrize(
    ('sub_project', 'jobs'),
    [
        ({'vcs_platform': 'gitlab'}, {'tests', 'release'}),
        (
            {'vcs_platform': 'gitlab', 'gitlab_non_root_tests': True},
            {'tests', 'release'},
        ),
        ({'vcs_platform': 'gitlab', 'include_semantic_release': False}, {'tests'}),
    ],
    indirect=['sub_project'],
)
def test_jobs_install_uv_from_script(sub_project: Path, jobs: set[str]) -> None:
    """Every job installs uv with install-uv.sh, as root before any switch of user."""
    gitlab_ci = load_gitlab_ci(sub_project)
    assert {name for name in jobs if name in gitlab_ci} == jobs
    for name in jobs:
        job = gitlab_ci[name]
        before_script = job['before_script']
        assert INSTALL_UV in before_script
        switch_user = [i for i, cmd in enumerate(before_script) if 'runuser' in cmd]
        assert before_script.index(INSTALL_UV) < min(
            switch_user, default=len(before_script)
        )
        assert 'UV_VERSION' in job['variables']
    rendered = yaml.safe_dump(gitlab_ci)
    assert 'astral.sh' not in rendered
    assert '.local/bin/env' not in rendered


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_install_uv_script(sub_project: Path) -> None:
    """The script checks the release archive against its checksum file."""
    script = sub_project / 'scripts' / 'copier-template' / 'install-uv.sh'
    assert os.access(script, os.X_OK)
    text = script.read_text()
    assert (
        'https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$archive' in text
    )
    assert '"$url.sha256"' in text
    assert 'sha256sum --check --strict' in text
    assert 'install.sh' not in text
    assert '| sh' not in text
