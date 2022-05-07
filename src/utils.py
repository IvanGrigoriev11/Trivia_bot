from typing import Optional


def parse_int(s: str) -> Optional[int]:
    try:
        return int(s)
    except ValueError:
        return None


def transform_keywords(key: str) -> str:
    """to avoid using the specific "from" function when we need an attribute "from_"
    to get data updates from Telegram keyboard"""

    return key if key != "from" else "from_"
