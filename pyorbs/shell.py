import sys
from os import environ, execl
from subprocess import PIPE, run

DEFAULT_SHELL = '/bin/bash'
SHELLS = ('bash', 'fish')


def current_shell_type():
    for shell in SHELLS:
        if shell in environ.get('SHELL', DEFAULT_SHELL):
            return shell
    raise RuntimeError('Shell "%(SHELL)s" is not supported' % environ)


def execute(init=None, command=None, replace=False, capture=False):
    """
    Execute a shell command or start a new interactive session.

    Args:
        init (str): The init file to be used when starting an interactive session.
        command (str): The command to be executed.
        replace (bool): Whether to replace the current process or return the completed process.
        capture (bool): Whether to capture the standard output and standard error.

    """
    if init and command:
        raise ValueError('You cannot use an initialization file with a command')
    if replace and capture:
        raise ValueError('You cannot capture the output when replacing the current process')

    if current_shell_type() == 'bash':
        args = ['--init-file', init] if init else ['-c', command] if command else []
    elif current_shell_type() == 'fish':
        args = ['-C', 'source "%s"' % init] if init else ['-c', command] if command else []

    shell = environ.get('SHELL', DEFAULT_SHELL)
    sys.stdout.flush()
    sys.stderr.flush()
    if replace:
        return execl(shell, shell, *args)
    if capture:
        return run([shell] + args, stdout=PIPE, stderr=PIPE, universal_newlines=True, check=False)
    return run([shell] + args, check=False)


def which(command):
    """
    Returns the absolute path of the given command.
    """
    path = run(['which', command], stdout=PIPE, universal_newlines=True, check=False)
    if path.returncode:
        raise ValueError('Command "%s" not found' % command)
    return path.stdout.strip()
