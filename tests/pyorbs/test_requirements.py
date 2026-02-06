from pathlib import Path

from pytest import raises

from pyorbs.requirements import Requirements
from tests.pyorbs.conftest import RequirementsFixture


def test_requirements(requirements: RequirementsFixture) -> None:
    # No requirements
    item = Requirements(required=False)
    assert item.path is None
    assert item.lockfile is None
    assert not item.outdated
    assert not item.changed

    # Requirements file without lockfile
    item = Requirements(Path(requirements('no_lockfile')))
    assert not item.outdated
    assert item.changed
    with raises(RuntimeError, match='does not have a lockfile'):
        assert item.lockfile_packages

    # Requirements file with outdated lockfile
    item = Requirements(Path(requirements('changed')), allow_outdated=True)
    packages = Path(requirements('changed', lock=True)).read_text(encoding='utf-8').strip()
    assert item.outdated
    assert item.changed
    assert item.lockfile_packages == '\n'.join(
        line for line in packages.splitlines()
        if not line.startswith('#')
    )


def test_requirements_default_paths(requirements: RequirementsFixture) -> None:
    item = Requirements(default_paths=[Path('non-existent'), Path(requirements('unchanged'))])
    assert item.path == Path(requirements('unchanged'))
    assert not item.outdated
    assert not item.changed


def test_requirements_errors() -> None:
    with raises(RuntimeError, match='Cannot update'):
        Requirements(required=False).update_lockfile('test')
