from PyQt5.QtWidgets import (
    QMainWindow, QVBoxLayout, QWidget, QFileDialog, QMessageBox,
    QHBoxLayout, QFrame, QPushButton, QSpacerItem, QSizePolicy, QProgressBar, QLabel, QCheckBox, QInputDialog
)
from PyQt5.QtCore import Qt, QSize, QThread, QTimer, pyqtSignal
from PyQt5.QtGui import QIcon, QFont, QPixmap
from src.components.navigator import Navigator
from src.components.schedule_table import ScheduleTable, ScheduleLegend
from src.components.schedule_header import ScheduleHeader
from src.components.schedule_progress import ScheduleProgress
from src.components.full_size_window import FullSizeWindow
from src.components.ScheduleMetrics import ScheduleMetrics
from src.components.loading_overlay import LoadingOverlay
from src.models.schedule import Schedule
from src.controllers.ScheduleController import ScheduleController
from src.components.ranking_controls import RankingControls
from src.services.schedule_event_maker import ScheduleEventMaker
from typing import List, Optional
import os
from src.components.semester_choice_dialog import SemesterChoiceDialog
from src.styles.theme import PALETTE
from src.styles.icons import icon

class ScheduleWindow(QMainWindow):
    """
    Main window for displaying and managing generated schedules.
    Uses modular components for better maintainability.
    """
    def __init__(self, controller: ScheduleController, maximize_on_start=True, show_progress_on_start=True):
        super().__init__()
        self.setup_window()  # Set up window properties and layout
        self.setup_components(-1, controller)  # Set up all UI components
        self.setup_connections()  # Connect signals and slots
        self.setWindowState(Qt.WindowMaximized)
        self.show()

    def setup_window(self):
        """Initialize window properties and layout"""
        # Set window properties
        self.setObjectName("ScheduleWindow")
        self.setWindowTitle("Schedule King")
        icon_path = os.path.join(os.path.dirname(__file__), "../assets/logo.png")
        self.setWindowIcon(QIcon(icon_path))
        
        # Create main layout
        self.central_widget = QWidget()
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setSpacing(14)
        self.main_layout.setContentsMargins(28, 22, 28, 18)
        self.setCentralWidget(self.central_widget)
        
        # Set window size
        self.setMinimumSize(1100, 720)
        self.resize(1440, 900)
        
    def setup_components(self, schedules: int , controller: ScheduleController):
        """Initialize and setup all window components"""
        # Store references
        self.controller = controller
        self.schedules = schedules
        self.first_schedule_shown = False
        self.full_size_window = None
        self.on_back = lambda: None  # Default no-op callback for navigation back to course selection
        
        # Initialize loading overlay and export worker
        self.loading_overlay = None

        # Header: back button, title, export controls
        self.header = ScheduleHeader(self.controller, self.handle_export)

        top_layout = QHBoxLayout()
        top_layout.setSpacing(16)
        top_layout.setContentsMargins(0, 0, 0, 0)
        top_layout.addWidget(self.header.back_button, 0, Qt.AlignVCenter)
        top_layout.addWidget(self.header.title_container, 0, Qt.AlignVCenter)
        top_layout.addStretch(1)
        top_layout.addWidget(self.header.export_controls, 0, Qt.AlignVCenter)
        top_widget_container = QWidget()
        top_widget_container.setObjectName("schedule_top_bar")
        top_widget_container.setLayout(top_layout)
        self.main_layout.addWidget(top_widget_container)

        # Metric tiles
        self.metrics_widget = ScheduleMetrics(Schedule([]))
        self.main_layout.addWidget(self.metrics_widget)

        # Toolbar: progress, navigator, ranking and quick actions
        toolbar = QWidget()
        toolbar.setObjectName("toolbar_card")
        nav_container = QHBoxLayout(toolbar)
        nav_container.setContentsMargins(14, 8, 14, 8)
        nav_container.setSpacing(12)

        self.navigator = Navigator(-1)
        self.navigator.setObjectName("compact_navigator")
        nav_container.addWidget(self.navigator)

        self.progress = ScheduleProgress()
        nav_container.addWidget(self.progress)
        nav_container.addStretch(1)

        self.ranking_controls = RankingControls()
        self.ranking_controls.setObjectName("ranking_controls")
        nav_container.addWidget(self.ranking_controls)

        divider = QFrame()
        divider.setFrameShape(QFrame.VLine)
        divider.setStyleSheet(f"color: {PALETTE['border']};")
        nav_container.addWidget(divider)

        self.full_size_button = self._icon_button("expand", "⛶", "Open in a full-size window")
        self.refresh_button = self._icon_button("refresh", "↻", "Refresh the current schedule")
        self.export_calendar_button = self._icon_button("calendar", "Export Calendar",
                                                        "Export this schedule to Google Calendar")
        self.export_calendar_button.setObjectName("export_calendar_button")
        for button in (self.full_size_button, self.refresh_button, self.export_calendar_button):
            nav_container.addWidget(button)
        self.main_layout.addWidget(toolbar)

        # Timetable + legend
        self.schedule_table = ScheduleTable()
        self.schedule_table.setObjectName("enhanced_table")
        self.main_layout.addWidget(self.schedule_table, 1)

        self.legend = ScheduleLegend()
        self.main_layout.addWidget(self.legend)

    def _icon_button(self, icon_name: str, fallback_text: str, tooltip: str) -> QPushButton:
        button = QPushButton()
        button.setObjectName("nav_button")
        button.setFixedSize(40, 40)
        button.setToolTip(tooltip)
        button.setCursor(Qt.PointingHandCursor)
        button.setIcon(icon(icon_name, 20, PALETTE["text"]))
        button.setIconSize(QSize(20, 20))
        return button

    def setup_connections(self):
        """Setup signal connections between components"""
        # Connect navigator signals
        self.navigator.schedule_changed.connect(self.on_schedule_changed)
        
        # Connect header buttons
        self.header.back_button.clicked.connect(self.navigateToCourseWindow)
        
        # Connect full size button
        self.full_size_button.clicked.connect(self.open_full_size)
        
        # Connect refresh button
        self.refresh_button.clicked.connect(self.on_refresh_button_clicked)
        
        # Connect export calendar button
        self.export_calendar_button.clicked.connect(self.on_export_calendar_clicked)
        
        # Connect controller callbacks
        self.controller.on_schedules_generated = self.on_schedule_generated
        self.controller.on_progress_updated = self.progress.update_progress

        # Connect ranking controls to controller
        self.ranking_controls.preference_changed.connect(self.on_preference_changed)
        
    def show_initial_schedule(self):
        """Display the first schedule if available"""
        # Force window to be maximized

        self.setWindowState(Qt.WindowMaximized)
        
    # Properties for backward compatibility with tests
    @property
    def export_button(self):
        """Access to export button for backward compatibility"""
        return self.header.export_controls.export_button
        
    @property
    def back_button(self):
        """Access to back button for backward compatibility"""
        return self.header.back_button
        
    @property
    def export_visible_only(self):
        """Access to export checkbox for backward compatibility"""
        return self.header.export_controls.export_visible_only
        
    def displaySchedules(self, schedules: List[Schedule]):
        """
        Updates the navigator and table with new schedules.
        For backward compatibility.
        """
        self.schedules = schedules
        self.navigator.set_schedules(schedules)
        if schedules:
            self.on_schedule_changed(0)
            # Enable refresh button if schedules are displayed
            self.refresh_button.setEnabled(True)
        else:
            self.schedule_table.clearContents()
            # Update export controls with empty data
            self.header.export_controls.update_data([], 0)
            # Disable refresh button if no schedules are displayed
            self.refresh_button.setEnabled(False)

    def on_schedule_changed(self, index: int):
        """
        Handle schedule change event from navigator and preference controls.
        Updates the table, metrics, and export controls.
        """
        if 0 <= index < self.schedules:
            try:
                # Get the ranked schedule based on current preference
                schedule = self.controller.get_kth_schedule(index)
                self.current_schedule = schedule  # Store current schedule for full size window
                self.schedule_table.display_schedule(schedule)
                # Update export controls with current schedules and index
                self.header.export_controls.update_data(index)
                self.header.export_controls.export_button.setEnabled(True)
                self.header.back_button.setEnabled(True)

                # Update the metric tiles and the colour legend
                self.metrics_widget.set_schedule(schedule)
                entries = getattr(self.schedule_table, "legend_entries", None)
                self.legend.set_entries(entries if isinstance(entries, list) else [])

                # Enable the refresh button since a schedule is displayed
                self.refresh_button.setEnabled(True)

            except IndexError:
                self.schedule_table.clearContents()
                self.header.export_controls.update_data(0)
                self.header.export_controls.export_button.setEnabled(False)
                self.header.back_button.setEnabled(False)
                # Disable the refresh button when there's an error or no schedules
                self.refresh_button.setEnabled(False)
        
    def on_schedule_generated(self, schedules_num: int = 0):
        """
        Handle new schedule generation.
        Updates the navigator, table, and export controls.
        """
        self.navigator.set_schedules(schedules_num)
        self.header.set_schedule_count(schedules_num)
        if self.schedules != schedules_num:
            self.schedules = schedules_num
            if schedules_num > 0 and not self.first_schedule_shown:
                self.navigator.current_index = 0
                self.on_schedule_changed(0)
                self.first_schedule_shown = True
                # Enable refresh button if schedules are generated
                self.refresh_button.setEnabled(True)
            elif schedules_num <= 0:
                self.schedule_table.clearContents()
                # Update export controls with empty data
                self.header.export_controls.update_data(0)
                # Disable refresh button if no schedules are generated
                self.refresh_button.setEnabled(False)
                
        if not self.controller.generation_active and  schedules_num<=0:
            self.progress.hide_progress()

    def on_preference_changed(self, metric, ascending):
        """
        Handle changes in ranking preferences.
        Updates the controller and refreshes the schedule display.
        """
        if metric is None:
            # Clear preference
            self.controller.clear_preference()
        else:
            # Set new preference
            self.controller.set_preference(metric, ascending)
        
        # Refresh the schedules display
        if self.navigator.current_index < self.schedules:
            self.on_schedule_changed(self.navigator.current_index)
            
    def navigateToCourseWindow(self):
        """
        Navigate back to course selection.
        Stops schedule generation and hides progress.
        """
        self.controller.stop_schedules_generation()
        self.progress.hide_progress()
        self.on_back()
        
    def handle_export(self, file_path: str, schedules_to_export: Optional[List[Schedule]]):
        """
        Handle export request from ExportControls.
        Calls the controller's export method.
        """
        if not self.schedules or self.navigator.current_index >= self.schedules:
            QMessageBox.warning(self, "No Schedule", "No schedule is currently selected.")
            return
            
        if schedules_to_export is None:
            # Export only the currently displayed schedule
            self.controller.export_schedules(file_path, [self.current_schedule])
        else:
            # Export specific schedules
            self.controller.export_schedules(file_path, schedules_to_export)
                
    def open_full_size(self):
        """
        Open current schedule in full-size window.
        Shows a warning if no schedule is selected.
        """
        if not self.schedules or self.navigator.current_index >= self.schedules:
            QMessageBox.warning(self, "No Schedule", "No schedule is currently selected.")
            return
            
        if self.full_size_window is not None:
            self.full_size_window.close()
            
        self.full_size_window = FullSizeWindow(
            self.current_schedule,
            self.navigator.current_index
        )

    def on_refresh_button_clicked(self):
        """
        Handle refresh button click: reload the current schedule.
        Only attempts to refresh if there are schedules to display.
        """
        current_index = self.navigator.current_index
        # Only attempt to refresh if there are schedules to display
        if 0 <= current_index < self.schedules:
            self.on_schedule_changed(current_index)
        # No else needed, as the button should be disabled if there are no schedules

    def on_export_calendar_clicked(self):
        """
        Handle export to calendar button click.
        Shows loading screen and calls the controller's async export method.
        """
        if not self.schedules or self.navigator.current_index >= self.schedules:
            QMessageBox.warning(self, "No Schedule", "No schedule is currently selected.")
            return
        
        # Use the new modern semester choice dialog
        semester, ok = SemesterChoiceDialog.get_semester(self)
        if not ok or not semester:
            return  # User cancelled
        
        # Disable the export button to prevent multiple clicks
        self.export_calendar_button.setEnabled(False)
        
        # Show loading overlay
        self.show_loading_overlay()
        # Use the controller's async export method, pass semester
        self.controller.export_to_calendar_async(self.current_schedule, semester, self.on_export_finished)
        
    def show_loading_overlay(self):
        """Show the loading overlay"""
        # Always create a new overlay
        if self.loading_overlay is not None:
            self.loading_overlay.deleteLater()
            self.loading_overlay = None

        self.loading_overlay = LoadingOverlay(self, "Exporting to Calendar...")
        self.loading_overlay.cancelled.connect(self.on_export_cancelled)
        window_size = self.size()
        self.loading_overlay.setGeometry(0, 0, window_size.width(), window_size.height())
        self.loading_overlay.show()
        self.loading_overlay.raise_()

    def hide_loading_overlay(self):
        """Hide the loading overlay"""
        if self.loading_overlay:
            self.loading_overlay.stop_spinner()
            self.loading_overlay.hide()
            self.loading_overlay.deleteLater()
            self.loading_overlay = None
            
    def on_export_finished(self, success: bool, message: str):
        """Handle export completion"""
        # Hide loading overlay
        self.hide_loading_overlay()
        # Re-enable the export button
        self.export_calendar_button.setEnabled(True)
        # Show result message
        if success:
            QMessageBox.information(self, "Success", message)
        else:
            QMessageBox.critical(self, "Error", message)
            
    def resizeEvent(self, event):
        """Handle window resize events"""
        super().resizeEvent(event)
        # Update loading overlay size if it exists and is visible
        if self.loading_overlay and self.loading_overlay.isVisible():
            central_size = self.central_widget.size()
            self.loading_overlay.setGeometry(0, 0, central_size.width(), central_size.height())

    def on_export_cancelled(self):
        """Handle export cancellation"""
        # Cancel the export operation
        self.controller.cancel_calendar_export()
        # Hide loading overlay
        self.hide_loading_overlay()
        # Re-enable the export button
        self.export_calendar_button.setEnabled(True)
        # Show cancellation message
        QMessageBox.information(self, "Cancelled", "Calendar export was cancelled.")
