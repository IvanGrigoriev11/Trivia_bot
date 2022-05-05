from typing import Optional


def parse_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except ValueError:
        return None


def transform_keywords(key: str) -> str:
    return key if key != "from" else "from_"
