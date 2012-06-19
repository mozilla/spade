from .base import *

try:
    from .local import *
except ImportError:
    pass

CACHES["default"]["VERSION"] = 1
