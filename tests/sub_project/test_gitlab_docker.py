"""Tests for gitlab_docker feature."""

from __future__ import annotations

import json
import os
import re
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

import pytest
import yaml

from tests.helpers import (
    RENOVATE_ANNOTATION_REGEX,
    gitlab_ci_path,
    load_tests_job,
    openpgp_fingerprint,
    scripts_dir,
)

# Each package with the CI variable that pins its version
DOCKER_PACKAGES = {
    'docker-ce-cli': 'DOCKER_CE_CLI_VERSION',
    'docker-buildx-plugin': 'DOCKER_BUILDX_PLUGIN_VERSION',
    'docker-compose-plugin': 'DOCKER_COMPOSE_PLUGIN_VERSION',
}
DOCKER_EXTRACT_VERSION = r'^(?:\d+:)?(?<version>\d+\.\d+\.\d+)-'
# Docker's published fingerprint for its apt repo signing key, see
# https://docs.docker.com/engine/install/debian/
DOCKER_KEY_FINGERPRINT = '9DC858229FC7DD38854AE2D88D81803C0EBFCD88'


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab'}, True),
        ({'vcs_platform': 'gitlab', 'gitlab_docker': True}, True),
        ({'vcs_platform': 'gitlab', 'gitlab_docker': False}, False),
        (
            {
                'vcs_platform': 'gitlab',
                'gitlab_docker': False,
                'gitlab_non_root_tests': True,
            },
            False,
        ),
    ],
    indirect=['sub_project'],
)
def test_gitlab_docker_tests_job(sub_project: Path, expected: bool) -> None:
    """The tests job gets the dind service and Docker client only when enabled."""
    job = load_tests_job(sub_project)
    assert (job.get('services') == [{'name': 'docker:dind'}]) == expected
    assert ('DOCKER_HOST' in job['variables']) == expected
    assert (
        'bash "scripts/copier-template/install-docker-client.sh"'
        in job['before_script']
    ) == expected
    assert (scripts_dir(sub_project) / 'install-docker-client.sh').exists() == expected
    assert (scripts_dir(sub_project) / 'docker.asc').exists() == expected


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_install_docker_client_script(sub_project: Path) -> None:
    """The script installs only the client and plugins, from the committed key."""
    script = scripts_dir(sub_project) / 'install-docker-client.sh'
    assert os.access(script, os.X_OK)
    text = script.read_text()
    for package, variable in DOCKER_PACKAGES.items():
        assert f'apt_version {package} "${variable}"' in text
        # Skipped when the image already has the pinned versions
        assert f'== "${variable}" ]]' in text
    assert '--allow-downgrades' in text
    # The image's Debian release picks the build, it isn't hard-coded
    assert 'VERSION_CODENAME' in text
    assert 'https://download.docker.com/linux/debian' in text
    # The signing key comes from the repo, never the network
    assert '"$script_dir/docker.asc"' in text
    assert 'curl' not in text
    assert 'wget' not in text
    # The daemon runs in the dind service, so it's never installed in the job
    assert 'docker-ce ' not in text
    assert 'docker.io' not in text


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab'}, False),
        ({'vcs_platform': 'gitlab', 'gitlab_docker': False}, True),
        ({'vcs_platform': 'github'}, False),
    ],
    indirect=['sub_project'],
)
def test_gitlab_docker_recorded_only_when_opted_out(
    sub_project: Path, expected: bool
) -> None:
    """Only the non-default answer is recorded, as for other beta flags."""
    answers = yaml.safe_load(
        (sub_project / '.copier-answers.copier-template.yml').read_text()
    )
    assert ('gitlab_docker' in answers) == expected


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_gitlab_docker_apt_key_fingerprint(sub_project: Path) -> None:
    """The committed key is Docker's apt repo signing key."""
    key = scripts_dir(sub_project) / 'docker.asc'
    assert openpgp_fingerprint(key.read_text()) == DOCKER_KEY_FINGERPRINT


