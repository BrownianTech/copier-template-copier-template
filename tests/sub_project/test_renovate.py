"""Tests for the generated Renovate setup."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import Any

import pytest
import yaml
from copier import run_copy, run_update
from packaging.version import Version
from plumbum import local

from tests.helpers import (
    RENOVATE_ANNOTATION_REGEX,
    git,
    git_save,
    is_git_repo_dirty,
    load_renovate,
)

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
    renovate = load_renovate(sub_project)
    assert preset in renovate['extends']

    dep_names = {
        match['depName']
        for path in sub_project.glob(ci_glob)
        for match in re.finditer(RENOVATE_ANNOTATION_REGEX, path.read_text())
    }
    assert dep_names == expected


@pytest.mark.parametrize('sub_project', [{'vcs_platform': ''}], indirect=True)
def test_no_ci_preset_without_vcs_platform(sub_project: Path) -> None:
    renovate = load_renovate(sub_project)
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
    """Validate the generated renovate.jsonc against Renovate's schema.

    Same check as the check-renovate pre-commit hook, which only sees this repo's
    own renovate.jsonc, not the one generated from renovate.jsonc.tmpl.
    check-jsonschema has no JSONC parser, so this uses its JSON5 one, as JSON5
    is a superset of JSONC.
    """
    check_jsonschema = local[sys.executable]['-m', 'check_jsonschema']
    retcode, stdout, stderr = check_jsonschema.run(
        [
            '--builtin-schema',
            'vendor.renovate',
            '--regex-variant',
            'nonunicode',
            '--default-filetype',
            'json5',
            str(sub_project / 'renovate.jsonc'),
        ],
        retcode=None,
    )
    assert retcode == 0, stdout + stderr


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'github'}, {'vcs_platform': 'gitlab'}, {'vcs_platform': ''}],
    indirect=True,
)
def test_project_markers_close_each_list(sub_project: Path) -> None:
    """Each list ends with a marker, for project entries to go below.

    Template entries then land above it on copier update, and project ones
    below, which merge without conflicts.
    """
    text = (sub_project / 'renovate.jsonc').read_text()
    for marker in (
        'Project presets below',
        'Project managers below',
        'Project rules below',
    ):
        assert re.search(rf'// {marker}\n\s*\],', text), marker


@pytest.mark.skipif(is_git_repo_dirty(), reason='Fail on dirty repo')
@pytest.mark.parametrize('edited', [False, True], ids=['unedited', 'edited'])
def test_update_moves_renovate_json(
    template_dir: Path,
    tmp_path: Path,
    mock_answers_required_without_defaults: dict[str, Any],
    edited: bool,
) -> None:
    """Updating from before the JSONC switch conflicts, keeping any edits.

    The migration moves renovate.json to renovate.jsonc, so it conflicts with
    the new file instead of being deleted, and leaves no renovate.json behind,
    which Renovate would read first.
    """
    worker = run_copy(
        str(template_dir),
        tmp_path,
        vcs_ref='v0.30.3',  # the last release with renovate.json
        defaults=True,
        data=mock_answers_required_without_defaults,
        unsafe=True,
    )
    renovate_json = tmp_path / 'renovate.json'
    project_rule = '"matchPackageNames": ["project-only"]'
    if edited:
        renovate_json.write_text(
            renovate_json.read_text().replace(
                '"packageRules": [',
                f'"packageRules": [\n    {{{project_rule}, "enabled": false}},',
            )
        )
    git_save(tmp_path)
    run_update(
        tmp_path,
        vcs_ref='HEAD',
        defaults=True,
        overwrite=True,
        answers_file=worker.answers_relpath,
        unsafe=True,
        conflict='inline',
    )
    assert not renovate_json.exists()
    renovate_jsonc = (tmp_path / 'renovate.jsonc').read_text()
    assert '<<<<<<< before updating' in renovate_jsonc
    assert '// Project rules below' in renovate_jsonc
    assert (project_rule in renovate_jsonc) == edited


def test_migration_version_follows_renovate_json(template_dir: Path) -> None:
    """The move to renovate.jsonc runs on updates from every release that needs it.

    Copier runs a migration when an update goes from below its version to it
    or above, so it must be after every release with renovate.json. Raise it
    if one is released before the switch.
    """
    copier_yml = yaml.safe_load((template_dir / 'copier.yml').read_text())
    (migration,) = copier_yml['_migrations']
    version = Version(migration['version'])
    with local.cwd(template_dir):
        tags = git('tag', '--list', 'v*').split()
        with_renovate_json = [
            tag
            for tag in tags
            if git['cat-file', '-e', f'{tag}:meta_template/renovate.json.tmpl'].run(
                retcode=None
            )[0]
            == 0
        ]
    assert with_renovate_json
    assert all(Version(tag) < version for tag in with_renovate_json)
