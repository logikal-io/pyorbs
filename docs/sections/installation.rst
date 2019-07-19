Installation
============
Requirements:

* `python <https://www.python.org/>`_ 3.5+ and `pip <https://pip.pypa.io/en/stable/>`_ 8.1+
* `bash <https://www.gnu.org/software/bash/>`_ 4.3+ or `fish <https://fishshell.com/>`_ 3.0+

Installing pyorbs is rather simple::

    $ pip3 install pyorbs

.. note:: In a sane world Debian/Ubuntu would ship with a complete and functioning Python standard
    library. For some reason this does not seem to be the case, therefore you may need to make sure
    :mod:`venv` is installed using ``apt-get install python3-venv`` before you can use pyorbs.

.. tip:: We also maintain a public `Docker Hub container repository
    <https://hub.docker.com/r/wbrp/pyorbs>`_ of base images that already include a working pyorbs
    installation.