@pytest.mark.parametrize(
    ('sub_project', 'expected'),
    [
        ({'vcs_platform': 'gitlab'}, True),
        ({'vcs_platform': 'gitlab', 'gitlab_docker': False}, False),
    ],
    indirect=['sub_project'],
)
def test_docker_client_versions_renovate_managed(
    sub_project: Path, expected: bool
) -> None:
    """Each pinned package is looked up in Docker's repo and updated as a group."""
    gitlab_ci = gitlab_ci_path(sub_project)
    variables = load_tests_job(sub_project)['variables']
    lookups = {
        match['depName']: match.groupdict()
        for match in re.finditer(RENOVATE_ANNOTATION_REGEX, gitlab_ci.read_text())
    }
    for package, variable in DOCKER_PACKAGES.items():
        assert (package in lookups) == expected
        assert (variable in variables) == expected
        if expected:
            lookup = lookups[package]
            assert lookup['datasource'] == 'deb'
            assert lookup['extractVersion'] == DOCKER_EXTRACT_VERSION
            registry_url = urlsplit(lookup['registryUrl'])
            assert registry_url.netloc == 'download.docker.com'
            assert registry_url.path == '/linux/debian'
            # Upstream versions only, with no Debian release in them
            assert re.fullmatch(r'\d+\.\d+\.\d+', variables[variable])
            assert lookup['currentValue'] == variables[variable]

    renovate = json.loads((sub_project / 'renovate.json').read_text())
    groups = [
        rule
        for rule in renovate['packageRules']
        if rule.get('groupName') == 'Docker client'
    ]
    assert bool(groups) == expected
    if expected:
        assert set(groups[0]['matchPackageNames']) == set(DOCKER_PACKAGES)


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_docker_lookups_match_image_release(sub_project: Path) -> None:
    """Renovate checks the Debian release the tests job's image is on.

    Docker builds each release separately and has no alias like `stable`, so
    the lookups name it. Changing the image's release means changing these too.
    """
    gitlab_ci = gitlab_ci_path(sub_project)
    image = load_tests_job(sub_project)['image']['name']
    # Optionally pinned to a digest, as Renovate leaves it
    match = re.fullmatch(
        r'debian:(?P<release>[a-z]+)-slim(?:@sha256:[0-9a-f]{64})?', image
    )
    assert match, f'expected a debian:<release>-slim image, got {image}'
    suites = {
        parse_qs(urlsplit(lookup['registryUrl']).query)['suite'][0]
        for lookup in re.finditer(RENOVATE_ANNOTATION_REGEX, gitlab_ci.read_text())
        if lookup['depName'] in DOCKER_PACKAGES
    }
    assert suites == {match['release']}


@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_docker_client_majors_not_automerged(sub_project: Path) -> None:
    """Generated projects group every Docker update, but review the majors."""
    renovate = json.loads((sub_project / 'renovate.json').read_text())
    rules = [
        rule
        for rule in renovate['packageRules']
        if set(rule.get('matchPackageNames', [])) == set(DOCKER_PACKAGES)
    ]
    assert all('matchUpdateTypes' not in rule for rule in rules if 'groupName' in rule)
    automerged = [rule for rule in rules if rule.get('automerge')]
    assert automerged
    for rule in automerged:
        assert set(rule['matchUpdateTypes']) == {'minor', 'patch'}


def test_root_renovate_groups_docker_client() -> None:
    """Renovate here groups the template's Docker lookups too.

    Its .tmpl manager finds them in meta_template/, and the generated config's
    rule only applies to generated projects.
    """
    root = Path(__file__).parents[2]
    renovate = json.loads((root / 'renovate.json').read_text())
    groups = [
        rule
        for rule in renovate['packageRules']
        if rule.get('groupName') == 'Docker client'
    ]
    assert len(groups) == 1
    assert set(groups[0]['matchPackageNames']) == set(DOCKER_PACKAGES)
    assert groups[0]['matchDatasources'] == ['deb']
