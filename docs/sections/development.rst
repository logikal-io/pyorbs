Development
===========
We welcome any contribution to our open source projects. If you want to participate in our work,
make sure to read our `software development principles <https://github.com/logikal-jp/principles>`_
before you start.

Issue Reporting
---------------
In case you encounter an issue feel free to let us know about it on `GitHub
<https://github.com/logikal-jp/pyorbs/issues>`_.

Development Environment
-----------------------
You can manage the development environment of pyorbs with pyorbs itself. If you already have pyorbs
installed you can simply execute ``orb -m pyorbs`` within the project folder, after which you can
execute ``orb pyorbs`` and ``pip install -e .`` to install the ``orb`` command inside the
``pyorbs`` orb. This allows you to develop and test the ``orb`` command itself while the ``pyorbs``
orb is active.

Testing
-------
Make sure to test pyorbs on all supported shells that are listed in the :ref:`index:Features`
section of the documentation (for this you will need to install all of these shells on your
system).

Creating Releases
-----------------
You can make a new release as follows:

#. Make sure the changelog is properly updated.
#. Create a pull request and ask for review.
#. Once the pull request has been approved, increase the version number using ``bump2version``.
#. Merge the pull request.
#. Create a new distribution and upload it to `test.pypi.org <https://test.pypi.org>`_::

    $ make dist
    $ twine upload --repository-url https://test.pypi.org/legacy/ dist/*

#. Check if your distribution works properly::

    $ pip3 install --user --upgrade --index-url https://test.pypi.org/simple/ pyorbs
    $ orb -v

#. Finally, upload the new distribution to PyPI::

    $ twine upload dist/*

Maintenance
-----------
This package is maintained by `Logikal <https://logikal.jp>`_.
