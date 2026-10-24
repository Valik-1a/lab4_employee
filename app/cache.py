from time import monotonic
from typing import Any

_cache: dict[str, tuple[float, Any]] = {}
TTL_SECONDS = 10


def get_cached(key: str) -> Any | None:
    item = _cache.get(key)
    if item is None:
        return None
    expires, value = item
    if monotonic() >= expires:
        _cache.pop(key, None)
        return None
    return value


def set_cached(key: str, value: Any) -> None:
    _cache[key] = (monotonic() + TTL_SECONDS, value)


def clear_cache() -> None:
    _cache.clear()
