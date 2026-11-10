"""Tests for gitlab_prebuilt_ci_image feature."""

from __future__ import annotations

import re
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
import yaml

from tests.helpers import gitlab_ci_path, load_gitlab_ci

BUILD_JOB = 'build-copier-template-ci-image'
IMAGE_INPUTS = ['.gitlab/ci/copier-template/**/*', 'scripts/copier-template/**/*']


def dockerfile_path(sub_project: Path) -> Path:
    return gitlab_ci_path(sub_project).parent / 'image' / 'Dockerfile'


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab'}, False),
        ({'vcs_platform': 'gitlab', 'gitlab_prebuilt_ci_image': False}, False),
        ({'vcs_platform': 'gitlab', 'gitlab_prebuilt_ci_image': True}, True),
        (
            {
                'vcs_platform': 'gitlab',
                'gitlab_prebuilt_ci_image': True,
                'gitlab_non_root_tests': True,
            },
            True,
        ),
    ],
    indirect=['sub_project'],
)
def test_prebuilt_ci_image_jobs(sub_project: Path, expected: bool) -> None:
    """The build job and the tests job's use of its image only when opted in."""
    gitlab_ci = load_gitlab_ci(sub_project)
    tests = gitlab_ci['tests']
    assert (BUILD_JOB in gitlab_ci) == expected
    assert dockerfile_path(sub_project).exists() == expected
    if not expected:
        assert tests['image'] == {'name': 'debian:trixie-slim'}
        assert tests['needs'] == []
        assert 'rules' not in tests
        return

    # The tests run in the image built for this commit when its inputs changed,
    # and in :latest otherwise
    assert tests['image']['name'] == (
        '$CI_REGISTRY_IMAGE/copier-template-ci:$TESTS_IMAGE_TAG'
    )
    assert tests['variables']['TESTS_IMAGE_TAG'] == 'latest'
    assert tests['needs'] == [{'job': BUILD_JOB, 'optional': True}]
    changed, otherwise = tests['rules']
    assert changed == {
        'changes': IMAGE_INPUTS,
        'variables': {'TESTS_IMAGE_TAG': '$CI_COMMIT_SHORT_SHA'},
    }
    assert otherwise == {'when': 'on_success'}

    build = gitlab_ci[BUILD_JOB]
    assert build['rules'] == [{'changes': IMAGE_INPUTS}]
    # Same variables as the tests job, so one pinned copy of each version
    assert build['variables'] == tests['variables']
    script = build['script'][0]
    assert '--tag "$image:$CI_COMMIT_SHORT_SHA"' in script
    assert '--push' in script
    assert script.rstrip().endswith('"scripts/copier-template"')


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'gitlab', 'gitlab_prebuilt_ci_image': True}],
    indirect=True,
)
def test_prebuilt_ci_image_build_args(sub_project: Path) -> None:
    """The image is built with every version the tests job pins, and its Pythons."""
    gitlab_ci = load_gitlab_ci(sub_project)
    script = gitlab_ci[BUILD_JOB]['script'][0]
    build_args = dict(
        re.match(r'(\w+)(?:="(.*)")?$', arg).groups()
        for arg in re.findall(r'--build-arg (\S+(?: \S+)*?)(?= \\| --)', script)
    )
    pinned = {
        name
        for name in gitlab_ci['tests']['variables']
        if name.endswith('_VERSION') and name != 'PYTHON_VERSION'
    }
    # Taken from the job's environment, so not repeated in the build command
    assert {name for name, value in build_args.items() if value is None} == pinned
    (python_versions,) = gitlab_ci['tests']['parallel']['matrix']
    assert build_args['PYTHON_VERSIONS'] == ' '.join(python_versions['PYTHON_VERSION'])

    dockerfile = dockerfile_path(sub_project).read_text()
    assert set(re.findall(r'^ARG (\w+)$', dockerfile, re.MULTILINE)) == {
        *pinned,
        'PYTHON_VERSIONS',
    }
    # A tag, for the generated project's Renovate to pin
    assert re.search(r'^FROM debian:trixie-slim$', dockerfile, re.MULTILINE)
    for script_name in ('install-uv.sh', 'install-task.sh', 'install-docker-client.sh'):
        assert f'bash /tmp/install/{script_name}' in dockerfile
        assert (sub_project / 'scripts' / 'copier-template' / script_name).exists()


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'gitlab', 'gitlab_prebuilt_ci_image': True}],
    indirect=True,
)
def test_prebuilt_ci_image_scheduled_build_skips_cache(sub_project: Path) -> None:
    """A schedule rebuilds from scratch, as the cache would keep the apt layer."""
    script = load_gitlab_ci(sub_project)[BUILD_JOB]['script'][0]
    assert 'if [ "$CI_PIPELINE_SOURCE" = schedule ]; then' in script
    assert 'no_cache="--no-cache"' in script
    assert re.search(r'^\s+\$no_cache \\$', script, re.MULTILINE)


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'gitlab', 'gitlab_prebuilt_ci_image': True}],
    indirect=True,
)
def test_prebuilt_ci_image_build_not_interruptible(sub_project: Path) -> None:
    """A cancelled build would leave :latest behind, until the inputs change."""
    assert load_gitlab_ci(sub_project)[BUILD_JOB]['interruptible'] is False


