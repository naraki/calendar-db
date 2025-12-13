"""Compatibility shim for `be.db`.

The real implementation lives in `be/src/db.py`; tests and other modules
import `be.db`, so re-export the implementation here.
"""
#from be.src import db as _db
import db as _db

# Re-export names from the implementation module
__all__ = [name for name in dir(_db) if not name.startswith("_")]
for _name in __all__:
    globals()[_name] = getattr(_db, _name)
