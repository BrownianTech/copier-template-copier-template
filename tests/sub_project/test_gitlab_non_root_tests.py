"""Tests for gitlab_non_root_tests feature."""

from __future__ import annotations

from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.helpers import load_tests_job


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
    assert (
        job.get('after_script') == ['chown -R "$(id -u):$(id -g)" "$CI_PROJECT_DIR"']
    ) == expected
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
