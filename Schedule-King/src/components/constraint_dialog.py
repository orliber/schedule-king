from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QMessageBox, QToolButton, QButtonGroup
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from src.components.time_constraint_table import TimeConstraintTable
from src.styles.theme import PALETTE


class ConstraintDialog(QDialog):
    def __init__(self, parent=None, initial_forbidden=None, initial_preferred=None):
        super().__init__(parent)
        self.setWindowTitle("Time Preferences")
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowContextHelpButtonHint)
        self.setMinimumSize(980, 700)

        layout = QVBoxLayout()
        layout.setContentsMargins(24, 20, 24, 20)
        layout.setSpacing(14)

        # === Header: title, explanation, help ===
        header_layout = QHBoxLayout()
        titles = QVBoxLayout()
        titles.setSpacing(2)
        title = QLabel("Time preferences")
        title.setObjectName("section_title")
        subtitle = QLabel("Click or drag across the grid. Blocked hours are never scheduled; "
                          "preferred hours raise a schedule's preference score.")
        subtitle.setObjectName("muted")
        subtitle.setWordWrap(True)
        titles.addWidget(title)
        titles.addWidget(subtitle)
        header_layout.addLayout(titles, 1)

        self.help_btn = QToolButton()
        self.help_btn.setText("?")
        self.help_btn.setFixedSize(34, 34)
        self.help_btn.setStyleSheet(f"""
            QToolButton {{
                background-color: {PALETTE['surface']};
                color: {PALETTE['text']};
                border: 1px solid {PALETTE['border_strong']};
                border-radius: 17px;
                font-size: 15px;
                font-weight: 800;
            }}
            QToolButton:hover {{ background-color: {PALETTE['primary_soft']}; color: {PALETTE['primary']}; }}
        """)
        self.help_btn.setToolTip("How is the preference score calculated?")
        self.help_btn.clicked.connect(self.show_scoring_help)
        header_layout.addWidget(self.help_btn, 0, Qt.AlignTop)
        layout.addLayout(header_layout)

        # === Mode selector (segmented control) + live summary ===
        mode_row = QHBoxLayout()
        mode_row.setSpacing(0)
        self.block_btn = QPushButton("Block hours")
        self.mode_toggle_btn = QPushButton("Prefer hours")  # checked => preferred mode
        for i, button in enumerate((self.block_btn, self.mode_toggle_btn)):
            button.setCheckable(True)
            button.setCursor(Qt.PointingHandCursor)
            button.setMinimumHeight(38)
            button.setMinimumWidth(150)
        group = QButtonGroup(self)
        group.setExclusive(True)
        group.addButton(self.block_btn)
        group.addButton(self.mode_toggle_btn)
        self.block_btn.setChecked(True)
        mode_row.addWidget(self.block_btn)
        mode_row.addWidget(self.mode_toggle_btn)
        mode_row.addSpacing(16)
        self.summary_label = QLabel("")
        mode_row.addWidget(self.summary_label)
        mode_row.addStretch(1)
        layout.addLayout(mode_row)

        # === Time slot table ===
        self.table = TimeConstraintTable()
        self.table.cell_toggled.connect(self.update_summary)

        if initial_forbidden:
            for row, col in initial_forbidden:
                self.table.set_forbidden_cell(row, col)

        if initial_preferred:
            for row, col in initial_preferred:
                self.table.set_preferred_cell(row, col)

        layout.addWidget(self.table, 1)

        # === Buttons ===
        btns = QHBoxLayout()
        btns.setSpacing(10)
        self.clear_all_btn = QPushButton("Clear all")
        self.clear_all_btn.setProperty("variant", "danger")
        self.clear_all_btn.setCursor(Qt.PointingHandCursor)
        self.cancel_btn = QPushButton("Cancel")
        self.cancel_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn = QPushButton("Save preferences")
        self.ok_btn.setProperty("variant", "primary")
        self.ok_btn.setCursor(Qt.PointingHandCursor)
        self.ok_btn.setDefault(True)
        btns.addWidget(self.clear_all_btn)
        btns.addStretch(1)
        btns.addWidget(self.cancel_btn)
        btns.addWidget(self.ok_btn)
        layout.addLayout(btns)

        self.setLayout(layout)

        # === Connections ===
        self.clear_all_btn.clicked.connect(self._clear_all_constraints)
        self.ok_btn.clicked.connect(self.accept)
        self.cancel_btn.clicked.connect(self.reject)
        self.block_btn.clicked.connect(self.toggle_mode)
        self.mode_toggle_btn.clicked.connect(self.toggle_mode)

        self.update_summary()
        self.toggle_mode()  # apply default style

    def show_scoring_help(self):
        """Show help dialog explaining the preference scoring system"""
        help_dialog = QMessageBox(self)
        help_dialog.setWindowTitle("Preference Scoring Explanation")
        help_dialog.setIcon(QMessageBox.Information)
        
        help_text = """
<h3>📊 How Preference Scoring Works</h3>

<p><b>🎯 Simple Formula:</b><br>
Score = (Preferred slots used ÷ Total preferred slots) × 100</p>

<p><b>📋 What this means:</b><br>
• <span style="color: #4CAF50;"><b>100%</b></span> = All your preferred time slots have classes<br>
• <span style="color: #FF9800;"><b>50%</b></span> = Half of your preferred time slots have classes<br>
• <span style="color: #F44336;"><b>1%</b></span> = None of your preferred time slots have classes</p>

<p><b>🔴 Forbidden slots:</b> Prevent classes from being scheduled (no scoring impact)</p>

<p><b>🟢 Preferred slots:</b> Count towards your preference score when filled</p>

<p><b>⚪ Neutral slots:</b> Ignored in scoring (neither help nor hurt your score)</p>

<p><b>📈 Example:</b><br>
You mark 10 preferred slots → System schedules 7 classes in preferred slots → Score = 70%</p>
        """
        
        help_dialog.setText(help_text)
        help_dialog.setTextFormat(Qt.RichText)
        
        # Make dialog wider to accommodate the text
        help_dialog.setStyleSheet("QMessageBox { min-width: 500px; }")
        
        help_dialog.exec_()

    def _segment_style(self, active: bool, color: str, soft: str, left: bool) -> str:
        radius = ("border-top-left-radius: 10px; border-bottom-left-radius: 10px; "
                  "border-top-right-radius: 0; border-bottom-right-radius: 0;") if left else (
                  "border-top-right-radius: 10px; border-bottom-right-radius: 10px; "
                  "border-top-left-radius: 0; border-bottom-left-radius: 0;")
        if active:
            return f"QPushButton {{ background-color: {soft}; color: {color}; border: 1.5px solid {color}; {radius} }}"
        return (f"QPushButton {{ background-color: {PALETTE['surface']}; color: {PALETTE['text_muted']}; "
                f"border: 1px solid {PALETTE['border_strong']}; {radius} }}")

    def toggle_mode(self):
        """Switch between marking blocked (forbidden) and preferred hours."""
        preferred = self.mode_toggle_btn.isChecked()
        self.table.mark_mode = 'preferred' if preferred else 'forbidden'
        self.block_btn.setChecked(not preferred)
        self.block_btn.setStyleSheet(self._segment_style(not preferred, "#E11D48", "#FFE4E6", True))
        self.mode_toggle_btn.setStyleSheet(self._segment_style(preferred, PALETTE["success"], PALETTE["success_soft"], False))

    def _clear_all_constraints(self):
        """Clear all cell markings."""
        self.table.clear_constraints()
        self.update_summary()

    def update_summary(self):
        """Update the label showing how many cells are selected per type."""
        forbidden_count = len(self.table.forbidden)
        preferred_count = len(self.table.preferred)
        self.summary_label.setText(
            f"<span style='color:#E11D48'>●</span> {forbidden_count} blocked &nbsp;&nbsp; "
            f"<span style='color:{PALETTE['success']}'>●</span> {preferred_count} preferred")
        self.summary_label.setStyleSheet(f"color: {PALETTE['text_muted']}; font-weight: 600;")

    def get_forbidden(self):
        return set(self.table.forbidden)

    def get_preferred(self):
        return set(self.table.preferred)