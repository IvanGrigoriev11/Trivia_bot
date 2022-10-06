import string
from typing import Optional


def parse_answer(s: str) -> Optional[int]:
    try:
        for char in string.ascii_letters:
            if char == s.lower():
                return ord(char) - ord("a") + 1
        return int(s)
    except ValueError:
        return None


def transform_keywords(key: str) -> str:
    """Appends "_" to keys which are Python-reserved keywords. E.g. `from` -> `from_`."""

    return key if key != "from" else "from_"
