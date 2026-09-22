"""
Render the main Schedule King screens headlessly and save them as PNGs.

Usage:  python tools/take_screenshots.py [output_dir]
Default output: ../docs/screenshots (repository root)
"""
import os
import sys
import time

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, ROOT)
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from src.qt_bootstrap import ensure_qt_plugins_visible  # noqa: E402

ensure_qt_plugins_visible()

from src.controllers.MainConroller import MainController  # noqa: E402
from src.services.schedule_api import ScheduleAPI  # noqa: E402
from PyQt5.QtCore import Qt  # noqa: E402
from PyQt5.QtWidgets import QApplication  # noqa: E402

SIZE = (1440, 900)


def pump(app, seconds=0.0):
    end = time.time() + seconds
    app.processEvents()
    while time.time() < end:
        app.processEvents()
        time.sleep(0.03)


def save(widget, out_dir, name, app):
    pump(app, 0.2)
    path = os.path.join(out_dir, name)
    widget.grab().save(path)
    print(f"saved {os.path.relpath(path, os.getcwd())}")


def main():
    out_dir = os.path.abspath(sys.argv[1] if len(sys.argv) > 1 else os.path.join(ROOT, "..", "docs", "screenshots"))
    os.makedirs(out_dir, exist_ok=True)

    QApplication.setAttribute(Qt.AA_ShareOpenGLContexts, True)
    app = QApplication(sys.argv)
    from src.styles.theme import apply_theme
    apply_theme(app)

    controller = MainController(ScheduleAPI(), maximize_on_start=False)
    window = controller.course_window
    window.resize(*SIZE)
    window.show()
    save(window, out_dir, "01-welcome.png", app)

    from src.views.course_window import LoadCoursesDialog
    dialog = LoadCoursesDialog(window)
    dialog.show()
    save(dialog, out_dir, "02-load-dialog.png", app)
    dialog.close()

    window.load_sample_courses()
    codes = [c.course_code for c in window.courseSelector.get_all_courses()[:5]]
    window.courseSelector.select_courses_by_code(codes)
    save(window, out_dir, "03-course-selection.png", app)

    from src.components.constraint_dialog import ConstraintDialog
    constraints = ConstraintDialog(window, {(0, 0), (1, 0), (0, 5), (1, 5)}, {(2, 1), (3, 1), (2, 2), (3, 2)})
    constraints.show()
    save(constraints, out_dir, "04-time-preferences.png", app)
    constraints.close()

    window.navigateToSchedulesWindow()
    deadline = time.time() + 20
    while time.time() < deadline:
        pump(app, 0.2)
        sw = controller.schedule_window
        if sw is not None and sw.schedules and sw.schedules > 0 and not controller.schedule_controller.generation_active:
            break
    sw = controller.schedule_window
    sw.setWindowState(Qt.WindowNoState)
    sw.resize(*SIZE)
    save(sw, out_dir, "05-schedules.png", app)

    sw.ranking_controls.metric_selector.setCurrentIndex(1)
    pump(app, 0.5)
    save(sw, out_dir, "06-ranked.png", app)

    controller.schedule_controller.stop_schedules_generation()
    pump(app, 0.3)
    os._exit(0)  # skip slow teardown of worker processes / web engine


if __name__ == "__main__":
    main()
