.. toctree::
    :hidden:

    self
    installation
    usage
    development
    license

Getting Started
===============
Python virtual environment management can be a little bit inconvenient sometimes. This magical tool
aims at making this process simpler.

Using pyorbs is easy. You install it::

    $ pip install pyorbs

then create a new orb in your project folder::

    $ orb -m magic
    Making orb "magic" using "requirements.txt"...

and whoosh, ready to go::

    $ orb magic -c ./magical-app
    Activating orb "magic"...
    Running "./magical-app"...

or, alternatively::

    $ orb magic
    Activating orb "magic"...
    Orb "magic" is glowing now
    (magic) $ ./magical-app

Features
--------
There are a few good things about pyorbs:

- Easy to install
- Provides a single and short ``orb`` command
- Streamlines local development, deployment and remote execution / troubleshooting
- Supports deterministic deployments through lockfiles
- Straightforward behavior using only `pip <https://pip.pypa.io/en/stable/>`_ and the now-standard
  :mod:`venv` under the hood
- Has no dependencies beyond pip and the Python standard library
- Supports `bash <https://www.gnu.org/software/bash/>`_ and `fish <https://fishshell.com/>`_
  shells and works reasonably well with `tmux <https://github.com/tmux/tmux/wiki>`_

Limitations
-----------
There are also a few bad things about pyorbs:

- Does not work with zsh, csh or tcsh shells
- May not work on Windows

Okay, but why?
--------------
Why on earth did we need `yet another tool <https://xkcd.com/927/>`_? Couldn't we just use
`virtualenvwrapper <https://virtualenvwrapper.readthedocs.io/en/latest/>`_, `Pipenv
<https://docs.pipenv.org/en/latest/>`_, `Poetry <https://python-poetry.org/>`_ or a `decent Python
IDE <https://www.jetbrains.com/pycharm/>`_ for all of this?

It seems that all of these tools have certain limitations that make things inconvenient at times.
To utilize all of virtualenvwrapper's features one has to edit a shell startup file and then
remember to source it when running an app via systemd, cron, `Airflow
<https://airflow.apache.org/>`_ or something similar. Pipenv does not provide a convenient way of
deploying an application to `more than two environments
<https://github.com/pypa/pipenv/issues/1071>`_ and has some `other limitations
<https://chriswarrick.com/blog/2018/07/17/pipenv-promises-a-lot-delivers-very-little/>`_ as well.
Poetry uses a series of non-standard approaches (for example, an arbitrary lockfile format). An IDE
can be clumsy too when one would like to run or troubleshoot an app in a distributed system.

Generally, pyorbs is somewhere between virtualenvwrapper and Pipenv, trying to support a similar
development workflow as virtualenvwrapper while also providing some useful features for
deterministic deployments in heterogeneous systems.
