from fastapi.templating import Jinja2Templates

# Safe cache that tolerates unhashable keys by stringifying them
class SafeCache(dict):
    def __getitem__(self, key):
        try:
            return super().__getitem__(key)
        except TypeError:
            return super().__getitem__(repr(key))

    def __setitem__(self, key, value):
        try:
            super().__setitem__(key, value)
        except TypeError:
            super().__setitem__(repr(key), value)

    def get(self, key, default=None):
        try:
            return super().get(key, default)
        except TypeError:
            return super().get(repr(key), default)

templates = Jinja2Templates(directory='templates')
# Replace jinja cache with safe cache
try:
    templates.env.cache = SafeCache()
    templates.env.cache_size = 0
except Exception:
    pass
