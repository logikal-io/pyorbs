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
    item = Requirements(Path(requirements('bare')))
    assert not item.outdated
    assert item.changed

    # Requirements file with outdated lockfile
    item = Requirements(Path(requirements('changed')), allow_outdated=True)
    assert item.outdated
    assert item.changed


def test_requirements_default_paths(requirements: RequirementsFixture) -> None:
    item = Requirements(default_paths=[Path('non-existent'), Path(requirements('unchanged'))])
    assert item.path == Path(requirements('unchanged'))
    assert not item.outdated
    assert not item.changed


def test_requirements_errors() -> None:
    with raises(RuntimeError, match='Cannot update'):
        Requirements(required=False).update_lockfile('test')
