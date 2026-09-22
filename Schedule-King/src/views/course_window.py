from PyQt5.QtWidgets import (
    QMainWindow, QFileDialog, QVBoxLayout,
    QHBoxLayout, QWidget, QSizePolicy, QMessageBox,
    QPushButton, QDialog, QLabel
)
from PyQt5.QtCore import Qt, pyqtSignal, QTimer, QSize
from typing import List, Callable, Optional
import os
from src.models.course import Course
from src.models.time_slot import TimeSlot
from src.components.course_selector import CourseSelector
from src.components.choicefreak_loader_dialog import ChoiceFreakLoaderDialog
from src.components.constraint_dialog import ConstraintDialog
from src.components.CourseEditorDialog import CourseEditorDialog
from src.components.user_guide_dialog import UserGuideDialog
from src.styles.theme import PALETTE
from src.styles.icons import icon

# Bundled demo catalog used by the "Try sample data" button
SAMPLE_COURSES_PATH = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "sample_data", "sample_courses.txt",
)

class LoadCoursesDialog(QDialog):
    """Dialog with two options for loading courses: a local file or ChoiceFreak."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Load Courses")
        self.setModal(True)
        self.setFixedSize(560, 300)
        self.result_action = None  # "local", "choicefreak", or None
        self._setup_ui()

    def _option_button(self, icon_name: str, title: str, description: str) -> QPushButton:
        button = QPushButton()
        button.setCursor(Qt.PointingHandCursor)
        button.setMinimumHeight(170)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {PALETTE['surface']};
                border: 1.5px solid {PALETTE['border']};
                border-radius: 16px;
            }}
            QPushButton:hover {{
                border-color: {PALETTE['primary']};
                background-color: {PALETTE['primary_soft']};
            }}
        """)
        inner = QVBoxLayout(button)
        inner.setContentsMargins(18, 18, 18, 18)
        inner.setSpacing(6)
        icon_label = QLabel()
        icon_label.setPixmap(icon(icon_name, 36, PALETTE["primary"], 1.8).pixmap(36, 36))
        icon_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        title_label = QLabel(title)
        title_label.setObjectName("section_title")
        title_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        desc_label = QLabel(description)
        desc_label.setObjectName("muted")
        desc_label.setWordWrap(True)
        desc_label.setAttribute(Qt.WA_TransparentForMouseEvents)
        inner.addWidget(icon_label)
        inner.addSpacing(4)
        inner.addWidget(title_label)
        inner.addWidget(desc_label)
        inner.addStretch(1)
        return button

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(24, 22, 24, 24)
        layout.setSpacing(16)

        title = QLabel("Where should we load courses from?")
        title.setObjectName("section_title")
        layout.addWidget(title)

        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(14)
        self.local_button = self._option_button(
            "folder", "Local file", "A .txt or .xlsx course file from your computer")
        self.local_button.setToolTip("Load from Local File")
        self.local_button.clicked.connect(self._select_local)
        self.choicefreak_button = self._option_button(
            "globe", "ChoiceFreak", "Fetch a full university catalog online")
        self.choicefreak_button.setToolTip("Load from Global Database")
        self.choicefreak_button.clicked.connect(self._select_choicefreak)
        buttons_layout.addWidget(self.local_button)
        buttons_layout.addWidget(self.choicefreak_button)
        layout.addLayout(buttons_layout)

    def _select_local(self):
        self.result_action = "local"
        self.accept()

    def _select_choicefreak(self):
        self.result_action = "choicefreak"
        self.accept()

    def get_selected_action(self):
        return self.result_action


