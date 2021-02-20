#!/usr/bin/env python3
import pathlib

import setuptools

from pyorbs import app

setuptools.setup(
    name=app.__project__,
    version=app.__version__,
    author=app.__author__,
    maintainer=app.__maintainer__,
    keywords=app.__keywords__,
    description=app.__doc__.strip(),
    long_description=pathlib.Path('README.rst').read_text(),
    long_description_content_type='text/x-rst',
    url=app.__urls__['docs'],
    project_urls={
        'Documentation': app.__urls__['docs'],
        'Issue tracker': app.__urls__['issues'],
        'Release notes': app.__urls__['releases'],
        'Source code': app.__urls__['source'],
    },
    python_requires='>=3.6',
    install_requires=[],
    packages=setuptools.find_packages(exclude=['docs*', 'tests*']),
    package_data={'pyorbs': ['templates/*']},
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Console',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Topic :: Software Development',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
    ],
    entry_points={'console_scripts': ['orb=pyorbs.app:main']},
)
