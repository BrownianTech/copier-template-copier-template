"""Tests for gitlab_non_root_tests feature."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml


def load_tests_job(sub_project: Path) -> dict[str, Any]:
    gitlab_ci = sub_project / '.gitlab' / 'ci' / 'copier-template' / '.gitlab-ci.yml'
    return yaml.safe_load(gitlab_ci.read_text())['tests']


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab', 'gitlab_non_root_tests': True}, True),
        ({'vcs_platform': 'gitlab', 'gitlab_non_root_tests': False}, False),
        ({'vcs_platform': 'gitlab'}, False),
    ],
    indirect=['sub_project'],
)
def test_gitlab_non_root_tests_job(sub_project: Path, expected: bool) -> None:
    """The tests job runs as TEST_USER only when opted in."""
    job = load_tests_job(sub_project)
    assert ('TEST_USER' in job['variables']) == expected
    assert 'DOCKER_CERT_PATH' in job['variables']
    assert job['script'][0].startswith('runuser') == expected
    assert any(cmd.endswith('task dev-setup:venv:ci') for cmd in job['before_script'])
    assert (
        all(
            cmd.startswith('runuser')
            for cmd in job['before_script']
            if 'install.sh' in cmd or cmd.startswith(('uv ', 'task '))
        )
        == expected
    )


@pytest.mark.parametrize(
    'sub_project',
    [
        {'vcs_platform': 'gitlab', 'gitlab_non_root_tests': True},
        {'vcs_platform': 'gitlab'},
    ],
    indirect=True,
)
def test_gitlab_ci_line_length(sub_project: Path) -> None:
    """Lines fit yamllint's 120 limit used by projects from the pre-commit template."""
    gitlab_ci = sub_project / '.gitlab' / 'ci' / 'copier-template' / '.gitlab-ci.yml'
    assert max(len(line) for line in gitlab_ci.read_text().splitlines()) <= 120


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab', 'gitlab_non_root_tests': True}, True),
        ({'vcs_platform': 'gitlab'}, False),
    ],
    indirect=['sub_project'],
)
def test_gitlab_non_root_tests_answer_recorded_only_on_opt_in(
    sub_project: Path, expected: bool
) -> None:
    """Beta flag: unrecorded unless opted in, so a later rollout asks fresh."""
    answers = yaml.safe_load(
        (sub_project / '.copier-answers.copier-template.yml').read_text()
    )
    assert ('gitlab_non_root_tests' in answers) == expected


@pytest.mark.parametrize('vcs_platform', ['github', ''])
def test_gitlab_non_root_tests_rejected_without_gitlab(
    sub_project_factory: Callable[[dict[str, Any] | None], Path],
    vcs_platform: str,
) -> None:
    """Opting in on a non-GitLab platform fails validation."""
    with pytest.raises(ValueError, match='only supported with GitLab'):
        sub_project_factory(
            {'vcs_platform': vcs_platform, 'gitlab_non_root_tests': True}
        )
