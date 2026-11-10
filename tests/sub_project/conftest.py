"""Test fixtures for generating the copier template output."""

from __future__ import annotations

import json
import shutil
from collections.abc import Callable
from pathlib import Path
from typing import Any

import pytest
from copier import run_copy

from tests.helpers import git_save


@pytest.fixture(scope='session')
def rendered_sub_project(
    template_dir: Path,
    tmp_path_factory: pytest.TempPathFactory,
    mock_answers_required_without_defaults: dict[str, Any],
) -> Callable[[dict[str, Any] | None], Path]:
    """Return a function that renders the template once per set of answers.

    Rendering is most of the suite's runtime, and many tests ask for the same
    answers. The returned directory is shared by every test that does, so it
    must not be modified: use `sub_project` or `sub_project_factory`, which
    hand each test its own copy.
    """
    renders: dict[str, Path] = {}

    def _render(data: dict[str, Any] | None = None) -> Path:
        merged = mock_answers_required_without_defaults | (data or {})
        key = json.dumps(merged, sort_keys=True, default=repr)
        if key not in renders:
            dst = tmp_path_factory.mktemp('rendered_sub_project')
            run_copy(
                str(template_dir),
                dst,
                vcs_ref='HEAD',
                data=merged,
                defaults=True,
                unsafe=True,
            )
            git_save(dst)
            renders[key] = dst
        return renders[key]

    return _render


@pytest.fixture
def sub_project_factory(
    rendered_sub_project: Callable[[dict[str, Any] | None], Path],
    tmp_path_factory: pytest.TempPathFactory,
) -> Callable[[dict[str, Any] | None], Path]:
    """Return a factory that creates a sub-project from the template with given data.

    Useful for matrix-style tests with multiple independent parametrize decorators:

    ```python
        @pytest.mark.parametrize('opt_a', ['x', 'y'])
        @pytest.mark.parametrize('opt_b', ['p', 'q'])
        def test_example(sub_project_factory, opt_a, opt_b) -> None:
            sub_project = sub_project_factory({'opt_a': opt_a, 'opt_b': opt_b})
            ...
    ```

    Each call returns a fresh copy, committed to its own git repo, that the test
    is free to modify.
    """

    def _factory(data: dict[str, Any] | None = None) -> Path:
        dst = tmp_path_factory.mktemp('sub_project')
        shutil.copytree(
            rendered_sub_project(data), dst, symlinks=True, dirs_exist_ok=True
        )
        return dst

    return _factory


@pytest.fixture
def sub_project(
    request: pytest.FixtureRequest,
    sub_project_factory: Callable[[dict[str, Any] | None], Path],
) -> Path:
    """Create a sub-project by copying the template.

    Can be used directly for default values:

    ```python
        def test_example(sub_project: Path) -> None:
            ...
    ```

    Or with indirect parametrization to pass custom copier data:

    ```python
        @pytest.mark.parametrize(
            ('sub_project','expected'),
            [
                ({'some_option': 'value1'}, 'expected1'),
                ({'some_option': 'value2'}, 'expected2'),
            ],
            indirect=['sub_project'],
        )
        def test_example(sub_project: Path, expected: str) -> None:
            ...
    ```

    """
    return sub_project_factory(getattr(request, 'param', None))
