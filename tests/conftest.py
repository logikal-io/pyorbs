import os
from pathlib import Path
from shutil import copyfile
from subprocess import CompletedProcess, run
from typing import List, Optional, Protocol

from pytest import FixtureRequest, fixture
from pytest_mock import MockerFixture

from pyorbs.shell import SHELL_TYPES, which

SHELL = {shell: which(shell) for shell in SHELL_TYPES}


class OrbFixture(Protocol):  # pylint: disable=too-few-public-methods
    def __call__(self, args: List[str], check: bool = ...) -> 'CompletedProcess[str]':
        """Protocol class for the orb fixture."""


@fixture(params=SHELL_TYPES)
def orb(mocker: MockerFixture, request: FixtureRequest, tmp_path: Path) -> OrbFixture:
    mocker.patch.dict(os.environ, {
        'SHELL': SHELL[request.param],
        'PYORBS_DEFAULT_REQUIREMENTS': '',
    })

    def run_orb(args: List[str], check: bool = True) -> 'CompletedProcess[str]':
        run_args = ['python3', '-m', 'pyorbs']
        if '--path' not in args:
            run_args += ['--path', str(tmp_path)]
        run_args += args
        return run(run_args, capture_output=True, text=True, check=check)  # nosec: used for tests
    return run_orb


class RequirementsFixture(Protocol):  # pylint: disable=too-few-public-methods
    def __call__(self, version: str = ..., lock: bool = ..., path: Optional[Path] = ...) -> str:
        """Protocol class for the requirements fixture."""


@fixture
def requirements() -> RequirementsFixture:
    def requirements_path(
        version: str = 'unchanged',
        lock: bool = False,
        path: Optional[Path] = None,
    ) -> str:
        path = path or (Path(__file__).parent / 'requirements')
        return str(path / f'{version}.txt{".lock" if lock else ""}')
    return requirements_path


@fixture
def tmp_requirements(
    tmp_path: Path,
    requirements: RequirementsFixture,  # pylint: disable=redefined-outer-name
) -> RequirementsFixture:
    def tmp_requirements_path(
        version: str = 'unchanged',
        lock: bool = False,
        path: Optional[Path] = None,
    ) -> str:
        original = Path(requirements(version=version, lock=lock))
        return str(copyfile(original, (path or tmp_path) / original.name))
    return tmp_requirements_path
