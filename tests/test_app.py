import os
import re
from importlib import reload
from pathlib import Path
from subprocess import CompletedProcess

from pytest import MonkeyPatch
from pytest_mock import MockerFixture

from pyorbs import orbs
from pyorbs.app import main
from pyorbs.shell import current_shell_type
from tests.conftest import OrbFixture, RequirementsFixture

reload(orbs)  # ensures coverage captures definitions


def assert_lockfiles_equal(file_1: str, file_2: str) -> None:
    comments = re.compile('^#.*\n?', re.MULTILINE)  # remove comments
    file_1 = comments.sub('', Path(file_1).read_text(encoding='utf-8'))
    file_2 = comments.sub('', Path(file_2).read_text(encoding='utf-8'))
    assert file_1 == file_2


def assert_error(process: 'CompletedProcess[str]', match: str, return_code: int = 1) -> None:
    assert process.returncode == return_code
    assert re.search(f'Error: .*{match}', process.stderr)


def test_keyboard_interrupt(mocker: MockerFixture) -> None:
    mocker.patch('pyorbs.app.Orb.act', side_effect=KeyboardInterrupt)
    assert main(args=['-l']) == 1


def test_help(orb: OrbFixture) -> None:
    assert 'usage:' in orb(['-h']).stdout


def test_version(orb: OrbFixture) -> None:
    assert re.match(r'[0-9]+\.[0-9]+\.[0-9]+', orb(['-v']).stdout)


def test_activate(orb: OrbFixture, requirements: RequirementsFixture) -> None:
    orb(['-m', 'test_orb', '-r', requirements()])  # make
    orb(['test_orb'])  # activate
    assert 'test_orb' in orb(['-c', 'echo $PYORBS_CURRENT_ORB']).stdout  # environment


def test_activate_command(orb: OrbFixture, requirements: RequirementsFixture) -> None:
    orb(['-m', 'test_orb', '-r', requirements()])  # make
    assert 'test_orb' in orb(['test_orb', '-c', 'echo $PYORBS_CURRENT_ORB']).stdout  # environment
    assert 'pip 19.0.1' in orb(['test_orb', '-c', 'pip --version']).stdout  # package


def test_list_and_info(orb: OrbFixture, requirements: RequirementsFixture, tmp_path: Path) -> None:
    assert 'no orbs' in orb(['-l', '--path', str(tmp_path / 'non-existent')]).stdout
    assert 'no orbs' in orb(['-l']).stdout  # empty folder
    orb(['-m', 'test_orb', '-r', requirements()])  # make
    assert 'test_orb' in orb(['-l']).stdout
    orb(['test_orb'])  # activate
    assert 'test_orb *' in orb(['-l']).stdout
    assert 'test_orb' in orb(['-i']).stdout
    orb(['-d', 'test_orb'])  # destroy
    assert 'no orbs' in orb(['-l']).stdout


def test_make(
    orb: OrbFixture, requirements: RequirementsFixture,
    tmp_path: Path, tmp_requirements: RequirementsFixture,
) -> None:
    orb(['-m', 'test_orb', '-r', tmp_requirements()])
    assert_lockfiles_equal(tmp_requirements(lock=True), requirements(lock=True))  # check lockfile
    assert (tmp_path / f'test_orb/bin/activate_orb.{current_shell_type()}').exists()


def test_make_empty(orb: OrbFixture, tmp_path: Path) -> None:
    process = orb(['-m', 'test_orb', '-e', 'python3', '--path', str(tmp_path / 'non_existent')])
    assert 'Making empty orb' in process.stdout


def test_make_errors(
    orb: OrbFixture, tmp_path: Path, tmp_requirements: RequirementsFixture,
) -> None:
    assert_error(
        orb(['-m', 'test', '-r', str(tmp_path)], check=False),
        match='Invalid requirements file',
    )
    assert_error(
        orb(['-m', 'test', '-r', 'non_existent'], check=False),
        match='Requirements file .* not found',
    )
    assert_error(
        orb(['-m', 'test', '-r', tmp_requirements('invalid')], check=False),
        match='Unable to install requirements',
    )
    assert_error(
        orb(['-m', 'test', '-r', tmp_requirements('referred_nonexistent')], check=False),
        match='file .* not found .*referenced by',
    )
    tmp_requirements('invalid_lockfile', lock=True)  # copy lockfile
    assert_error(
        orb(['-m', 'test', '-r', tmp_requirements('invalid_lockfile')], check=False),
        match='Invalid lockfile',
    )

    tmp_requirements('changed', lock=True)  # copy lockfile
    assert_error(
        orb(['-m', 'test', '-r', tmp_requirements('changed')], check=False),
        match='lockfile of .* is outdated',
    )


