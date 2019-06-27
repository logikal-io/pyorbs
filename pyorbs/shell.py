import sys
from os import environ, execl
from subprocess import run, PIPE

SHELLS = ('bash', 'fish')


def current_shell_type():
    for shell in SHELLS:
        if shell in environ['SHELL']:
            return shell
    raise RuntimeError('Shell \'%(SHELL)s\' is not supported' % environ)


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

    shell = environ['SHELL']
    sys.stdout.flush()
    sys.stderr.flush()
    if replace:
        execl(shell, shell, *args)
    elif capture:
        return run([shell] + args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
    else:
        return run([shell] + args)


def which(command):
    """
    Returns the absolute path of the given command.
    """
    which = run(['which', command], stdout=PIPE, universal_newlines=True)
    if which.returncode:
        raise ValueError('Command \'%s\' not found' % command)
    return which.stdout.strip()
