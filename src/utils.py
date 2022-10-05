from typing import Optional

import string


def parse_int(s: str) -> Optional[int]:
    try:
        for char in string.ascii_letters:
            if char == s:
                return ord(char) - ord('a') + 1
        else:
            return int(s)
    except ValueError:
        return None


def transform_keywords(key: str) -> str:
    """Appends "_" to keys which are Python-reserved keywords. E.g. `from` -> `from_`."""

    return key if key != "from" else "from_"
