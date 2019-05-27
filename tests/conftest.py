from pytest import fixture

from pyorbs.reqs import Requirements


@fixture
def reqs():
    def give_reqs(version='unchanged', bare=False, raw=False):
        path = 'tests/reqs/%s.txt' % (version if version else '')
        return Requirements(path, bare=bare) if not raw else path
    return give_reqs
