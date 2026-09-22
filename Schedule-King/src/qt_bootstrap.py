"""
Startup helpers that must run before the first QApplication is created.
"""
import os
import stat
import sys


def ensure_qt_plugins_visible():
    """
    On macOS, folders synced by iCloud (e.g. ~/Documents) can get the BSD
    "hidden" flag applied to files inside a virtualenv. Qt skips hidden files
    when scanning for plugins, so it fails to find its platform plugin and
    aborts on startup. Clearing the flag on Qt's plugin files avoids that.
    """
    if sys.platform != "darwin" or not hasattr(os, "chflags"):
        return
    try:
        import PyQt5
    except ImportError:
        return
    plugins_dir = os.path.join(os.path.dirname(PyQt5.__file__), "Qt5", "plugins")
    for root, dirs, files in os.walk(plugins_dir):
        for name in dirs + files:
            path = os.path.join(root, name)
            try:
                flags = os.lstat(path).st_flags
                if flags & stat.UF_HIDDEN:
                    os.chflags(path, flags & ~stat.UF_HIDDEN, follow_symlinks=False)
            except OSError:
                pass
