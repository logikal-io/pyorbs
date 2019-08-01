Development
===========
In case you want to participate in the development of pyorbs, you're very welcome to do so! Here
you can learn about some principles that we try to follow in order to make sure we produce
software that doesn't suck. It is assumed that you have a solid understanding of software
development best practices and Python development in general.

Issue Reporting
---------------
In case you encounter an issue feel free to let us know about it on `GitHub
<https://github.com/wbrp/pyorbs/issues>`__.

General Principles
------------------
There are some software development concepts and ideas that are important when writing software
that other people will rely on. In particular, you should always keep in mind the following
principles:

* No code shall be shipped without being thoroughly `tested
  <https://en.wikipedia.org/wiki/Test-driven_development>`_ and `reviewed
  <https://en.wikipedia.org/wiki/Code_review>`_ first.

* Write code that `doesn't smell <https://en.wikipedia.org/wiki/Code_smell>`_.

* `Don't repeat yourself <https://en.wikipedia.org/wiki/Don%27t_repeat_yourself>`_. Just don't.

* Live the `Zen of Python <https://www.python.org/dev/peps/pep-0020/>`_.

Coding Style
------------
When writing code you should always follow the `PEP8 Style Guide
<https://www.python.org/dev/peps/pep-0008/>`_ with the following exceptions:

* Each line should be less than 100 characters long.
* You should use `Google-style docstrings <https://google.github.io/styleguide/pyguide.html>`_
  starting on the second line.

Development Environment
-----------------------
You can manage the development environment of pyorbs with pyorbs itself. If you already have pyorbs
installed you can simply execute ``orb -m pyorbs`` within the project folder, after which you can
execute ``orb pyorbs`` and ``pip install -e .`` to install the ``orb`` command inside the
``pyorbs`` orb. This allows you to develop and test the ``orb`` command itself while the ``pyorbs``
orb is active.

Version Control
---------------
We use `GitHub <https://github.com/wbrp/pyorbs>`__ for version control and for aiding the review
process. Before starting to work on a new feature, make sure that you are aligned with the
maintainers to avoid developing things that may not get merged. Always work in separate feature
branches and commit often. Once your changes are ready to be reviewed, create a pull request.

You should increment the version number according to the `semantic versioning rules
<https://semver.org/>`_ using `bump2version <https://github.com/c4urself/bump2version>`_. Make sure
to `document your changes <https://keepachangelog.com/en/>`_ in the
:ref:`sections/changelog:Changelog` as well.

Testing
-------
The codebase is tested using the `pytest <https://docs.pytest.org/en/latest/>`_ framework. All
tests should reside in the ``tests`` folder. The code must have complete test coverage through
meaningful unit and system tests. Make sure the tool is tested with all supported shells that are
listed in the :ref:`index:Features` section (for this you will need to install all of these shells
on your system).

You can run the test suite by simply executing ``pytest``.

Documentation
-------------
This documentation is created using `Sphinx <http://www.sphinx-doc.org/en/master/>`_ and can be
modified or expanded by changing the source files in the ``docs`` folder. In order to re-build the
documentation just execute ``make`` inside this folder while the ``pyorbs`` orb is
active.

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
