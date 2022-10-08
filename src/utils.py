import string
from typing import Optional


def parse_answer(s: str) -> Optional[int]:
    """A helper function for handling user's answer on question.
    When given more than one letter or the letter is out of range of acceptable answers,
    the function returns None. If uppercase is given, the function returns lowercase."""

    if len(s) != 1:
        return None

    try:
        return string.ascii_lowercase.index(s.lower())
    except ValueError:
        return None


def transform_keywords(key: str) -> str:
    """Appends "_" to keys which are Python-reserved keywords. E.g. `from` -> `from_`."""

    return key if key != "from" else "from_"