@pytest.mark.parametrize(
    'sub_project',
    [{'vcs_platform': 'gitlab', 'gitlab_prebuilt_ci_image': True}],
    indirect=True,
)
def test_prebuilt_ci_image_pythons_on_path(sub_project: Path) -> None:
    """The image's Pythons are found on PATH, not through a root-owned uv dir.

    With UV_PYTHON_INSTALL_DIR in the image's environment, uv would download a
    Python the image lacks into that directory, which the non-root user can't
    write to.
    """
    dockerfile = dockerfile_path(sub_project).read_text()
    assert 'ENV UV_PYTHON_INSTALL_DIR' not in dockerfile
    assert (
        'UV_PYTHON_INSTALL_DIR=/opt/uv/python UV_PYTHON_BIN_DIR=/usr/local/bin \\\n'
        '        uv python install $PYTHON_VERSIONS'
    ) in dockerfile


@pytest.mark.parametrize(
    'sub_project',
    [
        {'vcs_platform': 'gitlab'},
        {'vcs_platform': 'gitlab', 'gitlab_prebuilt_ci_image': True},
        {'vcs_platform': 'gitlab', 'gitlab_non_root_tests': True},
        {
            'vcs_platform': 'gitlab',
            'gitlab_prebuilt_ci_image': True,
            'gitlab_non_root_tests': True,
        },
    ],
    indirect=True,
)
def test_tests_job_leaves_python_to_uv_sync(sub_project: Path) -> None:
    """The UV_PYTHON version is left to uv sync to find or download, as on GitHub."""
    tests = load_gitlab_ci(sub_project)['tests']
    assert not any('uv python' in cmd for cmd in tests['before_script'])
    assert tests['variables']['UV_PYTHON'] == '$PYTHON_VERSION'


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab'}, False),
        ({'vcs_platform': 'gitlab', 'gitlab_prebuilt_ci_image': True}, True),
    ],
    indirect=['sub_project'],
)
def test_prebuilt_ci_image_answer_recorded_only_on_opt_in(
    sub_project: Path, expected: bool
) -> None:
    """Beta flag: unrecorded unless opted in, so a later rollout asks fresh."""
    answers = yaml.safe_load(
        (sub_project / '.copier-answers.copier-template.yml').read_text()
    )
    assert ('gitlab_prebuilt_ci_image' in answers) == expected


@pytest.mark.parametrize(
    ('data', 'message'),
    [
        ({'vcs_platform': 'github'}, 'only supported with GitLab'),
        ({'vcs_platform': ''}, 'only supported with GitLab'),
        ({'vcs_platform': 'gitlab', 'gitlab_docker': False}, 'needs gitlab_docker'),
    ],
)
def test_prebuilt_ci_image_rejected(
    sub_project_factory: Callable[[dict[str, Any] | None], Path],
    data: dict[str, Any],
    message: str,
) -> None:
    """Opting in without GitLab, or without docker:dind to build with, fails."""
    with pytest.raises(ValueError, match=message):
        sub_project_factory({**data, 'gitlab_prebuilt_ci_image': True})
