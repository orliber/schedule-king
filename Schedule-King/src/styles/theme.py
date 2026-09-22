"""
Central design system for Schedule King.

All colours live in PALETTE and are injected into one application-wide
stylesheet, so components only need to set an objectName or a "variant"
property instead of carrying their own hard-coded CSS.
"""
import os
import sys
from typing import Optional, Tuple

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QFont, QIcon, QPainter, QPixmap

ASSETS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "assets")

PALETTE = {
    "bg": "#F4F6FB",
    "surface": "#FFFFFF",
    "surface_alt": "#F8FAFC",
    "border": "#E2E8F0",
    "border_strong": "#CBD5E1",
    "text": "#0F172A",
    "text_muted": "#64748B",
    "text_subtle": "#94A3B8",
    "primary": "#4F46E5",
    "primary_hover": "#4338CA",
    "primary_pressed": "#3730A3",
    "primary_soft": "#EEF2FF",
    "primary_soft_border": "#C7D2FE",
    "success": "#16A34A",
    "success_soft": "#DCFCE7",
    "danger": "#DC2626",
    "danger_hover": "#B91C1C",
    "danger_soft": "#FEF2F2",
    "warning": "#D97706",
    "warning_soft": "#FEF3C7",
    "gold": "#F59E0B",
}

# Distinct, readable course colours: (background, accent/border, text)
COURSE_COLORS = [
    ("#E0E7FF", "#4F46E5", "#312E81"),
    ("#DCFCE7", "#16A34A", "#14532D"),
    ("#FFE4E6", "#E11D48", "#881337"),
    ("#FEF3C7", "#D97706", "#78350F"),
    ("#E0F2FE", "#0284C7", "#0C4A6E"),
    ("#F3E8FF", "#9333EA", "#581C87"),
    ("#CCFBF1", "#0D9488", "#134E4A"),
    ("#FFEDD5", "#EA580C", "#7C2D12"),
]


def course_color(index: int) -> Tuple[str, str, str]:
    """Return the (background, accent, text) colours for the n-th course."""
    return COURSE_COLORS[index % len(COURSE_COLORS)]


def asset_path(name: str) -> str:
    return os.path.join(ASSETS_DIR, name)


def load_icon(name: str, size: Tuple[int, int] = (24, 24), color: Optional[str] = None) -> QIcon:
    """
    Load an icon from the assets folder, scaled and optionally tinted.
    Returns an empty QIcon when the file is missing or unreadable.
    """
    path = asset_path(name)
    if not os.path.exists(path):
        return QIcon()
    pixmap = QPixmap(path)
    if pixmap.isNull():
        return QIcon()
    pixmap = pixmap.scaled(size[0], size[1], Qt.KeepAspectRatio, Qt.SmoothTransformation)
    if color:
        tinted = QPixmap(pixmap.size())
        tinted.fill(Qt.transparent)
        painter = QPainter(tinted)
        painter.drawPixmap(0, 0, pixmap)
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(tinted.rect(), QColor(color))
        painter.end()
        pixmap = tinted
    return QIcon(pixmap)


def set_variant(widget, variant: str):
    """Switch a widget's style variant (e.g. primary/danger) and re-polish it."""
    widget.setProperty("variant", variant)
    repolish(widget)


def repolish(widget):
    """Re-apply the stylesheet after a dynamic property changed."""
    style = widget.style()
    style.unpolish(widget)
    style.polish(widget)


def default_font() -> QFont:
    if sys.platform == "win32":
        font = QFont("Segoe UI")
    elif sys.platform == "darwin":
        font = QFont(".AppleSystemUIFont")
    else:
        font = QFont("Ubuntu")
        font.setStyleHint(QFont.SansSerif)
    font.setPointSize(13 if sys.platform == "darwin" else 10)
    return font


