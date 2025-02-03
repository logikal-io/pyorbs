from pathlib import Path


def render(name: str, context: dict[str, str] | None = None) -> str:
    text = (Path(__file__).parent / 'templates' / name).read_text()
    return text.format(**(context)) if context else text
