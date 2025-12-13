import sys
from pathlib import Path

# Ensure repository root (two levels up from this file) is on sys.path
# so that imports like `from be import ...` work even when pytest
# sets the test root to `be/`.
ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
