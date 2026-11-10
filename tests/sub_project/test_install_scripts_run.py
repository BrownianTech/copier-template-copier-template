"""Runs the GitLab CI install scripts against fake tools, without root or network.

Each tool the scripts install, and each command they install it with (apt-get,
curl, install, ...), is a stub on PATH. The stubs for the installers log their
arguments and "install" by copying the pinned version's stubs into place.
"""

from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path

import pytest

from tests.helpers import load_tests_job, scripts_dir

# What the scripts run besides the tools they install and the installers
SYSTEM_COMMANDS = [
    'awk',
    'bash',
    'cat',
    'cp',
    'dirname',
    'grep',
    'head',
    'mktemp',
    'rm',
    'sh',
    'uname',
]


@dataclass(frozen=True)
class Script:
    """An install script, and stubs of what it installs at given versions."""

    name: str
    version_vars: tuple[str, ...]

    def tool_stubs(self, versions: dict[str, str]) -> dict[str, str]:
        """Return stub scripts, by command name, reporting these versions."""
        if self.name == 'install-task.sh':
            task = versions['TASK_VERSION']
            return {'task': f'echo "Task version: v{task} (h1:AbC=)"'}
        if self.name == 'install-uv.sh':
            uv = versions['UV_VERSION']
            return {
                'uv': f'echo "uv {uv} (0123abcd 2026-11-01)"',
                'uvx': f'echo "uvx {uv} (0123abcd 2026-11-01)"',
            }
        cli = versions['DOCKER_CE_CLI_VERSION']
        buildx = versions['DOCKER_BUILDX_PLUGIN_VERSION']
        compose = versions['DOCKER_COMPOSE_PLUGIN_VERSION']
        return {
            'docker': f"""case "$1" in
    --version) echo "Docker version {cli}, build abc1234" ;;
    buildx) echo "github.com/docker/buildx v{buildx} 0123abcd" ;;
    compose) echo "{compose}" ;;
    *) exit 1 ;;
esac""",
        }


def has_debian_codename() -> bool:
    """Return whether the host's os-release names a Debian-style codename.

    install-docker-client.sh reads it from /etc/os-release, which the sandbox
    can't stub. macOS has no such file, and e.g. Arch and Alpine don't set it.
    """
    os_release = Path('/etc/os-release')
    return os_release.is_file() and any(
        line.startswith('VERSION_CODENAME=') and line.split('=', 1)[1].strip('"\'')
        for line in os_release.read_text().splitlines()
    )


SCRIPTS = [
    pytest.param(Script('install-task.sh', ('TASK_VERSION',)), id='install-task.sh'),
    pytest.param(Script('install-uv.sh', ('UV_VERSION',)), id='install-uv.sh'),
    pytest.param(
        Script(
            'install-docker-client.sh',
            (
                'DOCKER_CE_CLI_VERSION',
                'DOCKER_BUILDX_PLUGIN_VERSION',
                'DOCKER_COMPOSE_PLUGIN_VERSION',
            ),
        ),
        id='install-docker-client.sh',
        marks=pytest.mark.skipif(
            not has_debian_codename(),
            reason='needs VERSION_CODENAME in /etc/os-release, as on Debian or Ubuntu',
        ),
    ),
]


def write_stub(directory: Path, name: str, body: str) -> None:
    """Write an executable sh script."""
    directory.mkdir(parents=True, exist_ok=True)
    stub = directory / name
    stub.write_text(f'#!/bin/sh\n{body}\n')
    stub.chmod(0o755)


@dataclass
class Sandbox:
    """Directories on PATH for a script run, and the installers' log."""

    root: Path

    @property
    def shadow(self) -> Path:
        """First on PATH, standing in for e.g. /usr/local/bin."""
        return self.root / 'shadow'

    @property
    def bin(self) -> Path:
        """Where the installers put the tools, standing in for e.g. /usr/bin."""
        return self.root / 'bin'

    @property
    def provides(self) -> Path:
        """What the installers copy into bin when they install."""
        return self.root / 'provides'

    @property
    def log(self) -> Path:
        """Every installer call, one per line."""
        return self.root / 'installers.log'

    def run(self, script: Path, env: dict[str, str]) -> subprocess.CompletedProcess:
        """Run a script with only the sandbox and SYSTEM_COMMANDS on PATH."""
        system = self.root / 'system'
        system.mkdir()
        for command in SYSTEM_COMMANDS:
            found = shutil.which(command)
            assert found, f'{command} not found'
            (system / command).symlink_to(found)
        self.bin.mkdir(exist_ok=True)
        path = os.pathsep.join(str(p) for p in [self.shadow, self.bin, system])
        # The script is the generated project's own, not untrusted input
        return subprocess.run(  # noqa: S603
            [str(system / 'bash'), str(script)],
            env={'PATH': path, 'HOME': str(self.root / 'home'), **env},
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=False,
        )


