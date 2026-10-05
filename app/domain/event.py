from dataclasses import dataclass


@dataclass(frozen=True)
class Event:
    """Something that happened in the game. 'source' says where it came from (e.g. coin A)."""

    kind: str
    source: str = ""
