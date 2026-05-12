# 경량 TTL 메모리 캐시. pykrx 호출 부하/지연을 줄이기 위해 사용.

import time
import threading
from typing import Any, Callable, Optional

_lock = threading.Lock()
_store: dict[str, tuple[float, Any]] = {}


def get(key: str) -> Optional[Any]:
    with _lock:
        v = _store.get(key)
        if not v:
            return None
        expires, data = v
        if time.time() > expires:
            _store.pop(key, None)
            return None
        return data


def put(key: str, value: Any, ttl_seconds: float):
    with _lock:
        _store[key] = (time.time() + ttl_seconds, value)


def memoize(key: str, ttl_seconds: float, factory: Callable[[], Any]) -> Any:
    cached = get(key)
    if cached is not None:
        return cached
    val = factory()
    if val is not None:
        put(key, val, ttl_seconds)
    return val


def clear():
    with _lock:
        _store.clear()
