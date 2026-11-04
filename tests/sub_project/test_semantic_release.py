"""Tests for include_semantic_release feature."""

from __future__ import annotations

import tomllib
from pathlib import Path

import pytest
import yaml


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'github', 'include_semantic_release': True}, True),
        ({'vcs_platform': 'github', 'include_semantic_release': False}, False),
        ({'vcs_platform': 'gitlab', 'include_semantic_release': True}, True),
        ({'vcs_platform': 'gitlab', 'include_semantic_release': False}, False),
    ],
    indirect=['sub_project'],
)
def test_semantic_release_files(sub_project: Path, expected: bool) -> None:
    """Test that semantic release files are included based on the option."""
    assert (
        sub_project / 'taskfile' / 'copier-template' / 'release'
    ).is_dir() == expected

    pyproject = tomllib.loads((sub_project / 'pyproject.toml').read_text())
    assert ('semantic_release' in pyproject.get('tool', {})) == expected
    dev_deps = ' '.join(pyproject['dependency-groups']['dev'])
    assert ('python-semantic-release' in dev_deps) == expected

    taskfile = yaml.safe_load((sub_project / 'Taskfile.yaml').read_text())
    assert ('release' in taskfile['includes']) == expected

    github_release = sub_project / '.github' / 'workflows' / 'release.yml'
    gitlab_ci = sub_project / '.gitlab' / 'ci' / 'copier-template' / '.gitlab-ci.yml'
    if gitlab_ci.exists():
        assert ('release' in yaml.safe_load(gitlab_ci.read_text())) == expected
    else:
        assert github_release.exists() == expected


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'github', 'include_semantic_release': True}],
    indirect=True,
)
def test_github_release_skipped_on_forks(sub_project: Path) -> None:
    """The release job doesn't run in forks, which lack the upstream tags."""
    workflow = sub_project / '.github' / 'workflows' / 'release.yml'
    job = yaml.safe_load(workflow.read_text())['jobs']['release']
    assert job['if'] == '${{ !github.event.repository.fork }}'


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'gitlab', 'include_semantic_release': True}],
    indirect=True,
)
def test_gitlab_release_skipped_without_token(sub_project: Path) -> None:
    """The release job is skipped without GITLAB_TOKEN, e.g. in forks."""
    gitlab_ci = sub_project / '.gitlab' / 'ci' / 'copier-template' / '.gitlab-ci.yml'
    rules = yaml.safe_load(gitlab_ci.read_text())['release']['rules']
    token_rule = {'if': '$GITLAB_TOKEN == null || $GITLAB_TOKEN == ""', 'when': 'never'}
    default_branch_rule = next(
        rule
        for rule in rules
        if rule['if'] == '$CI_COMMIT_BRANCH == $CI_DEFAULT_BRANCH'
    )
    # Rules match first-wins, so the skip must come before the rule that runs the job
    assert rules.index(token_rule) < rules.index(default_branch_rule)

    contributing = (sub_project / 'CONTRIBUTING.md').read_text()
    assert 'only runs when `GITLAB_TOKEN` is set' in contributing
