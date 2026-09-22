from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon, QFont, QPixmap
from src.components.export_controls import ExportControls
from src.controllers.ScheduleController import ScheduleController
import os
from src.styles.theme import PALETTE
from src.styles.icons import icon

class ScheduleHeader(QWidget):
    """
    Header component for the schedule window containing:
    - Back button
    - Title with crown icon
    - Export controls
    """
    def __init__(self, controller : ScheduleController ,export_handler):
        super().__init__()
        self.export_handler = export_handler
        self.controller = controller  # Reference to the controller for handling back navigation
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize and setup the header UI components"""
        # Main layout (this will be removed or modified in ScheduleWindow)
        header_layout = QHBoxLayout()
        header_layout.setSpacing(15)
        self.setLayout(header_layout) # Keep this for now, will be replaced when components are moved out
        
        # Back button (make public)
        self.back_button = QPushButton("  Back to courses")
        self.back_button.setObjectName("top_action_button")
        self.back_button.setIcon(icon("back", 18, PALETTE["text"]))
        self.back_button.setCursor(Qt.PointingHandCursor)
        self.back_button.setMinimumHeight(42)

        # Title container (make public)
        self.title_container = QWidget()
        self.title_container.setObjectName("title_container")
        title_row = QHBoxLayout(self.title_container)
        title_row.setContentsMargins(0, 0, 0, 0)
        title_row.setSpacing(12)

        crown_label = QLabel()
        crown_pixmap = QPixmap(os.path.join(os.path.dirname(__file__), "../assets/logo.png"))
        if not crown_pixmap.isNull():
            crown_label.setPixmap(crown_pixmap.scaled(48, 48, Qt.KeepAspectRatio, Qt.SmoothTransformation))
        else:
            crown_label.setText("👑")
        title_row.addWidget(crown_label)

        title_text_layout = QVBoxLayout()
        title_text_layout.setSpacing(0)
        self.headline = QLabel("Schedule King")
        self.headline.setObjectName("headline_label")
        self.subtitle = QLabel("Generating conflict-free schedules...")
        self.subtitle.setObjectName("subtitle_label")
        title_text_layout.addWidget(self.headline)
        title_text_layout.addWidget(self.subtitle)
        title_row.addLayout(title_text_layout)

        # Export controls (make public)
        self.export_controls = ExportControls(self.controller, self.export_handler)
        self.export_controls.setObjectName("export_controls_widget")

    def set_schedule_count(self, count: int):
        """Show how many schedules were found under the title."""
        if count and count > 0:
            noun = "schedule" if count == 1 else "schedules"
            self.subtitle.setText(f"{count:,} conflict-free {noun} found")
        else:
            self.subtitle.setText("Generating conflict-free schedules...")
