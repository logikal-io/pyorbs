from pathlib import Path
from os.path import join, dirname, abspath


def render(name, context):
    return Path(join(dirname(abspath(__file__)), 'templates/%s' % name)).read_text() % context
