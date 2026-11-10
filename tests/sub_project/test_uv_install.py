"""Tests for installing uv in the generated GitLab CI jobs."""

from __future__ import annotations

import os
from pathlib import Path

import pytest
import yaml

from tests.helpers import load_gitlab_ci, scripts_dir

INSTALL_UV = 'bash "scripts/copier-template/install-uv.sh"'


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
        # Recommends would add packages the job doesn't use, so the ones it
        # needs, ca-certificates included, are named
        assert any(
            'apt-get update && apt-get install --no-install-recommends -y '
            'ca-certificates curl git' in cmd
            for cmd in before_script
        )
        assert INSTALL_UV in before_script
        switch_user = [i for i, cmd in enumerate(before_script) if 'runuser' in cmd]
        assert before_script.index(INSTALL_UV) < min(
            switch_user, default=len(before_script)
        )
        assert 'UV_VERSION' in job['variables']
    rendered = yaml.safe_dump(gitlab_ci)
    assert 'astral.sh' not in rendered
    assert '.local/bin/env' not in rendered


@pytest.mark.parametrize(
    ('sub_project', 'local_bin'),
    [
        ({'vcs_platform': 'gitlab'}, '$HOME/.local/bin'),
        (
            {'vcs_platform': 'gitlab', 'gitlab_non_root_tests': True},
            '/home/$TEST_USER/.local/bin',
        ),
    ],
    indirect=['sub_project'],
)
def test_tests_job_puts_local_bin_on_path(sub_project: Path, local_bin: str) -> None:
    """Tools from uv tool install run as root or not, as the uv installer allowed."""
    before_script = load_gitlab_ci(sub_project)['tests']['before_script']
    assert f'export PATH="{local_bin}:$PATH"' in before_script


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_root_tests_job_puts_local_bin_on_path_before_installs(
    sub_project: Path,
) -> None:
    """The install scripts check versions on the PATH the job runs with.

    Astral's installer puts uv in ~/.local/bin, so an image built with it
    would otherwise shadow the pinned uv after the scripts had checked.
    """
    before_script = load_gitlab_ci(sub_project)['tests']['before_script']
    export = 'export PATH="$HOME/.local/bin:$PATH"'
    assert before_script.index(export) < before_script.index(INSTALL_UV)


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_install_uv_script(sub_project: Path) -> None:
    """The script checks the release archive against its checksum file."""
    script = scripts_dir(sub_project) / 'install-uv.sh'
    assert os.access(script, os.X_OK)
    text = script.read_text()
    assert (
        'https://github.com/astral-sh/uv/releases/download/$UV_VERSION/$archive' in text
    )
    assert '"$url.sha256"' in text
    assert 'sha256sum --check --strict' in text
    # Skipped when the image already has the pinned version
    assert '[[ "$(installed_version uv --version)" == "$UV_VERSION" ]]' in text
    assert 'install.sh' not in text
    assert '| sh' not in text
