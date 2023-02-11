import os
from pathlib import Path
from types import SimpleNamespace

from pytest import raises
from pytest_mock import MockerFixture

from pyorbs.shell import SHELL_TYPES, current_shell_type, execute, which


def test_current_shell_type(mocker: MockerFixture) -> None:
    for shell_type in SHELL_TYPES:
        mocker.patch.dict(os.environ, {'SHELL': shell_type})
        assert current_shell_type() == shell_type


def test_current_shell_type_unsupported(mocker: MockerFixture) -> None:
    mocker.patch.dict(os.environ, {'SHELL': 'unsupported'})
    with raises(RuntimeError, match='Shell .* is not supported'):
        current_shell_type()


def test_execute(mocker: MockerFixture) -> None:
    mocker.patch('pyorbs.shell.current_shell', return_value='bash')
    run = mocker.patch('pyorbs.shell.run')
    execute()
    run.assert_called_with(['bash'], capture_output=False, text=True, check=False)


def test_execute_init(mocker: MockerFixture) -> None:
    for shell in SHELL_TYPES:
        mocker.patch('pyorbs.shell.current_shell', return_value=shell)
        run = mocker.patch('pyorbs.shell.run')
        execute(init=Path('test'))
        assert run.called


def test_execute_replace(mocker: MockerFixture) -> None:
    execv = mocker.patch('pyorbs.shell.os.execv')
    execute(replace=True)
    assert execv.called


def test_execute_errors() -> None:
    with raises(ValueError, match='cannot be captured when replacing'):
        execute(replace=True, capture=True)


def test_which() -> None:
    assert 'which' in which('which')


def test_which_error(mocker: MockerFixture) -> None:
    mocker.patch('pyorbs.shell.run', return_value=SimpleNamespace(returncode=1))
    with raises(ValueError, match='not found'):
        which('test')
