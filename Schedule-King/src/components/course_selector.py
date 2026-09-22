from PyQt5.QtWidgets import (
    QVBoxLayout, QPushButton, QWidget, QHBoxLayout, QFrame,
    QLabel, QMessageBox, QProgressDialog, QSizePolicy, QStackedWidget
)
from PyQt5.QtCore import pyqtSignal, Qt, QSize
from PyQt5.QtGui import QPixmap

from typing import List
from src.models.course import Course
from src.components.course_list import CourseList
from src.components.selected_courses_panel import SelectedCoursesPanel
from src.components.search_bar import SearchBar
from src.styles.theme import PALETTE, asset_path, repolish
from src.styles.icons import icon
from src.styles.ui_styles import warning_label_style, success_label_style, footer_label_style


def _card() -> QFrame:
    card = QFrame()
    card.setObjectName("card")
    return card


class CourseSelector(QWidget):
    # Signals for communicating with parent widgets
    coursesSelected = pyqtSignal(list)
    coursesSubmitted = pyqtSignal(list)
    loadRequested = pyqtSignal()
    sampleRequested = pyqtSignal()
    browseRequested = pyqtSignal()  # "Load courses" in the empty state
    MAX_COURSES = 7  # Maximum number of courses allowed

    def __init__(self, parent=None):
        super().__init__(parent)
        self.layout = QVBoxLayout(self)
        self.layout.setContentsMargins(8, 4, 8, 4)
        self.layout.setSpacing(18)

        self._setup_header()
        self._setup_body()
        self._setup_footer()

        # Progress dialog for long-running work (ChoiceFreak loading, etc.)
        self.progress_bar = None
        self._update_submit_button_state([])
        self._update_empty_state()

    # ------------------------------------------------------------------ layout
    def _setup_header(self):
        """App header: logo, title/subtitle and a slot for global actions."""
        header = QHBoxLayout()
        header.setSpacing(14)

        logo = QLabel()
        pixmap = QPixmap(asset_path("logo.png"))
        if not pixmap.isNull():
            logo.setPixmap(pixmap.scaled(56, 56, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        header.addWidget(logo)

        titles = QVBoxLayout()
        titles.setSpacing(0)
        app_title = QLabel("Schedule King")
        app_title.setObjectName("app_title")
        subtitle = QLabel("Pick your courses and get every conflict-free timetable in seconds")
        subtitle.setObjectName("app_subtitle")
        titles.addStretch(1)
        titles.addWidget(app_title)
        titles.addWidget(subtitle)
        titles.addStretch(1)
        header.addLayout(titles)
        header.addStretch(1)

        # Filled by CourseWindow (Load / Add course / Guide)
        self.header_actions = QHBoxLayout()
        self.header_actions.setSpacing(10)
        header.addLayout(self.header_actions)

        # Kept for API compatibility; CourseWindow hides it in favour of its own load dialog
        self.load_button = QPushButton("Load Courses")
        self.load_button.setCursor(Qt.PointingHandCursor)
        self.load_button.clicked.connect(self._handle_load)
        self.header_actions.addWidget(self.load_button)

        self.layout.addLayout(header)

    def _setup_body(self):
        body = QHBoxLayout()
        body.setSpacing(18)
        self.split_layout = body
        body.addWidget(self._build_catalog_card(), 5)
        body.addWidget(self._build_selection_card(), 3)
        self.layout.addLayout(body, 1)

    def _build_catalog_card(self) -> QFrame:
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title_row = QHBoxLayout()
        self.title_label = QLabel("Available Courses")
        self.title_label.setObjectName("section_title")
        title_row.addWidget(self.title_label)
        title_row.addStretch(1)
        layout.addLayout(title_row)

        self.course_list = CourseList()
        self.course_list.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.course_list.selectionChanged.connect(self._handle_selection_changed)

        # Search + category filter on one row
        filter_row = QHBoxLayout()
        filter_row.setSpacing(10)
        self.search_bar = SearchBar()
        self.search_bar.searchTextChanged.connect(self._handle_search)
        filter_row.addWidget(self.search_bar, 3)
        self.course_list.category_filter.setMinimumHeight(40)
        filter_row.addWidget(self.course_list.category_filter, 1)
        layout.addLayout(filter_row)

        self.list_stack = QStackedWidget()
        self.list_stack.addWidget(self._build_empty_state())
        self.list_stack.addWidget(self.course_list)
        self.list_stack.setMinimumHeight(260)
        layout.addWidget(self.list_stack, 1)
        return card

    def _build_empty_state(self) -> QWidget:
        empty = QWidget()
        layout = QVBoxLayout(empty)
        layout.setAlignment(Qt.AlignCenter)
        layout.setSpacing(10)

        art = QLabel()
        pixmap = QPixmap(asset_path("logo.png"))
        if not pixmap.isNull():
            art.setPixmap(pixmap.scaled(110, 110, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        art.setAlignment(Qt.AlignCenter)
        layout.addWidget(art)

        headline = QLabel("No courses loaded yet")
        headline.setObjectName("section_title")
        headline.setAlignment(Qt.AlignCenter)
        layout.addWidget(headline)

        hint = QLabel("Load a course file (.txt / .xlsx), fetch a catalog from ChoiceFreak,\n"
                      "or explore the app with the built-in sample data.")
        hint.setObjectName("muted")
        hint.setAlignment(Qt.AlignCenter)
        layout.addWidget(hint)

        buttons = QHBoxLayout()
        buttons.setSpacing(10)
        buttons.addStretch(1)
        self.empty_load_button = QPushButton("Load courses")
        self.empty_load_button.setProperty("variant", "primary")
        self.empty_load_button.setCursor(Qt.PointingHandCursor)
        self.empty_load_button.clicked.connect(self.browseRequested.emit)
        self.sample_button = QPushButton("Try sample data")
        self.sample_button.setCursor(Qt.PointingHandCursor)
        self.sample_button.clicked.connect(self.sampleRequested.emit)
        buttons.addWidget(self.empty_load_button)
        buttons.addWidget(self.sample_button)
        buttons.addStretch(1)
        layout.addSpacing(6)
        layout.addLayout(buttons)
        return empty

    def _build_selection_card(self) -> QFrame:
        card = _card()
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 18, 20, 18)
        layout.setSpacing(12)

        title_row = QHBoxLayout()
        title = QLabel("Your Selection")
        title.setObjectName("section_title")
        title_row.addWidget(title)
        title_row.addStretch(1)
        self.count_badge = QLabel(f"0 / {self.MAX_COURSES}")
        self.count_badge.setObjectName("badge")
        title_row.addWidget(self.count_badge)
        layout.addLayout(title_row)

        self.limit_label = QLabel(f"Maximum {self.MAX_COURSES} courses allowed")
        layout.addWidget(self.limit_label)

        self.selected_panel = SelectedCoursesPanel()
        self.selected_panel.setMinimumSize(250, 160)
        self.selected_panel.removeRequested.connect(self.course_list.deselect_course)
        layout.addWidget(self.selected_panel, 1)

        # Secondary actions (CourseWindow adds the time-preferences button here)
        self.secondary_actions = QVBoxLayout()
        self.secondary_actions.setSpacing(8)
        layout.addLayout(self.secondary_actions)

        self.button_layout = QHBoxLayout()
        self.button_layout.setSpacing(10)

        self.clear_button = QPushButton("  Clear")
        self.clear_button.setProperty("variant", "danger")
        self.clear_button.setIcon(icon("trash", 18, PALETTE["danger"]))
        self.clear_button.setIconSize(QSize(18, 18))
        self.clear_button.setToolTip("Clear all selected courses")
        self.clear_button.setCursor(Qt.PointingHandCursor)
        self.clear_button.setMinimumHeight(46)

        self.submit_button = QPushButton("  Generate Schedules")
        self.submit_button.setProperty("variant", "primary")
        self.submit_button.setIcon(icon("sparkles", 20, "#FFFFFF"))
        self.submit_button.setIconSize(QSize(20, 20))
        self.submit_button.setToolTip("Generate every conflict-free schedule")
        self.submit_button.setCursor(Qt.PointingHandCursor)
        self.submit_button.setMinimumHeight(46)

        self.button_layout.addWidget(self.clear_button, 1)
        self.button_layout.addWidget(self.submit_button, 2)
        layout.addLayout(self.button_layout)

        self.clear_button.clicked.connect(self._handle_clear)
        self.submit_button.clicked.connect(self._handle_submit)
        return card

    def _setup_footer(self):
        footer = QLabel("Made with ♥ by the Schedule Kings")
        footer.setAlignment(Qt.AlignCenter)
        footer.setStyleSheet(footer_label_style())
        self.layout.addWidget(footer)

    # --------------------------------------------------------------- progress
    def show_progress_bar(self, text="Generating schedules...", title="Generating"):
        """Show a modal busy indicator."""
        if self.progress_bar:
            self.progress_bar.close()
        self.progress_bar = QProgressDialog(text, "Cancel", 0, 0, self)
        self.progress_bar.setWindowModality(Qt.WindowModal)
        self.progress_bar.setMinimumDuration(0)
        self.progress_bar.setAutoClose(False)
        self.progress_bar.setAutoReset(False)
        self.progress_bar.setWindowTitle(title)
        self.progress_bar.show()

    def close_progress_bar(self):
        if self.progress_bar:
            self.progress_bar.close()
            self.progress_bar = None

    # ------------------------------------------------------------------- data
    def populate_courses(self, courses: List[Course]):
        """Populate the course list with available courses."""
        self.course_list.populate_courses(courses)
        self.title_label.setText(f"Available Courses ({len(courses)} total)")
        self.selected_panel.update_selection([])
        self._update_submit_button_state([])
        self._update_empty_state()

    def get_all_courses(self) -> List[Course]:
        return self.course_list.courses

    def _update_empty_state(self):
        self.list_stack.setCurrentIndex(1 if self.course_list.courses else 0)
        has_courses = bool(self.course_list.courses)
        self.search_bar.setEnabled(has_courses)
        self.course_list.category_filter.setEnabled(has_courses)

    def _handle_search(self, text: str):
        self.course_list.filter_courses(text)
        self.title_label.setText(f"Available Courses ({len(self.course_list.get_selected_courses())} selected)")

    def _handle_selection_changed(self, selected_courses: List[Course]):
        if len(selected_courses) > self.MAX_COURSES:
            # Undo the selection that went over the limit
            self.course_list.selected_course_codes.remove(selected_courses[-1].course_code)
            self.course_list._update_course_list(self.course_list.filtered_courses)
            QMessageBox.warning(self, "Course Limit", f"You cannot select more than {self.MAX_COURSES} courses.")
            return

        self.selected_panel.update_selection(selected_courses)
        self.title_label.setText(f"Available Courses ({len(selected_courses)} selected)")
        self._update_submit_button_state(selected_courses)
        self.coursesSelected.emit(selected_courses)

    def _handle_submit(self):
        selected = self.course_list.get_selected_courses()
        if len(self.course_list.courses) == 0:
            QMessageBox.critical(self, "Error", "No courses loaded. Please load courses first.")
            return
        if len(selected) == 0:
            QMessageBox.critical(self, "Error", "No courses selected. Please select courses first.")
            return
        if len(selected) > self.MAX_COURSES:
            QMessageBox.warning(self, "Course Limit", f"You cannot select more than {self.MAX_COURSES} courses.")
            return
        self.coursesSubmitted.emit(selected)

    def _handle_clear(self):
        self.close_progress_bar()
        self.course_list.clear_selection()
        self.selected_panel.clear()
        self.search_bar.clear()
        self.title_label.setText(f"Available Courses ({len(self.course_list.courses)} total)")

    def _handle_load(self):
        self.close_progress_bar()
        self.loadRequested.emit()

    def get_selected_courses(self) -> List[Course]:
        return self.course_list.get_selected_courses()

    def _update_submit_button_state(self, selected_courses: List[Course]):
        count = len(selected_courses)
        self.count_badge.setText(f"{count} / {self.MAX_COURSES}")
        at_limit = count >= self.MAX_COURSES
        self.count_badge.setProperty("state", "warning" if at_limit else ("success" if count else ""))
        repolish(self.count_badge)
        if count > self.MAX_COURSES:
            self.submit_button.setEnabled(False)
            self.limit_label.setStyleSheet(warning_label_style())
        else:
            self.submit_button.setEnabled(True)
            self.limit_label.setStyleSheet(warning_label_style() if at_limit else success_label_style())
        remaining = self.MAX_COURSES - count
        if at_limit:
            self.limit_label.setText(f"Maximum {self.MAX_COURSES} courses allowed - limit reached")
        else:
            self.limit_label.setText(f"Maximum {self.MAX_COURSES} courses allowed - {remaining} more available")

    def select_courses_by_code(self, codes):
        """Select courses in the list by their course codes."""
        self.course_list.selected_course_codes = set(codes)
        self.course_list._update_course_list(self.course_list.courses)
        self._handle_selection_changed(self.get_selected_courses())

    def update_selected_courses_panel(self):
        """Re-render the selected courses in the SelectedCoursesPanel."""
        self.selected_panel.update_selection(self.get_selected_courses())
