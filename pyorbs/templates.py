from pathlib import Path


def render(name, context=None):
    return (Path(__file__).parent / 'templates' / name).read_text() % (context or {})
