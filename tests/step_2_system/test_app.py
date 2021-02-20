import re
from subprocess import run, PIPE
from shutil import copyfile
from os.path import basename, exists
from pathlib import Path

from pytest import fixture

from pyorbs.app import __version__
from pyorbs.shell import SHELLS, which, current_shell_type


@fixture(autouse=True, params=[which(shell) for shell in SHELLS])
def shells(monkeypatch, request):
    monkeypatch.setenv('SHELL', request.param)


@fixture
def orb(tmp_path):
    def run_orb(args, check=True):
        args = ['python3', '-m', 'pyorbs', '-o', str(tmp_path)] + args
        return run(args, stdout=PIPE, universal_newlines=True, check=check)
    return run_orb


@fixture
def tmp_reqs(tmp_path, reqs):
    def give_tmp_reqs(version='unchanged'):
        return copyfile(reqs(version, raw=True), str(tmp_path / basename(reqs(version, raw=True))))
    return give_tmp_reqs


def lockfiles_equal(file_1, file_2):
    comments = re.compile('^#.*\n?', re.MULTILINE)  # remove comments
    return comments.sub('', Path(file_1).read_text()) == comments.sub('', Path(file_2).read_text())


def test_help(orb):
    assert 'usage:' in orb(['-h']).stdout


def test_version(orb):
    assert orb(['-v']).stdout.strip() == __version__


def test_make(orb, tmp_path, tmp_reqs, reqs):
    orb(['-m', 'test_orb', '-r', tmp_reqs(), '-e', 'python3'])  # make
    assert lockfiles_equal(tmp_reqs() + '.lock', reqs(raw=True) + '.lock')  # lockfile
    assert exists(str(tmp_path / 'test_orb/bin/activate_orb') + '.' + current_shell_type())


def test_activate(orb, reqs):
    orb(['-m', 'test_orb', '-r', reqs(raw=True)])  # make
    orb(['test_orb'])  # activate
    assert 'test_orb' in orb(['-c', 'echo $VIRTUAL_ENV']).stdout  # glowing


def test_command(orb, reqs):
    orb(['-m', 'test_orb', '-r', reqs(raw=True)])  # make
    assert 'test_orb' in orb(['test_orb', '-c', 'echo $VIRTUAL_ENV']).stdout  # check environment
    assert 'pip 19.0.1' in orb(['test_orb', '-c', 'pip --version']).stdout  # check package


def test_info_and_list(orb, reqs):
    assert 'no orbs' in orb(['-l']).stdout
    orb(['-m', 'test_orb', '-r', reqs(raw=True)])  # make
    assert 'test_orb' in orb(['-l']).stdout
    orb(['test_orb'])  # activate
    assert 'test_orb *' in orb(['-l']).stdout
    assert 'test_orb' in orb(['-i']).stdout
    orb(['-d', 'test_orb'])  # destroy
    assert 'no orbs' in orb(['-l']).stdout


def test_freeze(orb, tmp_reqs, reqs):
    orb(['-f', '-r', tmp_reqs()])  # freeze
    assert lockfiles_equal(tmp_reqs() + '.lock', reqs(raw=True) + '.lock')  # lockfile


def test_freeze_referred(orb, tmp_reqs, reqs):
    tmp_reqs('changed')  # copy requirements / constraints file
    for check in ('referred_requirements', 'referred_constraints'):
        orb(['-f', '-r', tmp_reqs('%s_changed' % check)])  # freeze
        assert lockfiles_equal(tmp_reqs('%s_changed' % check) + '.lock',
                               reqs('%s_unchanged' % check, raw=True) + '.lock')  # lockfile


def test_test(orb, reqs):
    assert orb(['-t', '-r', reqs(raw=True)], check=False).returncode == 0
    assert orb(['-t', '-r', reqs('changed', raw=True)], check=False).returncode == 1
    for check in ('referred_requirements', 'referred_constraints'):
        assert orb(['-t', '-r', reqs('%s_changed' % check, raw=True)], check=False).returncode == 1


def test_glow(monkeypatch, orb, reqs):
    monkeypatch.delenv('PYORBS_ACTIVE_ORB', raising=False)
    assert 'No orb' in orb(['-g']).stdout  # no orb is glowing by default
    orb(['-m', 'test_orb', '-r', reqs(raw=True)])  # make
    assert 'test_orb' in orb(['-g', 'test_orb']).stdout  # add glow directly
    assert 'No orb' in orb(['-g', 'test_orb']).stdout  # remove glow directly
    monkeypatch.setenv('PYORBS_ACTIVE_ORB', 'test_orb')
    assert 'test_orb' in orb(['-g']).stdout  # add glow indirectly
    monkeypatch.delenv('PYORBS_ACTIVE_ORB', raising=False)
    assert 'No orb' in orb(['-g']).stdout  # remove glow indirectly


def test_bash_completion(orb):
    assert 'complete' in orb(['--bash']).stdout


def test_session(orb, tmp_reqs):
    orb(['-f', '-r', tmp_reqs()])  # freeze
    orb(['-m', 'test_orb', '-r', tmp_reqs()])  # make
    orb(['-u', 'test_orb', '-r', tmp_reqs()])  # update
    assert 'test_orb' in orb(['-l']).stdout  # list
    assert 'test_orb' in orb(['test_orb', '-c', 'echo $VIRTUAL_ENV']).stdout  # command
    orb(['test_orb'])  # activate
    assert 'No orb' in orb(['-g', 'test_orb']).stdout  # remove glow
    orb(['-d', 'test_orb'])  # destroy
    assert orb(['test_orb'], check=False).returncode == 1  # does not exist anymore
