"""Tests for the generated Renovate setup."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
from plumbum import local

from tests.helpers import RENOVATE_ANNOTATION_REGEX

DOCKER_CLIENT = {'docker-ce-cli', 'docker-buildx-plugin', 'docker-compose-plugin'}


@pytest.mark.parametrize(
    ('sub_project', 'preset', 'ci_glob', 'expected'),
    [
        (
            {'vcs_platform': 'github'},
            'customManagers:githubActionsVersions',
            '.github/workflows/*.yml',
            {'astral-sh/uv', 'go-task/task'},
        ),
        (
            {'vcs_platform': 'gitlab'},
            'customManagers:gitlabPipelineVersions',
            '.gitlab/ci/**/.gitlab-ci.yml',
            {'astral-sh/uv', 'go-task/task'} | DOCKER_CLIENT,
        ),
        (
            {'vcs_platform': 'gitlab', 'gitlab_docker': False},
            'customManagers:gitlabPipelineVersions',
            '.gitlab/ci/**/.gitlab-ci.yml',
            {'astral-sh/uv', 'go-task/task'},
        ),
    ],
    indirect=['sub_project'],
)
def test_ci_tool_versions_renovate_managed(
    sub_project: Path, preset: str, ci_glob: str, expected: set[str]
) -> None:
    """CI tool versions are annotated for the platform's Renovate preset."""
    renovate = json.loads((sub_project / 'renovate.json').read_text())
    assert preset in renovate['extends']

    dep_names = {
        match['depName']
        for path in sub_project.glob(ci_glob)
        for match in re.finditer(RENOVATE_ANNOTATION_REGEX, path.read_text())
    }
    assert dep_names == expected


@pytest.mark.parametrize('sub_project', [{'vcs_platform': ''}], indirect=True)
def test_no_ci_preset_without_vcs_platform(sub_project: Path) -> None:
    renovate = json.loads((sub_project / 'renovate.json').read_text())
    assert renovate['extends'] == ['config:best-practices']


@pytest.mark.parametrize(
    'sub_project',
    [
        {'vcs_platform': 'github'},
        {'vcs_platform': 'github', 'include_actions_lockfile': True},
        {'vcs_platform': 'gitlab'},
        {'vcs_platform': 'gitlab', 'gitlab_docker': False},
        {'vcs_platform': ''},
    ],
    indirect=True,
)
def test_renovate_config_matches_schema(sub_project: Path) -> None:
    """Validate the generated renovate.json against Renovate's schema.

    Same check as the check-renovate pre-commit hook, which only sees this repo's
    own renovate.json, not the one generated from renovate.json.tmpl.
    """
    check_jsonschema = local[sys.executable]['-m', 'check_jsonschema']
    retcode, stdout, stderr = check_jsonschema.run(
        [
            '--builtin-schema',
            'vendor.renovate',
            '--regex-variant',
            'nonunicode',
            str(sub_project / 'renovate.json'),
        ],
        retcode=None,
    )
    assert retcode == 0, stdout + stderr
