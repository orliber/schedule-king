from PyQt5.QtWidgets import (
    QListWidget, QAbstractItemView, QListWidgetItem, QVBoxLayout, QWidget, QSizePolicy,
    QComboBox, QToolTip, QStyledItemDelegate, QStyle
)
from PyQt5.QtCore import pyqtSignal, Qt, QEvent, QTimer, QRectF, QSize
from PyQt5.QtGui import QFont, QCursor, QColor, QPainter, QPainterPath, QPen, QFontMetrics
from typing import List, Dict, Optional, Set
from src.models.course import Course
from src.styles.theme import PALETTE


class CourseItemDelegate(QStyledItemDelegate):
    """Paints each course as a rounded card with a code pill and a selection check."""

    ROW_HEIGHT = 62

    def __init__(self, course_lookup, parent=None):
        super().__init__(parent)
        self._course_lookup = course_lookup

    def sizeHint(self, option, index):
        return QSize(option.rect.width(), self.ROW_HEIGHT)

    def paint(self, painter: QPainter, option, index):
        painter.save()
        painter.setRenderHint(QPainter.Antialiasing)
        selected = bool(option.state & QStyle.State_Selected)
        hovered = bool(option.state & QStyle.State_MouseOver)
        rect = QRectF(option.rect).adjusted(2, 2, -2, -2)

        if selected:
            bg, border = QColor(PALETTE["primary_soft"]), QColor(PALETTE["primary"])
        elif hovered:
            bg, border = QColor(PALETTE["surface_alt"]), QColor(PALETTE["border_strong"])
        else:
            bg, border = QColor(PALETTE["surface"]), QColor(PALETTE["border"])
        path = QPainterPath()
        path.addRoundedRect(rect, 12, 12)
        painter.fillPath(path, bg)
        painter.setPen(QPen(border, 1.5 if selected else 1))
        painter.drawPath(path)

        code = index.data(Qt.UserRole) or ""
        course = self._course_lookup().get(code)
        name = course.name if course else index.data(Qt.DisplayRole)
        subtitle = ""
        if course is not None:
            parts = []
            if course.is_detailed and course.instructor:
                parts.append(course.instructor)
            if course.category and course.category != "default":
                parts.append(course.category)
            subtitle = "  ·  ".join(parts)

        # Code pill
        base_font = QFont(option.font)
        pill_font = QFont(base_font)
        pill_font.setBold(True)
        pill_font.setPointSizeF(max(base_font.pointSizeF() - 1, 8))
        fm = QFontMetrics(pill_font)
        pill_w = max(fm.horizontalAdvance(code) + 20, 64)
        pill = QRectF(rect.left() + 12, rect.center().y() - 12, pill_w, 24)
        pill_path = QPainterPath()
        pill_path.addRoundedRect(pill, 8, 8)
        painter.fillPath(pill_path, QColor(PALETTE["primary"] if selected else PALETTE["primary_soft"]))
        painter.setFont(pill_font)
        painter.setPen(QColor("#FFFFFF" if selected else PALETTE["primary"]))
        painter.drawText(pill, Qt.AlignCenter, code)

        # Name + subtitle
        text_left = pill.right() + 14
        text_rect = QRectF(text_left, rect.top(), rect.right() - text_left - 48, rect.height())
        name_font = QFont(base_font)
        name_font.setWeight(QFont.DemiBold)
        painter.setFont(name_font)
        painter.setPen(QColor(PALETTE["text"]))
        name_fm = QFontMetrics(name_font)
        if subtitle:
            painter.drawText(text_rect.adjusted(0, 6, 0, -rect.height() / 2 + 1), Qt.AlignLeft | Qt.AlignBottom,
                             name_fm.elidedText(name, Qt.ElideRight, int(text_rect.width())))
            sub_font = QFont(base_font)
            sub_font.setPointSizeF(max(base_font.pointSizeF() - 1, 8))
            painter.setFont(sub_font)
            painter.setPen(QColor(PALETTE["text_muted"]))
            painter.drawText(text_rect.adjusted(0, rect.height() / 2 + 3, 0, 0), Qt.AlignLeft | Qt.AlignTop,
                             QFontMetrics(sub_font).elidedText(subtitle, Qt.ElideRight, int(text_rect.width())))
        else:
            painter.drawText(text_rect, Qt.AlignLeft | Qt.AlignVCenter,
                             name_fm.elidedText(name, Qt.ElideRight, int(text_rect.width())))

        # Selection check circle
        circle = QRectF(rect.right() - 36, rect.center().y() - 11, 22, 22)
        if selected:
            painter.setPen(Qt.NoPen)
            painter.setBrush(QColor(PALETTE["primary"]))
            painter.drawEllipse(circle)
            pen = QPen(QColor("#FFFFFF"), 2.2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            c = circle.center()
            painter.drawLine(int(c.x() - 5), int(c.y()), int(c.x() - 1), int(c.y() + 4))
            painter.drawLine(int(c.x() - 1), int(c.y() + 4), int(c.x() + 6), int(c.y() - 4))
        else:
            painter.setBrush(Qt.NoBrush)
            painter.setPen(QPen(QColor(PALETTE["border_strong"]), 1.5))
            painter.drawEllipse(circle)
        painter.restore()

class CourseListWidget(QListWidget):
    tooltipRequested = pyqtSignal(Course)  # Changed from str to Course

    def __init__(self, parent=None):
        super().__init__(parent)
        self.viewport().installEventFilter(self)
        self.setMouseTracking(True)
        self.viewport().setAttribute(Qt.WA_Hover, True)
        # Cache for course lookup
        self._course_cache: Dict[str, Course] = {}

    def set_course_cache(self, course_cache: Dict[str, Course]):
        """Set the course cache for efficient lookups."""
        self._course_cache = course_cache

    def eventFilter(self, obj, event):
        if obj is self.viewport() and event.type() == QEvent.ToolTip:
            item = self.itemAt(event.pos())
            if item:
                course_code = item.data(Qt.UserRole)
                if course_code and course_code in self._course_cache:
                    course = self._course_cache[course_code]
                    if not course.is_detailed:
                        self.tooltipRequested.emit(course)
            return False
        return super().eventFilter(obj, event)

class CourseList(QWidget):
    selectionChanged = pyqtSignal(list)
    tooltipRequested = pyqtSignal(Course)  # Changed from str to Course

    def __init__(self, parent=None):
        super().__init__(parent)
        self.courses: List[Course] = []
        self.filtered_courses: List[Course] = []
        self.selected_course_codes: Set[str] = set()
        # Cache for performance
        self._course_lookup: Dict[str, Course] = {}
        self._item_lookup: Dict[str, QListWidgetItem] = {}
        self._categories_cache: List[str] = []
        self._setup_ui()
        self._connect_signals()

    def _setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(10)
        self.category_filter = QComboBox()
        self.category_filter.setObjectName("category_filter")
        self.category_filter.addItem("All Categories")
        layout.addWidget(self.category_filter)
        self.list_widget = CourseListWidget()
        self.list_widget.setObjectName("course_list_widget")
        self._configure_list_widget()
        layout.addWidget(self.list_widget)

    def _configure_list_widget(self):
        self.list_widget.setSelectionMode(QAbstractItemView.MultiSelection)
        self.list_widget.setUniformItemSizes(True)
        self.list_widget.setSpacing(3)
        self.list_widget.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.list_widget.setVerticalScrollMode(QAbstractItemView.ScrollPerPixel)
        self.list_widget.setItemDelegate(CourseItemDelegate(lambda: self._course_lookup, self.list_widget))

    def _connect_signals(self):
        self.category_filter.currentIndexChanged.connect(self._apply_filters)
        self.list_widget.itemSelectionChanged.connect(self._handle_selection_changed)
        self.list_widget.tooltipRequested.connect(self.tooltipRequested)

    def populate_courses(self, courses: List[Course]):
        self.courses = courses
        self.filtered_courses = courses
        self.selected_course_codes.clear()
        self._course_lookup = {course.course_code: course for course in courses}
        self._item_lookup.clear()
        self.list_widget.set_course_cache(self._course_lookup)
        self._update_category_filter(courses)
        self._update_course_list(courses)

    def _update_category_filter(self, courses: List[Course]):
        new_categories = sorted(set(course.category for course in courses))
        if new_categories != self._categories_cache:
            self._categories_cache = new_categories
            self.category_filter.blockSignals(True)
            self.category_filter.clear()
            self.category_filter.addItem("All Categories")
            self.category_filter.addItems(new_categories)
            self.category_filter.blockSignals(False)

    def _update_course_list(self, course_list: List[Course]):
        self.list_widget.blockSignals(True)
        self.list_widget.clear()
        self._item_lookup.clear()
        filtered_lookup = {course.course_code: course for course in course_list}
        self.list_widget.set_course_cache(filtered_lookup)
        items_to_select = []
        for course in course_list:
            item = self._create_course_item(course)
            self.list_widget.addItem(item)
            self._item_lookup[course.course_code] = item
            if course.course_code in self.selected_course_codes:
                items_to_select.append(item)
        for item in items_to_select:
            item.setSelected(True)
        self.list_widget.blockSignals(False)

    def _create_course_item(self, course: Course) -> QListWidgetItem:
        item = QListWidgetItem(f"{course.course_code} - {course.name}")
        item.setData(Qt.UserRole, course.course_code)
        tooltip_text = self._generate_tooltip_text(course)
        item.setToolTip(tooltip_text)
        return item

    def _generate_tooltip_text(self, course: Course) -> str:
        if not course.is_detailed:
            return f"<b>{course.course_code}</b>: {course.name}<br>Loading ..."
        details = [
            f"<b>{course.course_code}</b>: {course.name}",
            f"Category: {course.category}",
            f"Instructor: {course.instructor}",
            (f"Lectures: {sum(1 for lec in course.lectures if lec)} | "
            f"Tirguls: {sum(1 for tir in course.tirguls if tir)} | "
            f"Labs: {sum(1 for lab in course.maabadas if lab)}"),
        ]
        self._format_slot_groups(course.lectures, "Lecture", "#1976D2", details)
        self._format_slot_groups(course.tirguls, "Tirgul", "#FF9800", details)
        self._format_slot_groups(course.maabadas, "Maabada", "#4CAF50", details)
        return "<br>".join(details)

    def _format_slot_groups(self, slot_groups, label: str, color: str, details: List[str]):
        for group in slot_groups:
            if not group:
                continue
            details.append(f"<span style='color:{color}'>\u25A0 {label}:</span>")
            if isinstance(group, list):
                for slot in group:
                    details.append(f"&nbsp;&nbsp;&bull; {slot}")
            else:
                details.append(f"&nbsp;&nbsp;&bull; {group}")

    def _handle_selection_changed(self):
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            code = item.data(Qt.UserRole)
            if item.isSelected():
                self.selected_course_codes.add(code)
            else:
                self.selected_course_codes.discard(code)
        selected_courses = [
            self._course_lookup[code] 
            for code in self.selected_course_codes 
            if code in self._course_lookup
        ]
        self.selectionChanged.emit(selected_courses)

    def get_selected_courses(self) -> List[Course]:
        return [
            self._course_lookup[code] 
            for code in self.selected_course_codes 
            if code in self._course_lookup
        ]

    def deselect_course(self, course_code: str):
        """Remove a single course from the selection, even if it is filtered out of view."""
        self.selected_course_codes.discard(course_code)
        item = self._item_lookup.get(course_code)
        if item is not None:
            self.list_widget.blockSignals(True)
            item.setSelected(False)
            self.list_widget.blockSignals(False)
        self.selectionChanged.emit(self.get_selected_courses())

    def clear_selection(self):
        self.list_widget.clearSelection()
        self.selected_course_codes.clear()
        self.selectionChanged.emit([])

    def filter_courses(self, text: str):
        text = text.strip().lower()
        selected_category = self.category_filter.currentText()
        self.filtered_courses = [
            course for course in self.courses
            if self._matches_filter(course, text, selected_category)
        ]
        self._update_course_list(self.filtered_courses)
        self._handle_selection_changed()

    def _matches_filter(self, course: Course, text: str, category: str) -> bool:
        text_match = (not text or 
                     text in course.name.lower() or 
                     text in course.course_code.lower())
        category_match = (category == "All Categories" or 
                         course.category == category)
        return text_match and category_match

    def _apply_filters(self):
        self.filter_courses("")

    def update_course_tooltip(self, course: Course):
        item = self._item_lookup.get(course.course_code)
        if not item:
            return
        tooltip_text = self._generate_tooltip_text(course)
        item.setToolTip(tooltip_text)
        if self._is_mouse_over_item(item):
            self._refresh_tooltip(tooltip_text)

    def _is_mouse_over_item(self, item: QListWidgetItem) -> bool:
        current_pos = self.list_widget.mapFromGlobal(QCursor.pos())
        hovered_item = self.list_widget.itemAt(current_pos)
        return hovered_item is item

    def _refresh_tooltip(self, tooltip_text: str):
        QToolTip.hideText()
        QTimer.singleShot(50, lambda: QToolTip.showText(QCursor.pos(), tooltip_text, self.list_widget))