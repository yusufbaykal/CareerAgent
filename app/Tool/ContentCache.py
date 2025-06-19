from typing import Any, Dict, Optional
import time

class ContentCache:
    def __init__(self, ttl: int = 3600):
        self.cache: Dict[str, Dict[str, Any]] = {}
        self.ttl = ttl

    def set(self, key: str, data: Any) -> None:
        self.cache[key] = {'data': data, 'timestamp': time.time()}

    def get(self, key: str) -> Optional[Any]:
        item = self.cache.get(key)
        if not item:
            return None
        if time.time() - item['timestamp'] > self.ttl:
            del self.cache[key]
            return None
        return item['data']


cache = ContentCache()