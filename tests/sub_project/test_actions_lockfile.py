"""Tests for include_actions_lockfile feature."""

from __future__ import annotations

import json
import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.helpers import RENOVATE_ANNOTATION_REGEX


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'github', 'include_actions_lockfile': True}, True),
        ({'vcs_platform': 'github', 'include_actions_lockfile': False}, False),
        ({'vcs_platform': 'github'}, False),
        ({'vcs_platform': 'gitlab'}, False),
    ],
    indirect=['sub_project'],
)
def test_actions_lockfile_files(sub_project: Path, expected: bool) -> None:
    """Test that lockfile support is included based on the option."""
    workflow = sub_project / '.github' / 'workflows' / 'verify-lockfile.yml'
    assert workflow.exists() == expected

    renovate = json.loads((sub_project / 'renovate.json').read_text())
    assert (
        any(
            rule.get('matchManagers') == ['github-actions']
            and rule.get('pinDigests') is False
            for rule in renovate['packageRules']
        )
        == expected
    )

    contributing = (sub_project / 'CONTRIBUTING.md').read_text()
    assert ('gh actions-lock' in contributing) == expected


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'github', 'include_actions_lockfile': True}],
    indirect=True,
)
def test_actions_lock_version_renovate_managed(sub_project: Path) -> None:
    """CI's extension pin is picked up by Renovate's preset and used by the job."""
    path = sub_project / '.github' / 'workflows' / 'verify-lockfile.yml'
    match = re.search(RENOVATE_ANNOTATION_REGEX, path.read_text())
    assert match is not None
    assert match['depName'] == 'github/gh-actions-lock'

    job = yaml.safe_load(path.read_text())['jobs']['verify']
    assert job['env']['GH_ACTIONS_LOCK_VERSION'] == match['currentValue']
    assert any(
        '--pin "$GH_ACTIONS_LOCK_VERSION"' in step.get('run', '')
        for step in job['steps']
    )


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'github', 'include_actions_lockfile': True}, True),
        ({'vcs_platform': 'github'}, False),
    ],
    indirect=['sub_project'],
)
def test_actions_lockfile_answer_recorded_only_on_opt_in(
    sub_project: Path, expected: bool
) -> None:
    """Beta flag: unrecorded unless opted in, so a later rollout asks fresh."""
    answers = yaml.safe_load(
        (sub_project / '.copier-answers.copier-template.yml').read_text()
    )
    assert ('include_actions_lockfile' in answers) == expected


@pytest.mark.parametrize('vcs_platform', ['gitlab', ''])
def test_actions_lockfile_rejected_without_github(
    sub_project_factory: Callable[[dict[str, Any] | None], Path],
    vcs_platform: str,
) -> None:
    """Opting in on a non-GitHub platform fails validation."""
    with pytest.raises(ValueError, match='only supported with GitHub'):
        sub_project_factory(
            {'vcs_platform': vcs_platform, 'include_actions_lockfile': True}
        )