STYLESHEET = """
/* ---------- Base ---------- */
QWidget {{
    color: {text};
    font-size: 14px;
}}
QMainWindow, QDialog {{
    background-color: {bg};
}}
QToolTip {{
    background-color: {text};
    color: #FFFFFF;
    border: none;
    padding: 6px 8px;
    border-radius: 6px;
}}
QLabel {{
    background: transparent;
}}

/* ---------- Buttons ---------- */
QPushButton {{
    background-color: {surface};
    color: {text};
    border: 1px solid {border_strong};
    border-radius: 10px;
    padding: 9px 18px;
    font-weight: 600;
}}
QPushButton:hover {{
    background-color: {surface_alt};
    border-color: {text_subtle};
}}
QPushButton:pressed {{
    background-color: {border};
}}
QPushButton:disabled {{
    color: {text_subtle};
    background-color: {surface_alt};
    border-color: {border};
}}
QPushButton[variant="primary"] {{
    background-color: {primary};
    color: #FFFFFF;
    border: 1px solid {primary};
}}
QPushButton[variant="primary"]:hover {{
    background-color: {primary_hover};
    border-color: {primary_hover};
}}
QPushButton[variant="primary"]:pressed {{
    background-color: {primary_pressed};
}}
QPushButton[variant="primary"]:disabled {{
    background-color: {primary_soft_border};
    border-color: {primary_soft_border};
    color: #FFFFFF;
}}
QPushButton[variant="danger"] {{
    background-color: {surface};
    color: {danger};
    border: 1px solid #FECACA;
}}
QPushButton[variant="danger"]:hover {{
    background-color: {danger_soft};
    border-color: {danger};
}}
QPushButton[variant="ghost"] {{
    background-color: transparent;
    border: 1px solid transparent;
    color: {text_muted};
}}
QPushButton[variant="ghost"]:hover {{
    background-color: {primary_soft};
    color: {primary};
}}
QPushButton[variant="icon"] {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 0;
}}
QPushButton[variant="icon"]:hover {{
    background-color: {primary_soft};
    border-color: {primary_soft_border};
}}
QPushButton[variant="icon"]:disabled {{
    background-color: {surface_alt};
}}

/* ---------- Inputs ---------- */
QLineEdit, QComboBox, QSpinBox, QTimeEdit {{
    background-color: {surface};
    border: 1px solid {border_strong};
    border-radius: 10px;
    padding: 8px 12px;
    selection-background-color: {primary_soft_border};
    selection-color: {text};
}}
QLineEdit:focus, QComboBox:focus, QSpinBox:focus, QTimeEdit:focus {{
    border: 2px solid {primary};
    padding: 7px 11px;
}}
QComboBox::drop-down {{
    border: none;
    width: 28px;
}}
QComboBox::down-arrow {{
    image: url("{assets}/chevron-down.png");
    width: 14px;
    height: 14px;
}}
QComboBox QAbstractItemView {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 4px;
    outline: none;
    selection-background-color: {primary_soft};
    selection-color: {primary};
}}
QCheckBox {{
    spacing: 8px;
    color: {text_muted};
}}
QCheckBox::indicator {{
    width: 18px;
    height: 18px;
    border-radius: 5px;
    border: 1px solid {border_strong};
    background: {surface};
}}
QCheckBox::indicator:checked {{
    background: {primary};
    border-color: {primary};
}}

/* ---------- Scroll bars ---------- */
QScrollBar:vertical {{
    background: transparent;
    width: 10px;
    margin: 4px 2px;
}}
QScrollBar::handle:vertical {{
    background: {border_strong};
    border-radius: 3px;
    min-height: 32px;
}}
QScrollBar::handle:vertical:hover {{
    background: {text_subtle};
}}
QScrollBar:horizontal {{
    background: transparent;
    height: 10px;
    margin: 2px 4px;
}}
QScrollBar::handle:horizontal {{
    background: {border_strong};
    border-radius: 3px;
    min-width: 32px;
}}
QScrollBar::add-line, QScrollBar::sub-line, QScrollBar::add-page, QScrollBar::sub-page {{
    background: none;
    border: none;
    width: 0;
    height: 0;
}}

/* ---------- Cards & typography ---------- */
QFrame#card, QWidget#card {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 16px;
}}
QLabel#app_title {{
    font-size: 26px;
    font-weight: 800;
    color: {text};
}}
QLabel#app_subtitle {{
    font-size: 14px;
    color: {text_muted};
}}
QLabel#section_title {{
    font-size: 16px;
    font-weight: 700;
    color: {text};
}}
QLabel#muted {{
    color: {text_muted};
}}
QLabel#badge {{
    background-color: {primary_soft};
    color: {primary};
    border-radius: 10px;
    padding: 3px 10px;
    font-size: 12px;
    font-weight: 700;
}}
QLabel#badge[state="warning"] {{
    background-color: {warning_soft};
    color: {warning};
}}
QLabel#badge[state="success"] {{
    background-color: {success_soft};
    color: {success};
}}

/* ---------- Course list ---------- */
QListWidget#course_list_widget {{
    background-color: transparent;
    border: none;
    outline: none;
}}
QListWidget#course_list_widget::item {{
    border: none;
    background: transparent;
}}

/* ---------- Tables ---------- */
QTableView, QTableWidget {{
    background-color: {surface};
    alternate-background-color: {surface_alt};
    border: 1px solid {border};
    border-radius: 14px;
    gridline-color: {border};
    selection-background-color: {primary_soft};
    selection-color: {text};
}}
QHeaderView {{
    background-color: transparent;
}}
QHeaderView::section {{
    background-color: {surface};
    color: {text_muted};
    border: none;
    border-bottom: 1px solid {border};
    padding: 8px;
    font-weight: 700;
    font-size: 13px;
}}
QHeaderView::section:vertical {{
    border-bottom: none;
    border-right: 1px solid {border};
    font-weight: 600;
    font-size: 12px;
}}
QTableCornerButton::section {{
    background-color: {surface};
    border: none;
}}

/* ---------- Schedule window ---------- */
QLabel#headline_label {{
    font-size: 24px;
    font-weight: 800;
    color: {text};
}}
QLabel#subtitle_label {{
    font-size: 13px;
    color: {text_muted};
}}
QWidget#title_container {{
    background: transparent;
}}
QWidget#toolbar_card {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 14px;
}}
QLabel#info_label {{
    font-size: 12px;
    color: {text_muted};
    font-weight: 600;
}}
QLineEdit#schedule_num {{
    font-size: 16px;
    font-weight: 700;
    color: {primary};
    min-width: 64px;
    max-width: 90px;
}}
QPushButton#nav_button {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 0;
}}
QPushButton#nav_button:hover {{
    background-color: {primary_soft};
    border-color: {primary_soft_border};
}}
QPushButton#nav_button:disabled {{
    background-color: {surface_alt};
    border-color: {border};
}}
QPushButton#export_calendar_button {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 10px;
    padding: 0;
}}
QPushButton#export_calendar_button:hover {{
    background-color: {primary_soft};
    border-color: {primary_soft_border};
}}
QLabel#ranking_label {{
    color: {text_muted};
    font-weight: 600;
}}
QComboBox#metric_selector {{
    min-width: 170px;
}}
QPushButton#sort_order_button {{
    background-color: {surface};
    border: 1px solid {border_strong};
    border-radius: 10px;
    padding: 0;
}}
QPushButton#sort_order_button:hover {{
    background-color: {primary_soft};
}}
QFrame#metric_tile {{
    background-color: {surface};
    border: 1px solid {border};
    border-radius: 14px;
}}
QLabel#metric_value {{
    font-size: 20px;
    font-weight: 800;
    color: {text};
}}
QLabel#metric_name {{
    font-size: 11px;
    font-weight: 600;
    color: {text_muted};
}}
QProgressBar#schedule_progress {{
    background-color: {primary_soft};
    border: none;
    border-radius: 5px;
    height: 10px;
    text-align: center;
    color: {primary};
    font-size: 11px;
    font-weight: 700;
}}
QProgressBar#schedule_progress::chunk {{
    background-color: {primary};
    border-radius: 5px;
}}
QLabel#progress_label {{
    color: {primary};
    font-size: 12px;
    font-weight: 700;
}}
QWidget#legend_item {{
    background: transparent;
}}

/* ---------- Dialogs ---------- */
QMessageBox QLabel {{
    color: {text};
    font-size: 14px;
}}
QMessageBox QPushButton, QDialogButtonBox QPushButton {{
    min-width: 88px;
}}
QProgressDialog QLabel {{
    color: {text};
}}
"""


def build_stylesheet() -> str:
    assets = ASSETS_DIR.replace("\\", "/")
    return STYLESHEET.format(assets=assets, **PALETTE)


def apply_theme(app):
    """Apply the Schedule King look to the whole application."""
    app.setStyle("Fusion")
    app.setFont(default_font())
    app.setStyleSheet(build_stylesheet())
