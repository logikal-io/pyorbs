Changelog
=========

We document changes in line with the `"keep a changelog" principles
<https://keepachangelog.com/en/1.1.0/>`_.

You can find the release dates on `GitHub <https://github.com/logikal-code/pyorbs/releases>`__.

1.6.0
-----
- *Added:* Default shell.

1.5.0
-----
- *Added:* Quiet mode for testing lockfiles.

1.4.2
-----
- *Fixed:* The ``pkg_resources`` package is also excluded from lockfiles.

1.4.1
-----
- *Changed:* Removed editable packages from lockfiles.

1.4.0
-----
- *Added:* The ``-i`` and ``--info`` options for listing outdated packages.
- *Changed:* Orbs are sorted by their name in the orb list.
- *Changed:* Removed Python 3.5 support.

1.3.1
-----
- *Changed:* Migrated the GitHub repository.

1.3.0
-----
- *Added:* Bash command completion.

1.2.0
-----
- *Added:* Option for testing whether requirements files are up-to-date.

1.1.0
-----
- *Added:* Support for constraints files and additional options in requirements files.

1.0.3
-----
- *Added:* Dockerfiles of our public Docker Hub images.
- *Changed:* Moved the software development principles documentation to a separate repository.

1.0.2
-----
- *Changed:* Files with a name starting with a dot are skipped when freezing a folder.

1.0.1
-----
- *Added:* Information about the public Docker Hub images.
- *Changed:* Replaced ``pip`` with ``pip3`` in the installation documentation.

1.0.0
-----
- Launched pyorbs.
