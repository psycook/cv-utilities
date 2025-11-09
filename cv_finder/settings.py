import os
from functools import lru_cache

from dotenv import load_dotenv

load_dotenv()


@lru_cache(maxsize=1)
def _allowed_api_keys() -> set[str]:
    raw = os.getenv("CV_FINDER_API_KEYS", "")
    return {item.strip() for item in raw.split(",") if item.strip()}


def is_valid_api_key(candidate: str | None) -> bool:
    if not candidate:
        return False
    return candidate in _allowed_api_keys()
