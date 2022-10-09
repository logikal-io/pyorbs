"""
A tool for managing Python virtual environments.
"""
import argparse
import os
import sys

from pyorbs.orbs import Orbs
from pyorbs.reqs import Requirements
from pyorbs.templates import render

__project__ = 'pyorbs'
__version__ = '1.6.0'
__author__ = 'Logikal'
__maintainer__ = 'Logikal'
__keywords__ = 'development virtual environment'
__urls__ = {
    'docs': 'https://pyorbs.readthedocs.io',
    'issues': 'https://github.com/logikal-code/pyorbs/issues',
    'releases': 'https://pyorbs.readthedocs.io/en/v%s/sections/changelog.html' % __version__,
    'source': 'https://github.com/logikal-code/pyorbs',
}


def main(args=tuple(sys.argv[1:])):  # pylint: disable=too-many-branches
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_argument_group(title='actions').add_mutually_exclusive_group()
    group.add_argument('-a', '--activate', action='store_true', help='activate an orb (default)')
    group.add_argument('-l', '--list', action='store_true', help='list orbs')
    group.add_argument('-m', '--make', action='store_true', help='make an orb')
    group.add_argument('-u', '--update', action='store_true', help='update an orb')
    group.add_argument('-d', '--destroy', action='store_true', help='destroy an orb')
    group.add_argument('-f', '--freeze', action='store_true', help='freeze requirements')
    group.add_argument('-t', '--test', action='store_true', help='test requirements')
    group.add_argument('-i', '--info', action='store_true', help='orb information')
    group.add_argument('-g', '--glow', action='store_true', help='toggle orb glow')
    group.add_argument('--bash', action='store_true', help='print bash completion script')
    parser.add_argument('name', nargs='?', help='name of the orb (default: glowing orb name)')
    parser.add_argument('-v', '--version', action='store_true', help='show version')
    parser.add_argument('-c', '--command', metavar='X',
                        help='command to be run after orb activation')
    parser.add_argument('-r', '--reqs', default='requirements.txt', metavar='X',
                        help='path to the requirements (default: requirements.txt)')
    parser.add_argument('-e', '--exec', default=sys.executable, metavar='X',
                        help='Python executable to use (default: sys.executable)')
    parser.add_argument('-o', '--orbs', default=os.path.expanduser('~/.pyorbs'), metavar='X',
                        help='orb storage directory (default: ~/.pyorbs)')
    parser.add_argument('-n', '--no-cd', action='store_true', help='do not change directory')
    parser.add_argument('-s', '--shell', action='store_true', help='activate the orb in a shell')
    parser.add_argument('-b', '--bare', action='store_true', help='use the bare requirements file')
    args = parser.parse_args(args)
    try:
        orbs = Orbs(path=args.orbs)
        if args.list:
            orbs.list()
        elif args.make:
            orbs.orb(args.name, new=True).make(Requirements(args.reqs, args.bare), args.exec)
        elif args.update:
            orbs.orb(args.name).make(Requirements(args.reqs, args.bare), args.exec, update=True)
        elif args.destroy:
            orbs.orb(args.name).destroy()
        elif args.info:
            orbs.orb(args.name).info()
        elif args.freeze:
            orbs.freeze(args.reqs, args.exec)
        elif args.test:
            return orbs.test(args.reqs)
        elif args.glow:
            orbs.toggle_glow(args.name)
        elif args.bash:
            print(render('orb-completion.bash').rstrip())
        elif args.version:
            print(__version__)
        else:
            orbs.orb(args.name, shell=args.shell).activate(run=args.command, no_cd=args.no_cd)
        return 0
    except KeyboardInterrupt:
        return 1
    except Exception as error:  # pylint: disable=broad-except
        return 'Error: %s' % error
