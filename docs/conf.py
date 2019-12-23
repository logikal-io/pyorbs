import os
import sys

sys.path.insert(0, os.path.abspath('..'))

from pyorbs import app

# Project information
project = app.__project__
copyright = app.__author__
author = app.__author__
version = app.__version__
release = app.__version__

# General configuration
extensions = ['sphinx.ext.intersphinx', 'sphinx.ext.autosectionlabel']
exclude_patterns = ['_build']
highlight_language = 'console'

# Options for HTML output
html_theme = 'sphinx_rtd_theme'
html_theme_options = {'canonical_url': '%s/docs/%s/' % (app.__urls__['docs'], app.__version__)}
html_static_path = ['_static']
html_favicon = '_static/favicon.png'
html_show_sourcelink = False

# Extensions
autosectionlabel_prefix_document = True
intersphinx_timeout = 30
intersphinx_mapping = {'python': ('https://docs.python.org/3.5', 'inventory/python-3.5.inv')}
