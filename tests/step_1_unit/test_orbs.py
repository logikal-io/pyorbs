from collections import namedtuple

from pytest import fixture, raises

from pyorbs.orbs import Orbs


@fixture
def orbs(tmp_path):
    orbs = Orbs(str(tmp_path))
    orbs.orbs = ['test']
    return orbs


@fixture
def orb(mocker, orbs):
    mocker.patch('pyorbs.orbs.exists', return_value=True)
    return orbs.orb('test')


@fixture
def make(mocker):
    return mocker.patch('pyorbs.orbs.Orb.make')


@fixture
def make_actions(mocker):
    execute = mocker.patch('pyorbs.orbs.execute')
    execute.return_value.returncode = 0
    mocker.patch('pyorbs.orbs.Orb.activate')
    return {
        'write_text': mocker.patch('pyorbs.orbs.Path.write_text'),
        'execute': execute,
        'lock_reqs': mocker.patch('pyorbs.reqs.Requirements.lock')
    }


def test_list(capsys, orbs):
    orbs.list()
    assert 'test' in capsys.readouterr().out


def test_freeze_invalid_paths(orbs):
    with raises(ValueError):
        orbs.freeze('invalid')
    with raises(ValueError):
        orbs.freeze('tests/reqs/empty')


def test_freeze_changed(orbs, make, reqs):
    orbs.freeze(reqs('changed', raw=True))
    assert make.called


def test_freeze_unchanged(orbs, make, reqs):
    orbs.freeze(reqs(raw=True))
    assert not make.called


def test_freeze_folder(orbs, make):
    orbs.freeze('tests/reqs')
    assert make.called


def test_toggle_glow_invalid_name(orbs):
    with raises(ValueError):
        orbs.toggle_glow('invalid')


def test_toggle_glow(orbs, monkeypatch):
    assert orbs.glowing() is None
    orbs.toggle_glow('test')
    assert orbs.glowing() == 'test'
    orbs.toggle_glow('test', force_on=True)
    assert orbs.glowing() == 'test'
    orbs.toggle_glow('test')
    assert orbs.glowing() is None
    monkeypatch.setenv('PYORBS_ACTIVE_ORB', 'test')
    orbs.toggle_glow()
    assert orbs.glowing() == 'test'


def test_orb_errors(orbs):
    with raises(ValueError):
        Orbs('invalid').orb()
    with raises(ValueError):
        orbs.orb('invalid')
    with raises(RuntimeError):
        orbs.orb()


def test_orb_shell(mocker, orbs):
    execute = mocker.patch('pyorbs.orbs.execute')
    orbs.orb(shell=True)
    assert execute.called


def test_orb_glowing(orbs):
    orbs.toggle_glow('test')
    assert orbs.orb().name == 'test'


def test_orb(orbs):
    assert orbs.orb('test').name == 'test'


def test_make_reqs_changed(orbs, reqs):
    with raises(RuntimeError):
        orbs.orb('test').make(reqs('changed'))


def test_make_venv_error(make_actions, orbs, reqs):
    make_actions['execute'].return_value.returncode = 1
    with raises(RuntimeError):
        orbs.orb('test').make(reqs())


def test_make_install_error(make_actions, orbs, reqs):
    make_actions['execute'].side_effect = [
        namedtuple('CompletedProcess', 'returncode')(0),
        namedtuple('CompletedProcess', 'returncode')(1),
    ]
    with raises(RuntimeError):
        orbs.orb('test').make(reqs())


def test_make(make_actions, orbs, reqs):
    orbs.orb('test').make(reqs())
    assert make_actions['write_text'].called
    assert make_actions['execute'].called
    assert not make_actions['lock_reqs'].called


def test_make_reqs_new(make_actions, orbs, reqs):
    orbs.orb('test').make(reqs('new'))
    assert make_actions['lock_reqs'].called


def test_make_update(make_actions, orbs, reqs):
    orbs.orb('test').make(reqs('changed'), update=True)
    assert make_actions['lock_reqs'].called


def test_make_quiet(mocker, make_actions, orbs, reqs):
    mocked_print = mocker.patch('builtins.print')
    orbs.orb('test').make(reqs(), quiet=True)
    assert not mocked_print.called
    assert not make_actions['lock_reqs'].called


def test_destroy_exit(monkeypatch, orbs):
    monkeypatch.setenv('PYORBS_ACTIVE_ORB', 'test')
    with raises(RuntimeError):
        orbs.orb('test').destroy()


def test_destroy(mocker, orbs):
    mocker.patch('pyorbs.orbs.Orbs.glowing', return_value='test')
    toggle_glow = mocker.patch('pyorbs.orbs.Orbs.toggle_glow')
    rmtree = mocker.patch('pyorbs.orbs.rmtree')
    orbs.orb('test').destroy()
    assert toggle_glow.called
    assert rmtree.called


def test_info(capsys, mocker, orb):
    execute = mocker.patch('pyorbs.orbs.execute')
    execute.return_value.stdout = 'outdated'
    orb.info()
    assert 'outdated' in capsys.readouterr().out


def test_activate_invalid(orbs):
    with raises(RuntimeError):
        orbs.orb('test').activate()


def test_activate(mocker, orb):
    toggle_glow = mocker.patch('pyorbs.orbs.Orbs.toggle_glow')
    execute = mocker.patch('pyorbs.orbs.execute')
    orb.activate()
    toggle_glow.assert_called_with(orb.name, force_on=True)
    execute.assert_called_with(init=orb.orb(), command=None, replace=True, capture=False)


def test_activate_run(mocker, orb):
    execute = mocker.patch('pyorbs.orbs.execute')
    command = 'source "%s"; test' % orb.orb()
    orb.activate(run='test')
    execute.assert_called_with(init=None, command=command, replace=True, capture=False)
    orb.activate(run='test', no_cd=True, capture=True)
    execute.assert_called_with(init=None, command=command, replace=False, capture=True)
