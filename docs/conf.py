# pylint: disable=invalid-name
import sys

highlight_language = 'console'
html_static_path = ['static']
html_favicon = 'static/favicon.png'

extensions = ['sphinx.ext.autosectionlabel', 'sphinx.ext.intersphinx']
intersphinx_mapping = {
    'python': (f'https://docs.python.org/{sys.version_info[0]}.{sys.version_info[1]}', None),
}
