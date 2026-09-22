from PyQt5.QtWidgets import QLineEdit, QVBoxLayout, QWidget
from PyQt5.QtCore import pyqtSignal

class SearchBar(QWidget):
    # Signal emitted when the search text changes
    searchTextChanged = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        
        # Create a vertical layout for the widget
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create the search input field
        self.search_input = QLineEdit()
        self.search_input.setObjectName("course_search_bar")
        self.search_input.setPlaceholderText("Search by course name or code...")
        self.search_input.setClearButtonEnabled(True)
        self.search_input.setMinimumHeight(40)
        self.search_input.textChanged.connect(self._handle_text_changed)  # Connect text change signal
        
        layout.addWidget(self.search_input)  # Add input to the layout

    def _handle_text_changed(self, text: str):
        # Emit custom signal when the text changes
        self.searchTextChanged.emit(text)

    def clear(self):
        # Clear the search input field
        self.search_input.clear() 