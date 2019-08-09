Development
===========
We welcome any contribution to our open source projects. If you want to participate in our work,
make sure to read our `software development principles <https://github.com/wbrp/principles>`_
before you start.

Issue Reporting
---------------
In case you encounter an issue feel free to let us know about it on `GitHub
<https://github.com/wbrp/pyorbs/issues>`_.

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

Continuous Deployment
---------------------
You generally do not have to worry about this too much, as the continuous deployment system is
maintained by `Webrepublic <https://webrepublic.com/en/>`_'s Data & Technology department. We use
`Concourse <https://concourse-ci.org>`_ for orchestrating the various tasks necessary for
publishing this package, including building and updating the documentation upon successful merging
into the ``master`` branch.

In case hell breaks loose and you must publish pyorbs manually, do this::

    $ ./setup.py sdist bdist_wheel
    $ twine check dist/*
    $ twine upload --repository-url https://test.pypi.org/legacy/ dist/*
    $ twine upload dist/*

Do not forget to `check your distribution <https://packaging.python.org/guides/using-testpypi/>`_
on `test.pypi.org <https://test.pypi.org>`_ before uploading it to PyPI.

Maintenance
-----------
This package is currently maintained by the `Webrepublic <https://webrepublic.com/en/>`_ Data &
Technology department.
