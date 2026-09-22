from PyQt5.QtWidgets import QTableWidget, QHeaderView, QLabel, QWidget, QHBoxLayout, QTableWidgetItem, QSizePolicy
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor
from src.models.schedule import Schedule
from src.styles.theme import PALETTE, course_color

DAY_NAMES = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday"]
FIRST_HOUR = 8
LAST_HOUR = 20


def _event_class(event: str) -> str:
    if "Lecture" in event:
        return "Lecture"
    if "Maabada" in event or "Mabada" in event:
        return "Maabada"
    return "Tirgul"


EVENT_LABELS = {"Lecture": "LECTURE", "Tirgul": "TIRGUL", "Maabada": "LAB"}


class ScheduleTable(QTableWidget):
    """
    Weekly timetable: days as columns, hours as rows.

    Every course gets its own colour (shared with the legend), and multi-hour
    events are drawn as one continuous block across their rows.
    """
    MIN_ROW_HEIGHT = 46

    def __init__(self):
        super().__init__()
        self.current_schedule = None
        self.legend_entries = []  # [(code, name, (bg, accent, text))] for the last displayed schedule

        self.setColumnCount(len(DAY_NAMES))
        self.setHorizontalHeaderLabels(DAY_NAMES)
        self.setRowCount(LAST_HOUR - FIRST_HOUR)
        self.setVerticalHeaderLabels([f"{hour:02d}:00" for hour in range(FIRST_HOUR, LAST_HOUR)])
        self.setWordWrap(True)

        self.setShowGrid(False)
        self.setAlternatingRowColors(True)
        self.setFocusPolicy(Qt.NoFocus)

        header = self.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.Stretch)
        header.setDefaultAlignment(Qt.AlignCenter)
        header.setFixedHeight(44)
        header.setHighlightSections(False)

        vertical_header = self.verticalHeader()
        vertical_header.setSectionResizeMode(QHeaderView.Stretch)
        vertical_header.setMinimumSectionSize(self.MIN_ROW_HEIGHT)
        vertical_header.setDefaultAlignment(Qt.AlignRight | Qt.AlignTop)
        vertical_header.setFixedWidth(72)
        vertical_header.setHighlightSections(False)

        self.setSelectionMode(QTableWidget.NoSelection)
        self.setEditTriggers(QTableWidget.NoEditTriggers)
        self.setMinimumSize(760, 420)

        # Kept for backwards compatibility with code that reads per-type colours
        self.event_colors = {
            "Lecture": QColor(course_color(0)[0]),
            "Tirgul": QColor(course_color(3)[0]),
            "Maabada": QColor(course_color(1)[0]),
        }

    def _assign_colors(self, day_map):
        codes = {}
        for events in day_map.values():
            for _, course_name, code, _ in events:
                codes.setdefault(str(code), course_name)
        ordered = sorted(codes)
        colors = {code: course_color(i) for i, code in enumerate(ordered)}
        self.legend_entries = [(code, codes[code], colors[code]) for code in ordered]
        return colors

    def display_schedule(self, schedule: Schedule):
        """Populate the table with a schedule's events."""
        if self.current_schedule == schedule:
            return
        self.current_schedule = schedule
        self.clearContents()

        day_map = schedule.extract_by_day()
        colors = self._assign_colors(day_map)

        for day_str, events in day_map.items():
            day = int(day_str) - 1
            for event, course_name, code, slot in events:
                start_row = slot.start_time.hour - FIRST_HOUR
                end_row = slot.end_time.hour - FIRST_HOUR
                event_class = _event_class(event)
                bg, accent, text = colors[str(code)]
                tooltip = (f"{course_name} ({code}) - {event_class}\n"
                           f"{slot.start_time.strftime('%H:%M')}-{slot.end_time.strftime('%H:%M')}\n"
                           f"Room: {slot.room} | Building: {slot.building}")

                for row in range(start_row, end_row):
                    is_first, is_last = row == start_row, row == end_row - 1
                    item = QTableWidgetItem()
                    item.setToolTip(tooltip)
                    self.setItem(row, day, item)

                    kind = EVENT_LABELS[event_class]
                    hours = f'{slot.start_time.strftime("%H:%M")}–{slot.end_time.strftime("%H:%M")}'
                    where = f"Room: {slot.room} | Building: {slot.building}"
                    if is_first:
                        details = where if end_row - start_row > 1 else f'<b style="color:{accent};">{kind}</b> · {where}'
                        html = (
                            f'<div style="white-space:nowrap; font-size:13px; font-weight:700; color:{text};">'
                            f'{course_name} ({code})</div>'
                            f'<div style="white-space:nowrap; font-size:11px; color:{text};">{details}</div>'
                        )
                    elif row == start_row + 1:
                        html = (
                            f'<div style="white-space:nowrap; font-size:11px; color:{text};">'
                            f'<b style="color:{accent};">{kind}</b> · {hours}</div>'
                            f'<div style="white-space:nowrap; font-size:10px; color:{accent};">{course_name} (continued)</div>'
                        )
                    else:
                        html = f'<div style="white-space:nowrap; font-size:10px; color:{accent};">{course_name} (continued)</div>'

                    label = QLabel(html)
                    label.setObjectName(f"course_label_{event_class}")
                    label.setAlignment(Qt.AlignLeft | Qt.AlignTop)
                    label.setWordWrap(True)
                    label.setSizePolicy(QSizePolicy.Ignored, QSizePolicy.Ignored)
                    label.setToolTip(tooltip)

                    radius = ""
                    if is_first:
                        radius += "border-top-left-radius: 8px; border-top-right-radius: 8px; margin-top: 3px;"
                    if is_last:
                        radius += "border-bottom-left-radius: 8px; border-bottom-right-radius: 8px; margin-bottom: 3px;"
                    label.setStyleSheet(f"""
                        QLabel {{
                            background-color: {bg};
                            border-left: 4px solid {accent};
                            {radius}
                            margin-left: 4px;
                            margin-right: 4px;
                            padding: 3px 8px;
                        }}
                    """)
                    self.setCellWidget(row, day, label)


class ScheduleLegend(QWidget):
    """Row of colour chips mapping each course colour to its name."""

    def __init__(self, parent=None):
        super().__init__(parent)
        self._layout = QHBoxLayout(self)
        self._layout.setContentsMargins(4, 0, 4, 0)
        self._layout.setSpacing(8)

    def set_entries(self, entries):
        while self._layout.count():
            item = self._layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()
        for code, name, (bg, accent, text) in entries:
            muted = PALETTE["text_muted"]
            chip = QLabel(f"<span style='color:{accent}'>●</span>&nbsp; {name} &nbsp;<span style='color:{muted}'>{code}</span>")
            chip.setStyleSheet(f"""
                QLabel {{
                    background-color: {bg};
                    color: {text};
                    border: 1px solid {accent};
                    border-radius: 12px;
                    padding: 4px 12px;
                    font-size: 12px;
                    font-weight: 600;
                }}
            """)
            self._layout.addWidget(chip)
        self._layout.addStretch(1)
