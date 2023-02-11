from pathlib import Path

from pyorbs.orb import Orb


class Orbs:  # pylint: disable=too-few-public-methods
    @staticmethod
    def test(reqs: str, quiet: bool = True) -> int:
        return int(Orb().test(path=Path(reqs), quiet=quiet))
