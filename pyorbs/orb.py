import argparse
import os
import shutil
import subprocess
import sys
import tempfile
from importlib import metadata
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional, Sequence, Set, TypeVar, Union, cast

from pyorbs.requirements import Requirements
from pyorbs.shell import SHELL_TYPES, current_shell_type, execute, which
from pyorbs.templates import render

DEFAULT_REQUIREMENTS = ('requirements.txt', 'requirements/dev.txt')
ActionCallable = TypeVar('ActionCallable', bound=Callable[..., Any])


class Action:  # pylint: disable=too-few-public-methods
    REGISTRY: Dict[str, 'Action'] = {}

    def __init__(self, method: ActionCallable, short: Optional[str] = None):
        if not method.__doc__:
            raise RuntimeError(f'Action method "{method}" must have a docstring')
        self.doc = method.__doc__.strip().splitlines()[0].rstrip('.')
        self.doc = self.doc[:1].lower() + self.doc[1:]
        self.flags = ([f'-{short}'] if short else []) + [f'--{method.__name__}']


def action(short: Optional[str] = None) -> Callable[[ActionCallable], ActionCallable]:
    def register_action(method: ActionCallable) -> ActionCallable:
        Action.REGISTRY[method.__name__] = Action(method=method, short=short)
        return method
    return register_action


