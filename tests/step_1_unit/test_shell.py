from pytest import raises

from pyorbs.shell import SHELLS, current_shell_type, execute, which


def test_current_shell_type(monkeypatch):
    for shell in SHELLS:
        monkeypatch.setenv('SHELL', shell)
        assert current_shell_type() == shell


def test_current_shell_type_unsupported(monkeypatch):
    monkeypatch.setenv('SHELL', 'unsupported')
    with raises(RuntimeError):
        current_shell_type()


def test_execute(monkeypatch, mocker):
    for shell in SHELLS:
        monkeypatch.setenv('SHELL', shell)
        run = mocker.patch('pyorbs.shell.run')
        execute()
        run.assert_called_with([shell], check=False)


def test_execute_replace(mocker):
    execl = mocker.patch('pyorbs.shell.execl')
    execute(replace=True)
    assert execl.called


def test_execute_capture(mocker):
    run = mocker.patch('pyorbs.shell.run')
    execute(capture=True)
    assert run.called


def test_execute_errors():
    with raises(ValueError):
        execute(init='test', command='test')
    with raises(ValueError):
        execute(replace=True, capture=True)


def test_which():
    assert 'which' in which('which')


def test_which_error():
    with raises(ValueError):
        which('UtTZY9GLiG2tToRlg9q3')  # invalid command
