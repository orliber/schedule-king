---
name: run-schedule-king
description: Launch, drive, test and screenshot the Schedule King PyQt5 desktop app (setup, headless rendering, macOS/iCloud Qt plugin pitfall).
---

# Running Schedule King

Schedule King is a PyQt5 desktop app. The app code lives in `Schedule-King/`, and `run.sh` sits at the repo root.

## Launch

```bash
./run.sh                 # creates Schedule-King/.venv on first run, installs requirements, launches
./run.sh --sample        # launch with sample_data/sample_courses.txt preloaded
./run.sh --windowed      # normal-size window instead of maximized
```

Run it in the background (`run_in_background: true`) and confirm it's alive with `pgrep -fl 'main.py'`.
To see the real window, use `screencapture -x <file>` and read the PNG. The window may sit behind the editor.

## Test (always headless)

```bash
./run.sh test            # = cd Schedule-King && QT_QPA_PLATFORM=offscreen .venv/bin/python -m pytest -q
```

`tests/conftest.py` defaults `QT_QPA_PLATFORM=offscreen`, so the tests never open windows.
Don't run Qt code on the cocoa platform from scripts. If Qt aborts, macOS shows a "Python quit unexpectedly" dialog to the user.

## Drive and screenshot headlessly

```bash
./run.sh screenshots     # tools/take_screenshots.py -> docs/screenshots/*.png
```

The script shows the pattern for driving the UI:
`MainController(ScheduleAPI(), maximize_on_start=False)` → `course_window.load_sample_courses()` →
`courseSelector.select_courses_by_code([...])` → `course_window.navigateToSchedulesWindow()` → pump `app.processEvents()` until `schedule_window.schedules > 0` → `widget.grab().save(path)`.

- Schedule generation uses `multiprocessing` (spawn), so driver code must be a real `.py` file with an `if __name__ == "__main__":` guard. Stdin scripts fail.
- Import `src.controllers.MainConroller` (it pulls in QtWebEngine) **before** creating `QApplication`, or set `Qt.AA_ShareOpenGLContexts` first.
- End driver scripts with `os._exit(0)` so worker processes don't slow the teardown.

## Known pitfall: "Could not find the Qt platform plugin"

The repo is under `~/Documents`, which iCloud syncs. iCloud keeps setting the BSD `hidden` flag on files inside `.venv`, and Qt skips hidden plugin files, then aborts.
`src/qt_bootstrap.ensure_qt_plugins_visible()` clears the flag on Qt's plugin folder. `main.py`, `tests/conftest.py` and `tools/take_screenshots.py` call it, and `run.sh` also runs `chflags -R nohidden` on the venv.
If a new entry point creates a `QApplication`, call it there too. Diagnose with `ls -lO <venv>/lib/python*/site-packages/PyQt5/Qt5/plugins/platforms`.
