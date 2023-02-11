from pathlib import Path
from typing import Mapping, Optional


def render(name: str, context: Optional[Mapping[str, str]] = None) -> str:
    text = (Path(__file__).parent / 'templates' / name).read_text()
    return text.format(**(context)) if context else text
