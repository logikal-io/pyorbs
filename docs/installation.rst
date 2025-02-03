Installation
============
Requirements:

* `python <https://www.python.org/>`_ 3.12+ and `pip <https://pip.pypa.io/en/stable/>`_ 24.0+
* `bash <https://www.gnu.org/software/bash/>`_ 5.2+ or `fish <https://fishshell.com/>`_ 3.7+

Installing pyorbs is rather simple::

    $ pipx install pyorbs

As pyorbs does not have any third-party dependencies, you can also safely install it system-wide::

    $ pip install pyorbs --break-system-packages

.. note:: In a sane world Debian/Ubuntu would ship with a complete and functioning Python standard
    library. For some reason this does not seem to be the case, therefore you may need to make sure
    :mod:`venv` is installed using ``sudo apt install python3-venv`` before you can use pyorbs.
