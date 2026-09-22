from PyQt5.QtWidgets import QWidget, QHBoxLayout, QPushButton, QCheckBox, QFileDialog, QMessageBox
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from src.models.schedule import Schedule
from src.controllers.ScheduleController import ScheduleController
from typing import List, Callable, Optional
import os
from src.styles.icons import icon

class ExportControls(QWidget):
    """
    Export controls component containing:
    - Export button
    - Export visible only checkbox
    - Export functionality
    """
    def __init__(self, controller: ScheduleController, export_handler: Callable[[str, Optional[List[Schedule]]], None]):
        super().__init__()
        self.export_handler = export_handler
        self.controller = controller  # Reference to the controller for handling export logic
        self.current_index = 0  # Store current index
        self.setup_ui()
        
    def setup_ui(self):
        """Initialize and setup the export controls UI"""
        # Main layout
        layout = QHBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(14)
        self.setLayout(layout)
        
        # Export button
        self.export_button = QPushButton("  Export Schedule")
        self.export_button.setObjectName("top_action_button")
        self.export_button.setProperty("variant", "primary")
        self.export_button.setIcon(icon("download", 18, "#FFFFFF"))
        self.export_button.setCursor(Qt.PointingHandCursor)
        self.export_button.setMinimumHeight(42)
        self.export_button.setToolTip("Save schedules as a text or Excel file")
            
        # Export visible only checkbox
        self.export_visible_only = QCheckBox("Current schedule only")
        self.export_visible_only.setObjectName("export_checkbox")
        
        # Add components to layout
        layout.addWidget(self.export_visible_only)
        layout.addWidget(self.export_button)
        
        # Connect button click
        self.export_button.clicked.connect(self.export_to_file)
        
    def update_data(self, current_index: int):
        """
        Update the stored schedules and current index.
        
        Args:
            schedules (List[Schedule]): List of all schedules
            current_index (int): Index of currently visible schedule
        """
        self.current_index = current_index
        
    def export_to_file(self):
        """Handle export button click"""
        size = self.controller.ranker.size()
        if self.current_index < 0 or self.current_index >= size :
            QMessageBox.warning(self, "No Schedules", "No schedules available to export.")
            return
            
        file_path, selected_filter = QFileDialog.getSaveFileName(
            self, "Save Schedules", "", 
            "Text Files (*.txt);;Excel Files (*.xlsx);;All Files (*)"
        )
        if file_path:
            # Add extension based on selected filter if not already present
            if selected_filter == "Text Files (*.txt)" and not file_path.endswith('.txt'):
                file_path += '.txt'
            elif selected_filter == "Excel Files (*.xlsx)" and not file_path.endswith('.xlsx'):
                file_path += '.xlsx'
            
            try:
                if self.export_visible_only.isChecked() and 0 <= self.current_index < size:
                    # Export only the visible schedule
                    self.export_handler(file_path,None)
                else:
                    # Calculate how many schedules we can get (up to 100)
                    remaining_schedules = self.controller.ranker.size() - self.current_index
                    count = min(100, remaining_schedules)
                    if count <= 0:
                        QMessageBox.warning(
                            self,
                            "No Schedules to Export",
                            "There are no more schedules available to export from the current position."
                        )
                        return
                        
                    self.export_handler(file_path, self.controller.get_ranked_schedules(count, self.current_index))
                    
                QMessageBox.information(
                    self, "Export Successful",
                    f"Schedules were saved successfully to:\n{file_path}"
                )
            except Exception as e:
                error_msg = str(e)
                print(f"Export error: {error_msg}")
                QMessageBox.critical(
                    self, "Export Failed",
                    f"Failed to export schedules:\n{error_msg}"
                ) 