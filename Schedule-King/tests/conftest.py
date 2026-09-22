import os
import sys

# Run Qt tests headless by default so no windows (or crash dialogs) pop up.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from src.qt_bootstrap import ensure_qt_plugins_visible  # noqa: E402

ensure_qt_plugins_visible()
