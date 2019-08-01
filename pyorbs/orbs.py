import sys
import tempfile
from os import path, getcwd, walk, remove, environ
from pathlib import Path
from os.path import exists, isdir, join
from shutil import rmtree

from pyorbs.templates import render
from pyorbs.shell import execute, current_shell_type, SHELLS, which
from pyorbs.reqs import Requirements


class Orbs:
    def __init__(self, path):
        self.path = path
        self.orbs = next(walk(path))[1] if exists(path) else []
        self._glowing_file = join(self.path, '.glowing')

    def list(self):
        orbs = [orb + ' *' if orb == self.glowing() else orb for orb in self.orbs]
        print('Available orbs:\n' + '\n'.join(orbs) if orbs else 'There are no orbs')

    @staticmethod
    def freeze(reqs, executable=sys.executable):
        """
        Freeze the requirements files in a given path.

        Args:
            reqs (str): The path to the requirements files.
            executable (str): The Python executable to use.

        """
        if not exists(reqs):
            raise ValueError('Requirements path \'%s\' not found' % reqs)
        if isdir(reqs):
            reqs_list = [Requirements(join(reqs, reqs_file)) for reqs_file in next(walk(reqs))[2]
                         if not (reqs_file.endswith('.lock') or reqs_file.startswith('.'))]
        else:
            reqs_list = [Requirements(reqs)]
        if not reqs_list:
            raise ValueError('There are no requirements files in path \'%s\'' % reqs)
        for reqs in reqs_list:
            if reqs.changed:
                print('Freezing requirements \'%s\'...' % reqs.path)
                with tempfile.TemporaryDirectory(prefix='pyorbs-') as tmp_path:
                    orb = Orbs(tmp_path).orb(name='frozen', new=True)
                    orb.make(reqs, executable, quiet=True, update=True)
            else:
                print('Requirements lockfile of \'%s\' is up-to-date' % reqs.path)

    def glowing(self):
        return Path(self._glowing_file).read_text() if exists(self._glowing_file) else None

    def toggle_glow(self, name=None, force_on=False):
        """
        Toggle orb glow.

        Args:
            name (str): The name of the orb. Defaults to the currently active orb.
            force_on (bool): Whether to force orb glow to be turned on.

        """
        name = name or environ.get('PYORBS_ACTIVE_ORB', None)
        if (not name or name == self.glowing()) and not force_on:
            if exists(self._glowing_file):
                remove(self._glowing_file)
            print('No orb shall glow now')
        elif name not in self.orbs:
            raise ValueError('Invalid orb name \'%s\'' % name)
        else:
            Path(self._glowing_file).write_text(name)
            print('Orb \'%s\' is glowing now' % name)

    def orb(self, name=None, new=False, shell=False):
        """
        Create an Orb instance.

        Args:
            name (str): The name of the orb. Defaults to the name of the glowing orb.
            new (bool): Whether the orb is new or if it shall exist already.
            shell (bool): Whether to use a wrapper shell.

        """
        name = name or self.glowing()
        if not name and shell:
            execute(replace=True)
        elif not exists(self.path) and not new:
            raise ValueError('Orb storage folder \'%s\' does not exist' % self.path)
        elif not name:
            raise RuntimeError('There is no glowing orb')
        elif name not in self.orbs and not new:
            raise ValueError('Invalid orb name \'%s\'' % name)
        return Orb(name=name, orbs=self, shell=shell)


class Orb:
    def __init__(self, name, orbs, shell):
        """
        Args:
            name (str): The name of the orb.
            orbs (Orbs): An orb factory instance.
            shell (bool): Whether to activate the orb in a shell.

        """
        self.name = name
        self._orbs = orbs
        self._shell = shell

    def orb(self, shell_type=current_shell_type()):
        return join(self._orbs.path, self.name, 'bin/activate_orb') + '.' + shell_type

    def make(self, reqs, executable=sys.executable, quiet=False, update=False):
        """
        Create or update the orb and generate a lockfile when necessary.

        Args:
            reqs (Requirements): The requirements to be used for package installation.
            executable (str): The Python executable to use.
            quiet (bool): Whether to suppress info messages.
            update (bool): Whether to update the orb including the relevant lockfile.

        """
        executable = path.realpath(which(executable))
        if not update and exists(reqs.locked) and reqs.changed:
            raise RuntimeError('Requirements lockfile of \'%s\' is out-of-date' % reqs.path)
        if not quiet:
            verb = 'Updating' if update else 'Making'
            print('%s orb \'%s\' using \'%s\'...' % (verb, self.name, reqs))
            print('Python executable: %s' % executable)

        # Creating virtual environment
        command = '%s -m venv --clear "%s"' % (executable, join(self._orbs.path, self.name))
        if execute(command=command).returncode:
            raise RuntimeError('Unable to create virtual environment')

        # Creating activation scripts
        for shell in SHELLS:
            activate = join(self._orbs.path, self.name, 'bin/activate')
            Path(self.orb(shell)).write_text(render('activate_orb.' + shell, {
                'name': self.name, 'cwd': getcwd(), 'init_file': self.orb(shell),
                'activate_script': activate + ('.' + shell if shell != 'bash' else ''),
            }))

        # Installing requirements
        command = 'source "%s" && pip install --upgrade pip' % self.orb()
        command += ' && pip install --upgrade -r "%s"' % reqs
        if execute(command=command).returncode:
            raise RuntimeError('Unable to install requirements')

        # Generating lockfile
        if reqs.changed:
            freeze = 'pip freeze --all | grep -v "pkg-resources"'
            reqs.lock(self.activate(run=freeze, capture=True).stdout)
        if not quiet:
            print('Orb \'%s\' is ready for use' % self.name)

    def destroy(self):
        if environ.get('PYORBS_ACTIVE_ORB', None) == self.name:
            raise RuntimeError('You must exit the orb first for this operation')
        print('Destroying orb \'%s\'...' % self.name)
        if self._orbs.glowing() == self.name:
            self._orbs.toggle_glow(self.name)
        rmtree(join(self._orbs.path, self.name))

    def activate(self, run=None, no_cd=False, capture=False):
        """
        Activate the orb.

        Args:
            run (str): A command to run in the activated orb.
            no_cd (bool): Do not change the working directory after orb activation.
            capture (bool): Whether to capture the standard output and standard error.

        """
        if not exists(self.orb()):
            raise RuntimeError('Orb file \'%s\' not found' % self.orb())
        if not capture:
            print('Activating orb \'%s\'...' % self.name)
        if not run:
            self._orbs.toggle_glow(self.name, force_on=True)
        if run and not capture:
            print('Running \'%s\'...' % run)

        environ['PYORBS_SHELL'] = str(int(self._shell and not run))
        environ['PYORBS_NO_CD'] = str(int(no_cd))

        init = self.orb() if not run else None
        command = 'source "%s"; %s' % (self.orb(), run) if run else None
        return execute(init=init, command=command, replace=not capture, capture=capture)
