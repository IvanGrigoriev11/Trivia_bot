from typing import Optional


def parse_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except ValueError:
        return None


def transform_keywords(key: str) -> str:
    """Appends "_" to keys which are Python-reserved keywords. E.g. `from` -> `from_`."""

    return key if key != "from" else "from_"
