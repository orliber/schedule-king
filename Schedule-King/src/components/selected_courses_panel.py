from PyQt5.QtWidgets import QLabel, QVBoxLayout, QHBoxLayout, QWidget, QScrollArea, QPushButton, QFrame
from PyQt5.QtCore import Qt, pyqtSignal
from typing import List
from src.models.course import Course
from src.styles.theme import PALETTE, course_color


class _SelectedCourseRow(QFrame):
    """One selected course: colour dot, name, code/instructor and a remove button."""

    def __init__(self, course: Course, index: int, on_remove, parent=None):
        super().__init__(parent)
        bg, accent, _ = course_color(index)
        self.setObjectName("selected_row")
        self.setStyleSheet(f"""
            QFrame#selected_row {{
                background-color: {PALETTE['surface']};
                border: 1px solid {PALETTE['border']};
                border-left: 4px solid {accent};
                border-radius: 10px;
            }}
        """)
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 6, 8)
        layout.setSpacing(8)

        text = QVBoxLayout()
        text.setSpacing(1)
        name = QLabel(course.name)
        name.setStyleSheet(f"font-weight: 600; color: {PALETTE['text']};")
        name.setWordWrap(True)
        details = course.instructor if course.is_detailed else "loading details..."
        meta = QLabel(f"{course.course_code}  ·  {details}")
        meta.setStyleSheet(f"font-size: 12px; color: {PALETTE['text_muted']};")
        meta.setWordWrap(True)
        text.addWidget(name)
        text.addWidget(meta)
        layout.addLayout(text, 1)

        remove = QPushButton("✕")
        remove.setProperty("variant", "ghost")
        remove.setFixedSize(28, 28)
        remove.setStyleSheet("padding: 0; font-size: 12px;")
        remove.setCursor(Qt.PointingHandCursor)
        remove.setToolTip(f"Remove {course.name}")
        remove.clicked.connect(lambda: on_remove(course.course_code))
        layout.addWidget(remove, 0, Qt.AlignTop)


class SelectedCoursesPanel(QWidget):
    removeRequested = pyqtSignal(str)

    EMPTY_TEXT = "No courses selected yet.\nPick courses from the catalog on the left."

    def __init__(self, parent=None):
        super().__init__(parent)
        outer_layout = QVBoxLayout(self)
        outer_layout.setContentsMargins(0, 0, 0, 0)

        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setFrameShape(QFrame.NoFrame)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        scroll_area.setStyleSheet("QScrollArea { background: transparent; }")

        inner_widget = QWidget()
        inner_widget.setStyleSheet("background: transparent;")
        self.inner_layout = QVBoxLayout(inner_widget)
        self.inner_layout.setContentsMargins(0, 0, 4, 0)
        self.inner_layout.setSpacing(8)

        # Kept as the empty-state message (and for backwards compatibility)
        self.label = QLabel(self.EMPTY_TEXT)
        self.label.setAlignment(Qt.AlignCenter)
        self.label.setWordWrap(True)
        self.label.setStyleSheet(f"""
            QLabel {{
                color: {PALETTE['text_subtle']};
                border: 1.5px dashed {PALETTE['border_strong']};
                border-radius: 12px;
                padding: 28px 12px;
                font-size: 13px;
            }}
        """)
        self.inner_layout.addWidget(self.label)
        self.inner_layout.addStretch(1)

        scroll_area.setWidget(inner_widget)
        outer_layout.addWidget(scroll_area)
        self._rows: List[QWidget] = []

    def update_selection(self, selected_courses: List[Course]):
        for row in self._rows:
            self.inner_layout.removeWidget(row)
            row.deleteLater()
        self._rows = []
        self.label.setVisible(not selected_courses)
        for i, course in enumerate(sorted(selected_courses, key=lambda c: c.course_code)):
            row = _SelectedCourseRow(course, i, self.removeRequested.emit)
            self.inner_layout.insertWidget(self.inner_layout.count() - 1, row)
            self._rows.append(row)

    def clear(self):
        self.update_selection([])
