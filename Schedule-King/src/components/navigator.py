from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLineEdit, QLabel, QMessageBox)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QIcon, QIntValidator, QTransform
from src.models.schedule import Schedule
from typing import List
import os
from src.styles.theme import PALETTE
from src.styles.icons import icon

class Navigator(QWidget):
    """
    An navigator component for browsing through schedules.
    Features better UI design and functionality.
    
    The navigator provides:
    - Previous/Next buttons for sequential navigation
    - A direct input field to jump to specific schedules
    - A display showing current position in the schedule list
    - Visual feedback and validation for user inputs
    """
    # Signal emitted when the schedule changes
    # This allows other components to react to navigation changes
    schedule_changed = pyqtSignal(int)
    
    def __init__(self, schedules: int):
        """
        Initialize the enhanced Navigator widget.

        Args:
        """
        super().__init__()
        self.current_index = 0      # Track current position in the schedule list
        if schedules <=0 :
            self.available_count = 0 # Number of currect available schedules

        # --- LAYOUT SETUP ---
        # Main layout is horizontal with proper spacing and margins
        self.layout = QHBoxLayout()
        self.layout.setContentsMargins(0, 0, 0, 0)
        self.layout.setSpacing(15)
        self.setLayout(self.layout)
        
        # --- NAVIGATION CONTROLS ---
        # Create a container for all navigation elements
        nav_container = QHBoxLayout()
        nav_container.setSpacing(8)
        nav_container.setAlignment(Qt.AlignCenter)  # Center all navigation elements
        
        # Previous button setup
        self.prev_btn = QPushButton()
        self.prev_btn.setObjectName("nav_button")
        self.prev_btn.setToolTip("Previous Schedule")
        self.prev_btn.setFixedSize(40, 40)
        
        # --- INPUT FIELD SETUP ---
        # Container for the schedule number input and label
        input_container = QVBoxLayout()
        input_container.setSpacing(3)
        input_container.setContentsMargins(0, 0, 0, 0)
        
        # Label showing current position (e.g., "Schedule 1 of 5")
        self.info_label = QLabel()
        self.info_label.setObjectName("info_label")
        self.info_label.setAlignment(Qt.AlignCenter)
        
        # Input field for direct schedule selection
        self.schedule_num = QLineEdit()
        self.schedule_num.setObjectName("schedule_num")
        self.schedule_num.setFixedHeight(40)
        self.schedule_num.setPlaceholderText("Jump to...")
        self.schedule_num.setAlignment(Qt.AlignCenter)
        
        # Add integer validator to ensure only valid numbers can be entered
        validator = QIntValidator(1, 9999999)  # Allow numbers between 1 and 9999999
        self.schedule_num.setValidator(validator)
        
        # Add input elements to their container
        
        # Next button setup (mirrors previous button)
        self.next_btn = QPushButton()
        self.next_btn.setObjectName("nav_button")
        self.next_btn.setToolTip("Next Schedule")
        self.next_btn.setFixedSize(40, 40)
        
        # Add navigation icons (with fallbacks)
        self.prev_btn.setIcon(icon("chevron_left", 18, PALETTE["text"]))
        self.next_btn.setIcon(icon("chevron_right", 18, PALETTE["text"]))
        for button in (self.prev_btn, self.next_btn):
            button.setCursor(Qt.PointingHandCursor)

        # --- ASSEMBLE NAVIGATION CONTROLS ---
        # Add all elements to the navigation container with proper spacing
        nav_container.addWidget(self.prev_btn)
        nav_container.addWidget(self.schedule_num)
        nav_container.addWidget(self.next_btn)
        nav_container.addSpacing(6)
        nav_container.addWidget(self.info_label)
        
        # Add navigation container to main layout with proper spacing
        self.layout.addLayout(nav_container)
        
        # --- CONNECT SIGNALS ---
        # Connect button clicks and input events to their handlers
        self.prev_btn.clicked.connect(self.go_to_previous)
        self.next_btn.clicked.connect(self.go_to_next)
        self.schedule_num.returnPressed.connect(self.on_schedule_num_entered)
        
        # Initialize the display
        self.update_display()

    def update_display(self):
        """
        Updates the UI to reflect the current schedule position.
        This includes:
        - Updating the info label
        - Setting the input field value
        - Enabling/disabling navigation buttons
        """
        if self.available_count > 0:
            # Update position display
            self.info_label.setText(f"Schedule {self.current_index + 1} of {self.available_count}")
            
            # Prevents the input field from being overwritten while the user is typing
            if not self.schedule_num.hasFocus():
                self.schedule_num.setText(str(self.current_index + 1))

            # Enable/disable buttons based on position
            self.prev_btn.setEnabled(self.current_index > 0)  # Disable at start
            self.next_btn.setEnabled(self.current_index < self.available_count - 1)  # Disable at end
        else:
            # Handle case when no schedules are available
            self.info_label.setText("No schedules available")
            self.schedule_num.setText("")
            self.prev_btn.setEnabled(False)
            self.next_btn.setEnabled(False)

    def go_to_next(self):
        """
        Navigate to the next schedule if available.
        Updates the display and emits the schedule_changed signal.
        """
        if self.current_index + 1 < self.available_count:
            self.current_index += 1
            self.update_display()
            self.schedule_changed.emit(self.current_index)

    def go_to_previous(self):
        """
        Navigate to the previous schedule if available.
        Updates the display and emits the schedule_changed signal.
        """
        if self.current_index > 0:
            self.current_index -= 1
            self.update_display()
            self.schedule_changed.emit(self.current_index)

    def on_schedule_num_entered(self):
        """
        Handle direct schedule number input.
        Validates the input and navigates to the selected schedule.
        Shows warning messages for invalid inputs.
        """
        try:
            # Convert input to zero-based index
            index = int(self.schedule_num.text()) - 1
            if 0 <= index < self.available_count:
                self.current_index = index
                self.update_display()
                self.schedule_changed.emit(self.current_index)
            else:
                # Show warning for out-of-range numbers
                QMessageBox.warning(
                    self,
                    "Invalid Schedule Number",
                    f"Please enter a number between 1 and {self.available_count}."
                )
                self.schedule_num.setText(str(self.current_index + 1))
        except ValueError:
            # Show warning for invalid input
            QMessageBox.warning(
                self,
                "Invalid Input",
                "Please enter a valid number."
            )
            self.schedule_num.setText(str(self.current_index + 1))

    def set_schedules(self, schedules: int):
        """
        Update the list of schedules and reset navigation.
        This is called when new schedules are loaded.
        """
        self.available_count = schedules  # Update available_count
        
        # Update the validator range when schedule count changes
        if self.available_count > 0:
          #  self.schedule_changed.emit(self.current_index)
            self.schedule_num.setValidator(QIntValidator(1, self.available_count))
        
        # Only reset index if we're setting schedules for the first time
        # or if schedules were previously empty
        if self.available_count == 0 or self.current_index < 0:
            self.current_index = 0 if schedules <=0 else -1
        elif self.available_count > 0:
            # Keep current index if possible, otherwise set to last available
            self.current_index = min(self.current_index, self.available_count - 1)
        else:
            self.current_index = -1
            
        self.update_display()
        # if self.schedules and self.current_index >= 0:
        #     self.schedule_changed.emit(self.current_index)
    
    def get_current_schedule(self):
        """
        Get the currently selected schedule.
        Returns None if no valid schedule is selected.
        """
        if 0 <= self.current_index < self.available_count:
            return self.current_index
        return None