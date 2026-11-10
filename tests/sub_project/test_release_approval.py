"""Tests for release_approval feature."""

from __future__ import annotations

from pathlib import Path

import pytest
import yaml

from tests.helpers import gitlab_ci_path


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'github', 'release_approval': True}, True),
        ({'vcs_platform': 'github', 'release_approval': False}, False),
        ({'vcs_platform': 'github'}, False),
    ],
    indirect=['sub_project'],
)
def test_release_approval_github(sub_project: Path, expected: bool) -> None:
    """The release job runs in the `release` environment only when opted in."""
    workflow = sub_project / '.github' / 'workflows' / 'release.yml'
    job = yaml.safe_load(workflow.read_text())['jobs']['release']
    assert (job.get('environment') == 'release') == expected

    contributing = (sub_project / 'CONTRIBUTING.md').read_text()
    assert ('### Release approval' in contributing) == expected


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab', 'release_approval': True}, True),
        ({'vcs_platform': 'gitlab', 'release_approval': False}, False),
        ({'vcs_platform': 'gitlab'}, False),
    ],
    indirect=['sub_project'],
)
def test_release_approval_gitlab(sub_project: Path, expected: bool) -> None:
    """The release job is manual on the default branch only when opted in."""
    gitlab_ci = gitlab_ci_path(sub_project)
    job = yaml.safe_load(gitlab_ci.read_text())['release']
    default_branch_rule = next(
        rule
        for rule in job['rules']
        if rule['if'] == '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    )
    assert (default_branch_rule.get('when') == 'manual') == expected
    assert (job.get('environment') == 'release') == expected

    contributing = (sub_project / 'CONTRIBUTING.md').read_text()
    assert ('### Release approval' in contributing) == expected


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'github'}, True),
        ({'vcs_platform': 'gitlab'}, True),
        ({'vcs_platform': 'github', 'include_semantic_release': False}, False),
        ({'vcs_platform': ''}, False),
    ],
    indirect=['sub_project'],
)
def test_release_approval_asked_only_with_releases_in_ci(
    sub_project: Path, expected: bool
) -> None:
    """Only asked (and recorded) when there's a CI release job to gate."""
    answers = yaml.safe_load(
        (sub_project / '.copier-answers.copier-template.yml').read_text()
    )
    assert ('release_approval' in answers) == expected
