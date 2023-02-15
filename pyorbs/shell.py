import os
import sys
from pathlib import Path
from subprocess import CompletedProcess, run
from typing import Optional

SHELL_TYPES = ('bash', 'fish')


def current_shell(default: str = 'bash') -> str:
    return os.environ.get('SHELL', which(default))


def current_shell_type(shell: Optional[str] = None) -> str:
    shell = shell or current_shell()
    for shell_type in SHELL_TYPES:
        if shell_type in shell:
            return shell_type
    raise RuntimeError(f'Shell "{shell}" is not supported')


def execute(
    init: Optional[Path] = None,
    command: Optional[str] = None,
    replace: bool = False,
    capture: bool = False,
) -> 'CompletedProcess[str]':
    """
    Execute a shell command or start a new interactive session.

    Args:
        init: The initialization file to use.
        command: The command to execute.
        replace: Whether to replace the current process or return the completed process.
        capture: Whether to capture the standard output and standard error.

    """
    if replace and capture:
        raise ValueError('The output cannot be captured when replacing the current process')

    shell = current_shell()
    args = [shell]
    if init and command:
        command = f'source "{init}"; {command}'
    if init and not command:
        shell_type = current_shell_type(shell=shell)  # nosec: just a helper function
        if shell_type == 'bash':
            args += ['--init-file', str(init)]
        elif shell_type == 'fish':
            args += ['--init-command', f'source "{init}"']
    if command:
        args += ['-c', command]

    sys.stdout.flush()
    sys.stderr.flush()
    if replace:
        return os.execv(shell, args)  # nosec: trusted input
    return run(args, capture_output=capture, text=True, check=False)  # nosec: trusted input


def which(command: str) -> str:
    """
    Return the absolute path of the given command.
    """
    args = ['which', command]
    process = run(args, capture_output=True, text=True, check=False)  # nosec: trusted input
    if process.returncode:
        raise ValueError(f'Command "{command}" not found')
    return process.stdout.strip()