@pytest.fixture
def sandbox(tmp_path: Path) -> Sandbox:
    """Installer stubs, which log their calls and install from provides."""
    box = Sandbox(tmp_path)
    log = box.log
    install_provided = f'cp "{box.provides}"/* "{box.bin}"/'
    write_stub(
        box.bin,
        'apt-get',
        f'echo "apt-get $*" >> "{log}"\n'
        f'if [ "$1" = install ]; then {install_provided}; fi',
    )
    write_stub(
        box.bin,
        'install',
        f'echo "install $*" >> "{log}"\n'
        # The apt source lists are piped in
        'for arg; do [ "$arg" = /dev/stdin ] && cat > /dev/null; done\n'
        # uv's binaries, the only install to /usr/local/bin
        f'for arg; do last=$arg; done\n'
        f'if [ "$last" = /usr/local/bin/ ]; then {install_provided}; fi',
    )
    write_stub(
        box.bin,
        'curl',
        f'echo "curl $*" >> "{log}"\n'
        'while [ $# -gt 0 ]; do [ "$1" = -o ] && : > "$2"; shift; done',
    )
    for name in ['sha256sum', 'tar']:
        write_stub(box.bin, name, f'echo "{name} $*" >> "{log}"')
    write_stub(box.bin, 'dpkg', 'echo amd64')
    return box


def pinned_versions(sub_project: Path, script: Script) -> dict[str, str]:
    """Return the script's version variables as the tests job sets them."""
    variables = load_tests_job(sub_project)['variables']
    return {var: variables[var] for var in script.version_vars}


def other_versions(versions: dict[str, str]) -> dict[str, str]:
    """Return a different version for each variable."""
    return {var: f'0.0.{len(var)}' for var in versions}


def provide(sandbox: Sandbox, script: Script, versions: dict[str, str]) -> None:
    """Make the installers install these versions."""
    for name, body in script.tool_stubs(versions).items():
        write_stub(sandbox.provides, name, body)
    if script.name == 'install-docker-client.sh':
        # Docker's apt repo, as apt-cache madison lists it
        rows = {
            'docker-ce-cli': versions['DOCKER_CE_CLI_VERSION'],
            'docker-buildx-plugin': versions['DOCKER_BUILDX_PLUGIN_VERSION'],
            'docker-compose-plugin': versions['DOCKER_COMPOSE_PLUGIN_VERSION'],
        }
        body = 'case "$2" in\n'
        for package, version in rows.items():
            body += (
                f'    {package}) echo "{package} | 5:{version}-1~debian.13~trixie'
                f' | https://download.docker.com/linux/debian trixie/stable amd64'
                f' Packages" ;;\n'
            )
        body += 'esac'
        write_stub(sandbox.bin, 'apt-cache', body)


def installer_calls(sandbox: Sandbox) -> list[str]:
    """Return the installer calls a run made."""
    if not sandbox.log.exists():
        return []
    return sandbox.log.read_text().splitlines()


@pytest.mark.parametrize('script', SCRIPTS)
@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_skips_when_pinned_version_installed(
    sub_project: Path, sandbox: Sandbox, script: Script
) -> None:
    """With the pinned versions on PATH, nothing is downloaded or installed."""
    versions = pinned_versions(sub_project, script)
    for name, body in script.tool_stubs(versions).items():
        write_stub(sandbox.bin, name, body)

    result = sandbox.run(scripts_dir(sub_project) / script.name, versions)

    assert result.returncode == 0, result.stderr
    assert 'is already installed' in result.stdout
    assert installer_calls(sandbox) == []


@pytest.mark.parametrize('installed', ['missing', 'other version'])
@pytest.mark.parametrize('script', SCRIPTS)
@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_installs_pinned_version(
    sub_project: Path, sandbox: Sandbox, script: Script, installed: str
) -> None:
    """A missing tool, or another version in the same place, gets the pin."""
    versions = pinned_versions(sub_project, script)
    if installed == 'other version':
        for name, body in script.tool_stubs(other_versions(versions)).items():
            write_stub(sandbox.bin, name, body)
    provide(sandbox, script, versions)

    result = sandbox.run(scripts_dir(sub_project) / script.name, versions)

    assert result.returncode == 0, result.stderr
    assert 'is already installed' not in result.stdout
    assert installer_calls(sandbox)


@pytest.mark.parametrize('script', SCRIPTS)
@pytest.mark.parametrize('sub_project', [{'vcs_platform': 'gitlab'}], indirect=True)
def test_fails_when_another_install_comes_first(
    sub_project: Path, sandbox: Sandbox, script: Script
) -> None:
    """Another version earlier on PATH fails the script, after installing the pin."""
    versions = pinned_versions(sub_project, script)
    for name, body in script.tool_stubs(other_versions(versions)).items():
        write_stub(sandbox.shadow, name, body)
    provide(sandbox, script, versions)

    result = sandbox.run(scripts_dir(sub_project) / script.name, versions)

    assert result.returncode == 1
    assert installer_calls(sandbox)
    assert 'so another install comes first' in result.stderr
    assert str(sandbox.shadow) in result.stderr
