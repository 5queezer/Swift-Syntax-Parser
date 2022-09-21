from typing import NamedTuple


class Token(NamedTuple):
    type: str or None
    value: str