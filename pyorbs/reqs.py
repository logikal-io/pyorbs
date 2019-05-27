import re
import hashlib
from os.path import exists, isfile, dirname, join
from pathlib import Path
from collections import OrderedDict

from pyorbs.templates import render


class Requirements:
    """
    Dynamic requirements file representation.

    Attributes:
        path: The path to the requirements file.
        locked: The path to the requirements lockfile.
        changed: Whether the requirements lockfile is up-to-date.

    """
    def __init__(self, path, bare=False):
        """
        Args:
            path (str): The path to the requirements file.
            bare (bool): Whether to use the bare requirements file.

        """
        if not exists(path) or not isfile(path):
            raise ValueError('Invalid requirements file \'%s\'' % path)
        self.path = path
        self.locked = path + '.lock'
        self._bare = bare
        self._hash = self._get_hash() if not bare else None
        self.changed = not bare and self._hash != self._get_stored_hash()

    def __str__(self):
        """
        Returns the path to the relevant requirements file.
        """
        return self.path if self._bare or self.changed else self.locked

    def lock(self, frozen):
        """
        Updates the lockfile using the provided frozen requirements.
        """
        header = render('lockfile_header', {'reqs': self.path, 'hash': self._hash})
        Path(self.locked).write_text(header + frozen)
        print('Frozen requirements are written to \'%s\'' % self.locked)

    def _get_hash(self):
        """
        Returns the SHA-256 hash of the concatenated requirements files.
        """
        result = hashlib.sha256()
        done = OrderedDict([(self.path, False)])
        while not all(done.values()):
            reqs = [r for r, p in done.items() if not p][0]
            if not exists(reqs):
                raise RuntimeError('Requirements file \'%s\' not found (required by \'%s\')' %
                                   (reqs, self.path))
            text = Path(reqs).read_text()
            result.update(text.encode())
            done.update([(join(dirname(reqs), r), False) for r in re.findall(r'-r (.*)', text)
                         if join(dirname(reqs), r) not in done])
            done[reqs] = True
        return result.hexdigest()

    def _get_stored_hash(self):
        """
        Returns the stored hash from the lockfile or None if no lockfile or hash is found.
        """
        if not exists(self.locked):
            return None
        hash_search = re.search(r'hash: (.*)', Path(self.locked).read_text())
        return hash_search.group(1) if hash_search else None