class CourseWindow(QMainWindow):
    choicefreakSelectionMade = pyqtSignal(str, str)  # define at class level
    def __init__(self, maximize_on_start=True, fullscreen_on_start=False):
        super().__init__()
        self.setWindowTitle("Schedule King - Select Courses")
        self._maximize_on_start = maximize_on_start
        self._fullscreen_on_start = fullscreen_on_start
        self._first_show = True
        self.setMinimumSize(1100, 720)

        # === Course Selector ===
        self.courseSelector = CourseSelector()
        self.courseSelector.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.courseSelector.coursesSubmitted.connect(self.navigateToSchedulesWindow)
        self.courseSelector.browseRequested.connect(self._open_load_dialog)
        self.courseSelector.sampleRequested.connect(self.load_sample_courses)
        # The selector's own load button is replaced by the richer "Load Courses" dialog button
        self.courseSelector.load_button.hide()

        outer_layout = QVBoxLayout()
        outer_layout.setContentsMargins(32, 24, 32, 16)
        outer_layout.setSpacing(0)
        outer_layout.addWidget(self.courseSelector)

        # === Header actions ===
        self.load_data_button = self._create_load_data_button()
        self.add_edit_course_button = QPushButton("  Add / Edit Course")
        self.add_edit_course_button.setIcon(icon("edit", 18, PALETTE["text"]))
        self.add_edit_course_button.setCursor(Qt.PointingHandCursor)
        self.add_edit_course_button.clicked.connect(self.open_course_editor_dialog)
        self.user_guide_button = self._create_user_guide_button()
        self.courseSelector.header_actions.addWidget(self.load_data_button)
        self.courseSelector.header_actions.addWidget(self.add_edit_course_button)
        self.courseSelector.header_actions.addWidget(self.user_guide_button)

        # === Time Constraints ===
        self.forbidden_slots = set()
        self.preferred_slots = set()
        self.constraintBtn = self._create_time_constraints_button()
        self.constraintBtn.clicked.connect(self._open_constraint_dialog)
        self.constraintBtn.setCursor(Qt.PointingHandCursor)
        self.courseSelector.secondary_actions.addWidget(self.constraintBtn)

        container = QWidget()
        container.setLayout(outer_layout)
        self.setCentralWidget(container)

        # External callbacks for handling events
        self.on_courses_loaded: Callable[[str], None] = lambda path: None
        self.on_continue: Callable[
            [List[Course], Optional[List[TimeSlot]], Optional[List[TimeSlot]]],
            None] = lambda selected, forbidden, preferred: None
        self.on_course_added_or_updated = None

        # Note: the Clear button only clears course selections, not time constraints.

    def _create_load_data_button(self) -> QPushButton:
        button = QPushButton("  Load Courses")
        button.setProperty("variant", "primary")
        button.setIcon(icon("upload", 18, "#FFFFFF"))
        button.setIconSize(QSize(18, 18))
        button.setToolTip("Load courses from a file or from ChoiceFreak")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(self._open_load_dialog)
        return button

    def load_sample_courses(self):
        """Load the bundled demo catalog so the app can be explored without any files."""
        if not os.path.exists(SAMPLE_COURSES_PATH):
            QMessageBox.warning(self, "Sample Data Missing", f"Sample file not found:\n{SAMPLE_COURSES_PATH}")
            return
        self.courseSelector._handle_clear()
        self.on_courses_loaded(SAMPLE_COURSES_PATH)

    def _open_load_dialog(self):
        """Open the load courses dialog"""
        dialog = LoadCoursesDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            action = dialog.get_selected_action()
            if action == "local":
                self.load_courses_from_file()
            elif action == "choicefreak":
                self.load_courses_from_choicefreak()

    def showEvent(self, event):
        super().showEvent(event)
        if self._fullscreen_on_start:
            self.showFullScreen()
        elif self._maximize_on_start:
            self.showMaximized()
        # Force layout update every time
        if self.centralWidget() and self.centralWidget().layout():
            self.centralWidget().layout().activate()
            self.centralWidget().updateGeometry()
            self.centralWidget().adjustSize()
        # Force a resize event
        self.resize(self.size())

    def _open_constraint_dialog(self):
        """Open the constraint selection dialog"""
        dialog = ConstraintDialog(self, self.forbidden_slots, self.preferred_slots)
        if dialog.exec_() == QDialog.Accepted:
            self.forbidden_slots = dialog.get_forbidden()
            self.preferred_slots = dialog.get_preferred()
            self._update_constraint_button()

    def _update_constraint_button(self):
        forbidden, preferred = len(self.forbidden_slots), len(self.preferred_slots)
        if forbidden or preferred:
            self.constraintBtn.setText(f"  Time Preferences  ·  {preferred} preferred, {forbidden} blocked")
            self.constraintBtn.setToolTip(f"Time Constraints ({forbidden + preferred} slots)")
        else:
            self.constraintBtn.setText("  Time Preferences")
            self.constraintBtn.setToolTip("Set Time Constraints")

    def displayCourses(self, courses: List[Course]):
        """
        Populate the course selector with a list of courses.
        """
        self.courseSelector.populate_courses(courses)

    def handleSelection(self) -> List[Course]:
        """
        Retrieve the list of selected courses from the course selector.
        """
        return self.courseSelector.get_selected_courses()
    
    def navigateToSchedulesWindow(self):
        """
        Handle the event when the user submits their course selection.
        """
        if hasattr(self.courseSelector, 'close_progress_bar'):
            self.courseSelector.close_progress_bar()

        selected = self.handleSelection()
        if selected:
            if len(selected) > 7:
                QMessageBox.warning(self, "Warning", "You cannot select more than 7 courses.")
                return

        # Convert forbidden cells to TimeSlot objects
        forbidden = []
        for row, col in self.forbidden_slots:
            day_index = col + 1  # Sunday=1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            forbidden.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))

        # Convert preferred cells to TimeSlot objects
        preferred = []
        for row, col in self.preferred_slots:
            day_index = col + 1
            start_time = f"{8+row:02d}:00"
            end_time = f"{8+row+1:02d}:00"
            preferred.append(TimeSlot(day=str(day_index), start_time=start_time, end_time=end_time, room="", building=""))

        # Always call on_continue with all three arguments
        self.on_continue(selected, forbidden if forbidden else None, preferred if preferred else None)

    def load_courses_from_file(self):
        """
        Open a file dialog to allow the user to select a course file.
        """
        if hasattr(self.courseSelector, 'close_progress_bar'):
            self.courseSelector.close_progress_bar()
        file_path, _ = QFileDialog.getOpenFileName(
            self,
            "Select Course File",
            "",
            "Text Files (*.txt);;Excel Files (*.xlsx);;All Files (*)"
        )
        if file_path:
            self.courseSelector.close_progress_bar()
            self.courseSelector._handle_clear()
            self.on_courses_loaded(file_path)  # Trigger the courses loaded callback with the file path

    def open_course_editor_dialog(self):
        all_current_courses = self.courseSelector.get_all_courses()
        editor_dialog = CourseEditorDialog(all_current_courses, self)
        editor_dialog.courseEdited.connect(self._handle_course_edited)

        if editor_dialog.exec_() == QDialog.Accepted:
            pass
        else:
            QMessageBox.information(self, "Cancelled", "Course editing cancelled.")

    def _handle_course_edited(self, edited_course: Course):
        if edited_course:
            QMessageBox.information(self, "Course Saved", f"Course '{edited_course.name}' saved successfully.")
            if getattr(self, "on_course_added_or_updated", None):
                self.on_course_added_or_updated(edited_course)

    def load_courses_from_choicefreak(self):
        """Load courses from ChoiceFreak (preserves original functionality)"""
        dialog = ChoiceFreakLoaderDialog(self)
        # Connect the custom signal to a handler method
        dialog.selectionMade.connect(self.on_choicefreak_selection)
        dialog.exec_()  # blocks until dialog closed

    def on_choicefreak_selection(self, university: str, period: str):
        """
        Handle the selection made in the ChoiceFreakLoaderDialog.
        This method should be implemented to fetch courses based on the selected university and period.
        """
        self.courseSelector.course_list.clear_selection()
        self.courseSelector.show_progress_bar("Loading courses from ChoiceFreak...", "Loading")
        QTimer.singleShot(1000, lambda: self.choicefreakSelectionMade.emit(university, period))
    def _create_time_constraints_button(self) -> QPushButton:
        """Button that opens the preferred / blocked hours dialog."""
        button = QPushButton("  Time Preferences")
        button.setIcon(icon("clock", 18, PALETTE["primary"]))
        button.setIconSize(QSize(18, 18))
        button.setToolTip("Set Time Constraints")
        button.setMinimumHeight(42)
        return button

    def _create_constraint_button(self):
        """Create and setup the time constraints button"""
        self.constraintBtn = self._create_time_constraints_button()
        self.constraintBtn.clicked.connect(self._open_constraint_dialog)
        self.constraintBtn.setCursor(Qt.PointingHandCursor)
        return self.constraintBtn

    def _create_user_guide_button(self) -> QPushButton:
        """Round help button that opens the user guide."""
        button = QPushButton("?")
        button.setProperty("variant", "icon")
        button.setFixedSize(40, 40)
        button.setStyleSheet("font-size: 16px; font-weight: 800; border-radius: 20px;")
        button.setToolTip("User Guide & Instructions")
        button.setCursor(Qt.PointingHandCursor)
        button.clicked.connect(self._open_user_guide)
        return button

    def _open_user_guide(self):
        """Open the user guide dialog"""
        dialog = UserGuideDialog(self)
        dialog.exec_()