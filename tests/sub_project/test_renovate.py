"""Tests for the generated Renovate setup."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import pytest
import yaml
from plumbum import local

# The match string shared by Renovate's customManagers:githubActionsVersions and
# customManagers:gitlabPipelineVersions presets
RENOVATE_ANNOTATION_REGEX = (
    r'# renovate: datasource=(?P<datasource>[a-zA-Z0-9-._]+?) '
    r'depName=(?P<depName>[^\s]+?)'
    r'(?: (?:lookupName|packageName)=(?P<packageName>[^\s]+?))?'
    r'(?: versioning=(?P<versioning>[^\s]+?))?'
    r'(?: extractVersion=(?P<extractVersion>[^\s]+?))?'
    r'(?: registryUrl=(?P<registryUrl>[^\s]+?))?'
    r'\s+[A-Za-z0-9_]+?_VERSION\s*:\s*["\']?(?P<currentValue>.+?)["\']?\s'
)


@pytest.mark.parametrize(
    ('sub_project', 'preset', 'ci_glob'),
    [
        (
            {'vcs_platform': 'github'},
            'customManagers:githubActionsVersions',
            '.github/workflows/*.yml',
        ),
        (
            {'vcs_platform': 'gitlab'},
            'customManagers:gitlabPipelineVersions',
            '.gitlab/ci/**/.gitlab-ci.yml',
        ),
    ],
    indirect=['sub_project'],
)
def test_ci_tool_versions_renovate_managed(
    sub_project: Path, preset: str, ci_glob: str
) -> None:
    """CI tool versions are annotated for the platform's Renovate preset."""
    renovate = json.loads((sub_project / 'renovate.json').read_text())
    assert preset in renovate['extends']

    dep_names = {
        match['depName']
        for path in sub_project.glob(ci_glob)
        for match in re.finditer(RENOVATE_ANNOTATION_REGEX, path.read_text())
    }
    assert dep_names == {'astral-sh/uv', 'go-task/task'}


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


def gitlab_image_manager_regex() -> re.Pattern[str]:
    """Return the match string this repo's Renovate uses for GitLab CI images."""
    renovate = json.loads((Path(__file__).parents[2] / 'renovate.json').read_text())
    manager = next(
        manager
        for manager in renovate['customManagers']
        if any('gitlab-ci' in pattern for pattern in manager['managerFilePatterns'])
        and manager.get('datasourceTemplate') == 'docker'
    )
    (match_string,) = manager['matchStrings']
    # Renovate's named groups are JavaScript style, (?<name>...)
    return re.compile(match_string.replace('(?<', '(?P<'))


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'gitlab'}, {'vcs_platform': 'gitlab', 'gitlab_docker': False}],
    indirect=True,
)
def test_gitlab_images_digest_pinned(sub_project: Path) -> None:
    """Every GitLab CI image is pinned the way generated projects' Renovate pins it.

    This repo's Renovate then keeps the pins current, so projects without
    Renovate get them on copier update, and projects with it already match.
    """
    pattern = gitlab_image_manager_regex()
    images = []
    for path in sub_project.glob('.gitlab/ci/**/.gitlab-ci.yml'):
        for job in yaml.safe_load(path.read_text()).values():
            if not isinstance(job, dict):
                continue
            images.extend(
                ref['name'] if isinstance(ref, dict) else ref
                for ref in [job.get('image'), *job.get('services', [])]
                if ref is not None
            )
    assert images
    for image in images:
        assert pattern.fullmatch(image), f'{image} is not digest-pinned'
