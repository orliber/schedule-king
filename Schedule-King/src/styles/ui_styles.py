"""
Small inline style helpers kept for components that still style labels directly.
Colours come from the central palette in src/styles/theme.py.
"""
from src.styles.theme import PALETTE as P


def _button(bg, hover, pressed, fg="#FFFFFF", border=None):
    border = border or bg
    return f"""
        QPushButton {{
            background-color: {bg};
            color: {fg};
            border: 1px solid {border};
            border-radius: 10px;
            padding: 9px 18px;
            font-weight: 600;
        }}
        QPushButton:hover {{ background-color: {hover}; }}
        QPushButton:pressed {{ background-color: {pressed}; }}
    """


def red_button_style():
    """Destructive action (Clear, Delete)."""
    return _button(P["surface"], P["danger_soft"], "#FEE2E2", fg=P["danger"], border="#FECACA")


def green_button_style():
    """Main call to action (Generate, Confirm)."""
    return _button(P["primary"], P["primary_hover"], P["primary_pressed"])


def blue_button_style():
    """Secondary action (Load, Info)."""
    return _button(P["surface"], P["surface_alt"], P["border"], fg=P["text"], border=P["border_strong"])


def disabled_button_style():
    return _button(P["primary_soft_border"], P["primary_soft_border"], P["primary_soft_border"])


def title_label_style():
    return f"QLabel {{ color: {P['text']}; font-size: 18px; font-weight: 700; }}"


def warning_label_style():
    return f"color: {P['warning']}; font-size: 12px; font-weight: 600;"


def success_label_style():
    return f"color: {P['text_muted']}; font-size: 12px; font-weight: 600;"


def instruction_label_style():
    return f"color: {P['text_muted']}; font-size: 13px;"


def footer_label_style():
    return f"color: {P['text_subtle']}; font-size: 12px;"


def headline_label_style():
    return f"QLabel {{ color: {P['text']}; font-size: 24px; font-weight: 800; }}"


def subtitle_label_style():
    return f"QLabel {{ color: {P['text_muted']}; font-size: 14px; }}"


def course_selector_background():
    return ""


def schedule_background():
    return f"background-color: {P['bg']};"


def table_cell_style(event_class, bg_color, border_color, is_start=False, is_end=False):
    """Generate table cell style for schedule events."""
    radius = ""
    if is_start:
        radius += "border-top-left-radius: 8px; border-top-right-radius: 8px;"
    if is_end:
        radius += "border-bottom-left-radius: 8px; border-bottom-right-radius: 8px;"
    return f"""
        QLabel {{
            background-color: {bg_color};
            border-left: 4px solid {border_color};
            {radius}
            padding: 3px;
        }}
    """
