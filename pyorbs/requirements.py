import hashlib
import re
from pathlib import Path
from typing import List, Optional, Sequence

from pyorbs.templates import render


class ProcessedRequirements:  # pylint: disable=too-few-public-methods
    def __init__(self, path: Path, lockfile: Path):
        stored_hash = self._get_stored_hash(lockfile) if lockfile.exists() else None

        # Derive current hash and options (including from dependencies)
        current_hash = hashlib.sha256()
        options: List[str] = []
        done = {path: False}
        while not all(done.values()):  # pylint: disable=while-used
            requirements = [entry for entry, processed in done.items() if not processed][0]
            if not requirements.exists():
                raise RuntimeError(
                    f'Requirements file "{requirements}" not found (referenced by "{path}")'
                )
            text = requirements.read_text()
            current_hash.update(text.encode(encoding='utf-8'))
            options.extend(re.findall(r'^(-[^rc].*)$', text, re.MULTILINE))
            done.update({
                requirements.parent / file: False
                for file in re.findall(r'^-[rc] (.+)$', text, re.MULTILINE)
                if requirements.parent / file not in done
            })
            done[requirements] = True

        # Set public properties
        self.current_hash = current_hash.hexdigest()
        self.options = options
        self.outdated = lockfile.exists() and self.current_hash != stored_hash

    @staticmethod
    def _get_stored_hash(lockfile: Path) -> str:
        if not (search := re.search(r'#[\s]*Requirements hash: (.+)', lockfile.read_text())):
            raise RuntimeError(f'Invalid lockfile "{lockfile}"')
        return search.group(1)


class Requirements:
    def __init__(  # pylint: disable=too-many-arguments
        self,
        path: Optional[Path] = None,
        default_paths: Optional[Sequence[Path]] = None,
        bare: bool = False,
        required: bool = True,
        allow_outdated: bool = False,
    ):
        """
        Represent a requirements file.

        Args:
            default_paths: The default paths to the requirements file.
            path: The path to the requirements file.
            bare: Whether to use the bare requirements file.
            required: Whether the requirements file must be provided.
            allow_outdated: Whether to allow an outdated requirements file.

        Attributes:
            changed: Whether the requirements lockfile is up-to-date.

        """
        self.path = path or self._default_path(default_paths or [])
        self.lockfile: Optional[Path] = None
        self.outdated = False
        self.changed = False
        self._processed: Optional[ProcessedRequirements] = None
        self._effective_path: Optional[Path] = None

        if self.path:
            if not self.path.exists():
                raise ValueError(f'Requirements file "{self.path}" not found')
            if not self.path.is_file():
                raise ValueError(f'Invalid requirements file "{self.path}"')

            self.lockfile = self.path.with_name(self.path.name + '.lock')

            if not bare:
                self._processed = ProcessedRequirements(self.path, self.lockfile)
                self.outdated = self._processed.outdated
                self.changed = not self.lockfile.exists() or self.outdated

            if not allow_outdated and self.outdated:
                raise RuntimeError(self.status)

            self._effective_path = self.path if bare or self.changed else self.lockfile
        elif required:
            raise RuntimeError('The requirements file must be specified')

    @property
    def status(self) -> str:
        if self.lockfile and self.lockfile.exists():
            status_text = 'outdated' if self.outdated else 'up-to-date'
            return f'Requirements lockfile of "{self.path}" is {status_text}'
        return f'Requirements file "{self.path}" does not have a lockfile'

    def __bool__(self) -> bool:
        return self._effective_path is not None

    def __str__(self) -> str:
        return str(self._effective_path)

    def update_lockfile(self, requirements: str) -> None:
        if not self.lockfile or not self._processed:
            raise RuntimeError('Cannot update the lockfile of an empty or bare orb')
        header = render('lockfile_header', {'hash': self._processed.current_hash})
        self.lockfile.write_text(header + '\n'.join(self._processed.options + [requirements]))
        print(f'Frozen requirements are written to "{self.lockfile}"')

    @staticmethod
    def _default_path(default_paths: Sequence[Path]) -> Optional[Path]:
        for path in default_paths:
            if path.exists():
                return path
        return None
