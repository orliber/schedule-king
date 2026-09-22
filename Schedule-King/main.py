import argparse
import ctypes
import os
import sys

from src.qt_bootstrap import ensure_qt_plugins_visible

ensure_qt_plugins_visible()

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QApplication

from src.controllers.MainConroller import MainController
from src.services.schedule_api import ScheduleAPI
from src.styles.theme import apply_theme


def parse_args():
    parser = argparse.ArgumentParser(description="Schedule King - build conflict-free study schedules")
    parser.add_argument("--sample", action="store_true", help="start with the bundled sample course catalog loaded")
    parser.add_argument("--windowed", action="store_true", help="start in a normal window instead of maximized")
    return parser.parse_known_args()[0]


def main():
    args = parse_args()
    basedir = os.path.dirname(os.path.realpath(__file__))

    # Windows taskbar icon grouping
    if os.name == "nt":
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID("com.biu.scheduleking")

    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps, True)
    app = QApplication(sys.argv)
    app.setApplicationName("Schedule King")

    icon_file = "favicon.ico" if sys.platform == "win32" else "icon.png"
    icon_path = os.path.join(basedir, "src", "assets", icon_file)
    if os.path.exists(icon_path):
        app.setWindowIcon(QIcon(icon_path))

    apply_theme(app)

    api = ScheduleAPI()
    controller = MainController(api, maximize_on_start=not args.windowed, fullscreen_on_start=False)
    controller.start_application()
    if args.windowed:
        controller.course_window.resize(1440, 900)
    if args.sample:
        controller.course_window.load_sample_courses()

    sys.exit(app.exec_())


if __name__ == "__main__":
    main()
