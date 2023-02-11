Usage
=====
Everything in pyorbs can be controlled using a single ``orb`` command. You can always access a
short usage help by executing ``orb --help`` or ``orb -h``.

Making Orbs
---------------------------------
Making a new orb is fairly simple::

    $ orb -m magic

This will create a new virtual environment called ``magic`` using :mod:`venv` in your orb storage
folder (``$XDG_DATA_HOME/pyorbs`` by default), upgrade pip, prepare pyorb's shell initialization
files, install the necessary packages using ``pip install --upgrade`` and generate a requirements
lockfile if one does not exist yet (based on ``requirements.txt`` or ``requirements/dev.txt`` by
default).

.. note:: Package installation is done based on the requirements lockfile if one exists, otherwise
    the requirements file is used directly. While we recommend relying on lockfiles in order to
    have deterministic deployments you can disable this feature using the ``--bare`` command-line
    option.

.. tip:: The orb storage folder can be specified for any orb action using the ``--path`` option.

Specifying a different orb storage folder, requirements file and Python executable can be done as::

    $ orb -m magic --path ~/.virtualenvs -r requirements/airflow.txt -e python3.11


Listing & Destroying Orbs
-------------------------
Orbs can be listed like so::

    $ orb -l

Destroying an orb is quite straightforward too::

    $ orb -d magic

Activating & Deactivating Orbs
------------------------------
Orb activation is not very difficult::

    $ orb magic

This will spawn a new sub-shell, initialize it and enter the virtual environment and the project
directory (which is the folder in which the orb was originally created). In case you do not want to
change your working directory you can use the ``--no-cd`` option.

In order to deactivate an orb simply exit the shell by typing ``exit`` or hit ``Ctrl + d``.

You can also run a command in a given environment without the interactive shell::

    $ orb magic -c ./magical-app

Please keep in mind that the working directory is also changed in this case before running the
command, but again, you can use the ``--no-cd`` option to override this behavior.

Managing Requirements
---------------------
The recommended way to manage the requirements of your application is through `pip requirements
files <https://pip.pypa.io/en/stable/user_guide/#requirements-files>`_.

In order to support deterministic deployments lockfiles are used. When an existing orb's
requirements change you can update its package environment and the appropriate requirements
lockfile as follows::

    $ orb -u magic

This will re-create the ``magic`` orb (using ``requirements.txt`` or ``requirements/dev.txt`` by
default) and trigger a re-generation of the requirements lockfile if the requirements changed. This
includes changes to files that are further specified within the appropriate requirements files
using the ``-r`` or ``-c`` options.

.. tip:: You do not need to specify the orb name when you are already inside one – pyorbs will
    default to using the current orb for all actions when no orb is specified explicitly.

.. note:: Whether a lockfile is outdated is assessed using a hash of the concatenated requirements
    and constraints files which is stored in the header of each lockfile.

In case you only want to generate or re-generate lockfiles you can use the ``orb --freeze`` or
``orb -f`` command. You can also specify the Python executable with this command when necessary
using the ``--executable`` or ``-e`` option. Finally, you can use the ``orb --test`` or ``orb -t``
command for checking whether your lockfiles are up-to-date.

.. tip:: You can freeze or test multiple requirements files in one run by specifying a folder
    instead of a single file with the ``--requirements`` or ``-r`` option. This can be useful when
    you need to manage multiple requirements files for different environments for example. Note
    that files which do not have lockfiles already will not be frozen or tested in this case.

Glowing Orb
-----------
The name of the orb which was last activated is saved in a file called ``glowing`` in the orb
storage folder. This then becomes the default orb name for all subsequent commands which are
executed outside an orb until another orb is activated or until the user toggles orb glow using the
``--glow`` or ``-g`` command-line option. This makes it very simple to activate the last used orb
for example by just executing ``orb`` without any arguments.

.. tip:: The glowing orb is marked with a star in the orb list output.

This mechanism can be leveraged in terminal multiplexers to automatically enter the active orb in
new windows or panes. For example, in the case of `tmux <https://github.com/tmux/tmux/wiki>`_ one
could add the line

.. code-block:: none

    bind -n C-t new-window -c '#{pane_current_path}' 'orb --shell'

to the tmux configuration file to make ``Ctrl + t`` open a new window at the current pane path
with the currently glowing orb activated. The ``--shell`` option ensures that a top-level
interactive shell (and thus a window) is always created, even when there is no orb to activate.

Command Completion
------------------
You can install bash command completion by executing the following command::

    $ orb --bash | sudo tee "$(pkg-config --variable=completionsdir bash-completion)/orb"
