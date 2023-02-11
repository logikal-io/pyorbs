import os
from pathlib import Path
from subprocess import CompletedProcess
from types import SimpleNamespace

from pytest import raises
from pytest_mock import MockerFixture

from pyorbs.orb import Orb, action


def test_invalid_action() -> None:
    with raises(RuntimeError, match='must have a docstring'):
        class Invalid:  # pylint: disable=too-few-public-methods, unused-variable
            @staticmethod
            @action()
            def missing_docstring() -> None:
                ...


def test_activate(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch.dict(os.environ, {'SHELL': 'bash'})
    mocker.patch('pyorbs.orb.Orb.glow')
    init = tmp_path / 'test/bin/activate_orb.bash'
    init.parent.mkdir(parents=True)
    init.touch()
    execute = mocker.patch('pyorbs.orb.execute', return_value=CompletedProcess([], returncode=0))
    Orb(args=['test', '--path', str(tmp_path)]).act()
    execute.assert_called_with(init=init, command=None, replace=True, capture=False)


def test_activate_error() -> None:
    with raises(RuntimeError, match='activation file .* not found'):
        Orb().activate(name='test', path=Path('invalid'))


def test_make_venv_error(mocker: MockerFixture, tmp_path: Path) -> None:
    mocker.patch('pyorbs.orb.execute', return_value=SimpleNamespace(returncode=1))
    with raises(RuntimeError, match='Unable to create virtual environment'):
        Orb().make(name='test', path=tmp_path)