class Orb:
    def __init__(
        self,
        args: Optional[Sequence[str]] = None,
        default_requirements: Optional[Sequence[str]] = None,
        default_path: Optional[Path] = None,
    ):
        """
        Manage Python virtual environments.

        Args:
            args: The command-line arguments to use.
            default_requirements: The default requirements to use.
            default_path: The default orb storage path to use.

        """
        xdg_data_home = Path(os.getenv('XDG_DATA_HOME', Path.home() / '.local/share'))
        default_path = default_path or xdg_data_home / 'pyorbs'
        if default_requirements is None:
            config = os.environ.get('PYORBS_DEFAULT_REQUIREMENTS')
            default_requirements = (
                DEFAULT_REQUIREMENTS if config is None
                else (config.split(',') if config else [])
            )
        default_requirements_str = ' or '.join(default_requirements)

        description = str(Orb.__init__.__doc__).strip().splitlines()[0]
        parser = argparse.ArgumentParser(description=description)
        group = parser.add_argument_group(title='actions').add_mutually_exclusive_group()
        for value in Action.REGISTRY.values():
            group.add_argument(*value.flags, action='store_true', help=value.doc)

        parser.add_argument('name', nargs='?',
                            help='name of the orb (default: current orb or glowing orb)')
        parser.add_argument('-r', '--requirements', metavar='X', type=Path,
                            help=f'requirements path (default: {default_requirements_str})')
        parser.add_argument('-c', '--command', metavar='X',
                            help='command to run after orb activation')
        parser.add_argument('-e', '--executable', metavar='X', default=sys.executable,
                            help='the Python executable to use (default: sys.executable)')
        parser.add_argument('--path', metavar='X', type=Path, default=default_path,
                            help='orb storage path (default: $XDG_DATA_HOME/pyorbs)')
        parser.add_argument('--no-cd', action='store_true', help='do not change directory')
        parser.add_argument('--shell', action='store_true', help='activate the orb in a shell')
        parser.add_argument('--bare', action='store_true', help='use the bare requirements file')

        self._args = parser.parse_args(args or [])
        self._default_requirements = [Path(requirement) for requirement in default_requirements]

    def _path(self) -> Path:
        return cast(Path, self._args.path).expanduser()

    def _name(self, use_current: bool = True, use_glowing: bool = True, check: bool = True) -> str:
        name = (
            self._args.name
            or (self._current_orb() if use_current else None)
            or (self._glowing_orb() if use_glowing else None)
        )
        if not name:
            raise ValueError('The orb name must be specified')
        if check and name not in self._orbs():
            raise ValueError(f'Unknown orb name "{name}"')
        return name

    @staticmethod
    def _current_orb() -> Optional[str]:
        return os.getenv('PYORBS_CURRENT_ORB')

    def _orbs(self) -> Set[str]:
        orb_path = self._path()
        if orb_path.exists():
            return set(path.stem for path in orb_path.iterdir() if path.is_dir())
        return set()

    def _glowing_file(self) -> Path:
        return self._path() / 'glowing'

    def _glowing_orb(self) -> Optional[str]:
        glowing_file = self._glowing_file()
        return glowing_file.read_text() if glowing_file.exists() else None

    def _action(self) -> str:
        for value in Action.REGISTRY:
            if getattr(self._args, value):
                return value
        return next(iter(Action.REGISTRY))

    def _requirements(self, path: Optional[Path] = None) -> List[Requirements]:
        path = path or self._args.requirements
        if path and path.is_dir():  # pylint: disable=consider-ternary-expression
            requirements = [
                Requirements(path=item, allow_outdated=True) for item in sorted(path.iterdir())
                if item.is_file() and item.suffix != '.lock'
                and not item.name.startswith('.')
            ]
        else:
            requirements = [Requirements(path=path, allow_outdated=True)]
        if not requirements:
            raise ValueError(f'There are no requirements files in path "{path}"')
        return requirements

    def act(self) -> int:
        result = getattr(self, self._action())() or 0
        if isinstance(result, subprocess.CompletedProcess):
            return result.returncode
        if isinstance(result, bool):
            return int(result)
        return result

    @action(short='a')
    def activate(  # pylint: disable=too-many-arguments
        self,
        name: Optional[str] = None,
        path: Optional[Path] = None,
        command: Optional[str] = None,
        no_cd: Optional[bool] = None,
        capture: bool = False,
    ) -> 'subprocess.CompletedProcess[str]':
        """
        Activate an orb (default).

        Args:
            name: The name of the orb to activate.
            path: The orb storage path to use.
            command: The command to run in the activated orb.
            no_cd: Whether to change the working directory after orb activation.
            capture: Whether to capture the standard output and standard error.

        """
        name = name or self._name()
        path = path or self._path()
        command = command or self._args.command
        init = path / name / f'bin/activate_orb.{current_shell_type()}'
        if not init.exists():
            raise RuntimeError(f'Orb activation file "{init}" not found')
        if not capture:
            print(f'Activating orb "{name}"...')
        if not command:
            self.glow(name=name)
        if command and not capture:
            print(f'Running "{command}"...')

        os.environ['PYORBS_NEW_SHELL'] = str(int(self._args.shell and not command))
        os.environ['PYORBS_NO_CD'] = str(int(no_cd if no_cd is not None else self._args.no_cd))

        return execute(init=init, command=command, replace=not capture, capture=capture)

    @action(short='l')
    def list(self) -> None:
        """
        List orbs.
        """
        orbs = self._orbs()
        if glowing := self._glowing_orb():
            orbs = set(f'{orb} *' if orb == glowing else orb for orb in orbs)
        print('\n'.join(sorted(orbs)) or 'There are no orbs')

    @action(short='m')
    def make(  # pylint: disable=too-many-arguments
        self,
        name: Optional[str] = None,
        path: Optional[Path] = None,
        requirements_path: Optional[Path] = None,
        update: bool = False,
        quiet: bool = False,
    ) -> None:
        """
        Make an orb.
        """
        name = name or self._name(use_current=update, use_glowing=update, check=update)
        path = path or self._path()
        requirements = Requirements(
            path=requirements_path or self._args.requirements,
            default_paths=self._default_requirements,
            bare=self._args.bare,
            required=update,
            allow_outdated=update,
        )

        executable = which(self._args.executable)
        if not quiet:
            print(
                f'{"Updating" if update else "Making"} orb "{name}" using "{requirements}"...'
                if requirements else f'Making empty orb "{name}"'
            )
            print(f'Python executable: {executable}')

        # Creating virtual environment
        if not path.exists():
            path.mkdir(parents=True, exist_ok=True)
        if execute(command=f'{executable} -m venv --clear "{path / name}"').returncode:
            raise RuntimeError('Unable to create virtual environment')

        # Creating activation scripts
        bin_dir = path / f'{name}/bin'
        for shell_type in SHELL_TYPES:
            shell_suffix = f'.{shell_type}' if shell_type != 'bash' else ''
            activate_orb = f'activate_orb.{shell_type}'
            (bin_dir / activate_orb).write_text(render(activate_orb, context={
                'name': name, 'cwd': os.getcwd(),
                'init_file': str(bin_dir / activate_orb),
                'activate_script': str((bin_dir / 'activate').with_suffix(shell_suffix)),
            }))

        # Installing requirements
        if requirements:
            activate_orb = f'activate_orb.{current_shell_type()}'
            command = ' '.join([
                f'source "{bin_dir / activate_orb}"',
                '&& pip install --upgrade pip setuptools wheel',
                f'&& pip install --upgrade --requirement "{requirements}"',
            ])
            if execute(command=command).returncode:
                raise RuntimeError('Unable to install requirements')

            # Generating lockfile
            if requirements.changed:
                # See https://bugs.launchpad.net/ubuntu/+source/python-pip/+bug/1635463
                freeze = 'pip freeze --all --exclude-editable | grep -v "pkg[-_]resources"'
                process = self.activate(name=name, path=path, command=freeze, capture=True)
                requirements.update_lockfile(requirements=process.stdout)

        if not quiet:
            print(f'Orb "{name}" is ready for use')

    @action(short='u')
    def update(self) -> None:
        """
        Update an orb.
        """
        self.make(update=True)

    @action(short='d')
    def destroy(self) -> None:
        """
        Destroy an orb.
        """
        name = self._name(use_current=False, use_glowing=False)
        if self._current_orb() == name:
            raise RuntimeError('The orb must be deactivated first for this operation')
        print(f'Destroying orb "{name}"...')
        if self._glowing_orb() == name:
            self._glowing_file().unlink(missing_ok=True)
            print('No orb shall glow now')
        shutil.rmtree(self._path() / name)

    @action(short='f')
    def freeze(self, path: Optional[Path] = None) -> None:
        """
        Freeze requirements.
        """
        for requirements in self._requirements(path=path):
            skip_freeze = (
                self._args.requirements and self._args.requirements.is_dir()
                and requirements.lockfile and not requirements.lockfile.exists()
            )
            if skip_freeze or not requirements.changed:
                print(requirements.status)
            else:
                print(f'Freezing requirements "{requirements}"...')
                with tempfile.TemporaryDirectory(prefix='pyorbs-') as tmp_path:
                    self.make(
                        name='frozen', path=Path(tmp_path), requirements_path=requirements.path,
                        update=True, quiet=True,
                    )

    @action(short='t')
    def test(self, path: Optional[Path] = None, quiet: bool = False) -> bool:
        """
        Test requirements.
        """
        outdated = False
        for requirements in self._requirements(path=path):
            if requirements.outdated:
                outdated = True
            if not quiet:
                print(requirements.status)
        return outdated

    @action(short='i')
    def info(self) -> None:
        """
        Show outdated packages.
        """
        name = self._name()
        print(f'Orb "{name}"')
        outdated = self.activate(
            name=name, command='pip list --outdated', capture=True,
        ).stdout
        print('\n' + (outdated.strip() or 'All packages are up-to-date'))

    @action(short='g')
    def glow(self, name: Optional[str] = None) -> None:
        """
        Toggle orb glow.
        """
        name = name or self._name(use_glowing=False)
        self._glowing_file().write_text(name)
        print(f'Orb "{name}" is glowing now')

    @staticmethod
    @action(short='v')
    def version() -> None:
        """
        Show version.
        """
        print(metadata.version('pyorbs'))

    @staticmethod
    @action()
    def bash() -> None:
        """
        Print bash completion script.
        """
        print(render('orb-completion.bash').strip())


def main(args: Sequence[str] = tuple(sys.argv[1:])) -> Union[int, str]:
    try:
        return Orb(args=args).act()
    except KeyboardInterrupt:
        return 1
    except (ValueError, RuntimeError) as error:
        return f'Error: {error}'
