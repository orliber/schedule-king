from PyQt5.QtWidgets import QFrame, QHBoxLayout, QVBoxLayout, QLabel
from PyQt5.QtCore import Qt
from src.models.schedule import Schedule


class ScheduleMetrics(QFrame):
    """A row of stat tiles summarising the displayed schedule."""

    METRICS = [
        ("active_days_label", "ACTIVE DAYS"),
        ("gap_count_label", "GAPS"),
        ("total_gap_time_label", "GAP HOURS"),
        ("avg_start_time_label", "AVG. START"),
        ("avg_end_time_label", "AVG. END"),
        ("preference_score_label", "PREFERENCE MATCH"),
    ]

    def __init__(self, schedule: Schedule, parent=None):
        super().__init__(parent)
        self.schedule = schedule
        self.setObjectName("ScheduleMetrics")
        self._values = {}
        self.init_ui()
        self.set_schedule(schedule)

    def init_ui(self):
        layout = QHBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(12)
        for obj_name, title in self.METRICS:
            tile = QFrame()
            tile.setObjectName("metric_tile")
            tile_layout = QVBoxLayout(tile)
            tile_layout.setContentsMargins(16, 10, 16, 10)
            tile_layout.setSpacing(2)
            name = QLabel(title)
            name.setObjectName("metric_name")
            value = QLabel("-")
            value.setObjectName("metric_value")
            value.setProperty("metric", obj_name)
            tile_layout.addWidget(name)
            tile_layout.addWidget(value)
            layout.addWidget(tile, 1)
            self._values[obj_name] = value

    def set_schedule(self, schedule: Schedule):
        """Refresh all tiles for a new schedule."""
        self.schedule = schedule
        try:
            values = {
                "active_days_label": str(schedule.active_days),
                "gap_count_label": str(schedule.gap_count),
                "total_gap_time_label": str(schedule.total_gap_time),
                "avg_start_time_label": self._format_time(schedule.avg_start_time),
                "avg_end_time_label": self._format_time(schedule.avg_end_time),
                "preference_score_label": f"{schedule.preference_score}%",
            }
        except Exception:
            values = {}
        for obj_name, label in self._values.items():
            label.setText(values.get(obj_name, "-"))

    def _format_time(self, time_value: float) -> str:
        """Format time from integer format (e.g., 900) to HH:MM."""
        if time_value == 0:
            return "N/A"
        total_minutes = Schedule.time_format_to_minutes(int(time_value))
        return f"{total_minutes // 60:02}:{total_minutes % 60:02}"
