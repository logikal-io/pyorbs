import sys
from typing import Sequence, Union

from pyorbs.orb import Orb


def main(args: Sequence[str] = tuple(sys.argv[1:])) -> Union[int, str]:
    try:
        return Orb(args=args).act()
    except KeyboardInterrupt:
        return 1
    except (ValueError, RuntimeError) as error:
        return f'Error: {error}'
