"""Useful methods for testing copier templates."""

import base64
import hashlib
from pathlib import Path

from plumbum import local
from plumbum.cmd import git as _git
from plumbum.machines import LocalCommand
from pytest_gitconfig.plugin import DEFAULT_GIT_USER_EMAIL, DEFAULT_GIT_USER_NAME

git: LocalCommand = _git.with_env(
    GIT_AUTHOR_NAME=DEFAULT_GIT_USER_NAME,
    GIT_AUTHOR_EMAIL=DEFAULT_GIT_USER_EMAIL,
    GIT_COMMITTER_NAME=DEFAULT_GIT_USER_NAME,
    GIT_COMMITTER_EMAIL=DEFAULT_GIT_USER_EMAIL,
)


# Adapted from the copier repo tests
def git_save(
    dst: str | Path,
    message: str = 'Test commit',
    tag: str | None = None,
    allow_empty: bool = False,
) -> None:
    """Save the current repo state in git.

    `$ copier update` / `>>> copier.run_update(...)` requires clean git state

    Args:
        dst: Path to the repo to save.
        message: Commit message.
        tag: Tag to create, optionally.
        allow_empty: Allow creating a commit with no changes

    """
    with local.cwd(dst):
        git('init')
        git('add', '.')
        git('commit', '-m', message, *(['--allow-empty'] if allow_empty else []))
        if tag:
            git('tag', tag)


def is_git_repo_dirty() -> bool:
    """Check if the git repository has uncommitted changes."""
    return bool(git('status', '--porcelain').strip())


def openpgp_fingerprint(armored: str) -> str:
    """V4 fingerprint of the primary key in an ASCII-armored public key block."""
    lines = armored.strip().splitlines()
    body = lines[lines.index('') + 1 :]
    base64_lines = [line for line in body if not line.startswith(('=', '-'))]
    data = base64.b64decode(''.join(base64_lines))
    tag = data[0]
    assert tag & 0x80, 'not an OpenPGP packet'
    if tag & 0x40:  # new-format header
        packet_tag, length_octet = tag & 0x3F, data[1]
        assert length_octet in range(192, 224), 'unsupported packet length'
        length = ((length_octet - 192) << 8) + data[2] + 192
        start = 3
    else:  # old-format header, only 2-byte lengths are used for keys this size
        packet_tag = (tag >> 2) & 0x0F
        assert tag & 0x03 == 1, 'unsupported packet length'
        length = int.from_bytes(data[1:3])
        start = 3
    assert packet_tag == 6, 'first packet is not a public key'
    packet = data[start : start + length]
    assert packet[0] == 4, 'not a v4 key'
    # V4 fingerprints are defined as SHA-1, this only compares against a known value
    digest = hashlib.sha1(b'\x99' + length.to_bytes(2) + packet, usedforsecurity=False)
    return digest.hexdigest().upper()