def test_update_errors(orb: OrbFixture) -> None:
    orb(['-m', 'test_orb'])
    assert_error(orb(['-u', 'test_orb'], check=False), match='requirements file must be specified')


def test_destroy_errors(
    mocker: MockerFixture, orb: OrbFixture, requirements: RequirementsFixture,
) -> None:
    orb(['-m', 'current', '-r', requirements()])
    mocker.patch.dict(os.environ, {'PYORBS_CURRENT_ORB': 'current'})
    assert_error(orb(['-d', 'current'], check=False), match='orb must be deactivated first')


def test_freeze(
    orb: OrbFixture, requirements: RequirementsFixture, tmp_requirements: RequirementsFixture,
) -> None:
    orb(['-f', '-r', tmp_requirements()])  # freeze
    assert_lockfiles_equal(tmp_requirements(lock=True), requirements(lock=True))  # check lockfile


def test_freeze_folder_bare_skip(
    orb: OrbFixture, tmp_path: Path, tmp_requirements: RequirementsFixture,
) -> None:
    path = tmp_path / 'folder'
    path.mkdir()
    tmp_requirements('unchanged', path=path)  # copy requirements file to the target path
    assert re.search(
        'file ".*/unchanged.txt" does not have a lockfile',
        orb(['-f', '-r', str(path)]).stdout,
    )


def test_freeze_referred(
    orb: OrbFixture, requirements: RequirementsFixture, tmp_requirements: RequirementsFixture,
) -> None:
    for change in ('changed', 'unchanged'):
        tmp_requirements(change)  # copy referred file
        for file in ('referred_requirements', 'referred_constraints'):
            lockfile = tmp_requirements(f'{file}_{change}', lock=True)  # copy lockfile
            process = orb(['-f', '-r', tmp_requirements(f'{file}_{change}')])  # freeze
            if change == 'changed':
                actual_lockfile = requirements(f'{file}_{change}', lock=True) + '.actual'
                assert_lockfiles_equal(lockfile, actual_lockfile)
            else:
                assert 'up-to-date' in process.stdout


def test_freeze_errors(orb: OrbFixture, tmp_path: Path) -> None:
    assert_error(orb(['-f'], check=False), match='requirements file must be specified')

    empty_folder = tmp_path / 'empty'
    empty_folder.mkdir()
    assert_error(
        orb(['-f', '-r', str(empty_folder)], check=False),
        match='There are no requirements files in path',
    )


def test_test(orb: OrbFixture, requirements: RequirementsFixture) -> None:
    for change, return_code in {'changed': 1, 'unchanged': 0}.items():
        assert orb(['-t', '-r', requirements(change)], check=False).returncode == return_code
        for file in ('referred_requirements', 'referred_constraints'):
            process = orb(['-t', '-r', requirements(f'{file}_{change}')], check=False)
            assert process.returncode == return_code


def test_legacy_test(requirements: RequirementsFixture) -> None:
    assert not orbs.Orbs.test(requirements('unchanged'))


def test_glow(
    monkeypatch: MonkeyPatch, orb: OrbFixture, requirements: RequirementsFixture,
) -> None:
    monkeypatch.delenv('PYORBS_CURRENT_ORB', raising=False)
    assert_error(orb(['-g'], check=False), match='orb name must be specified')
    orb(['-m', 'test_orb', '-r', requirements()])  # make
    assert 'test_orb' in orb(['-g', 'test_orb']).stdout  # add glow directly
    monkeypatch.setenv('PYORBS_CURRENT_ORB', 'test_orb')
    assert 'test_orb' in orb(['-g']).stdout  # add glow indirectly


def test_bash_completion(orb: OrbFixture) -> None:
    assert 'complete' in orb(['--bash']).stdout


def test_session(orb: OrbFixture, tmp_requirements: RequirementsFixture) -> None:
    orb(['-f', '-r', tmp_requirements()])  # freeze
    orb(['-m', 'test_orb', '-r', tmp_requirements()])  # make
    orb(['-u', 'test_orb', '-r', tmp_requirements()])  # update
    assert 'test_orb' in orb(['-l']).stdout  # list
    assert 'test_orb' in orb(['test_orb', '-c', 'echo $PYORBS_CURRENT_ORB']).stdout  # command
    orb(['test_orb'])  # activate
    assert 'test_orb' in orb(['-g', 'test_orb']).stdout
    assert 'No orb' in orb(['-d', 'test_orb']).stdout  # destroy
    assert_error(orb(['test_orb'], check=False), match='Unknown orb name')
