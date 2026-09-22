"""
Crisp line icons drawn with QPainter (24x24 design grid, scaled to any size),
so the UI does not depend on raster assets that clash with the theme.
"""
from PyQt5.QtCore import Qt, QPointF, QRectF
from PyQt5.QtGui import QColor, QIcon, QPainter, QPainterPath, QPen, QPixmap


def _paths(name: str):
    """Return a list of (QPainterPath, filled) in 24x24 coordinates."""
    p = QPainterPath()
    extra = []
    if name == "back":
        p.moveTo(19, 12); p.lineTo(5, 12)
        p.moveTo(11, 6); p.lineTo(5, 12); p.lineTo(11, 18)
    elif name == "chevron_left":
        p.moveTo(15, 5); p.lineTo(8, 12); p.lineTo(15, 19)
    elif name == "chevron_right":
        p.moveTo(9, 5); p.lineTo(16, 12); p.lineTo(9, 19)
    elif name == "chevron_down":
        p.moveTo(6, 9); p.lineTo(12, 15); p.lineTo(18, 9)
    elif name == "refresh":
        p.arcMoveTo(QRectF(4, 4, 16, 16), 60)
        p.arcTo(QRectF(4, 4, 16, 16), 60, 270)
        p.moveTo(14.5, 3.5); p.lineTo(16.2, 5.2); p.lineTo(13.8, 7.2)
    elif name == "expand":
        p.moveTo(9, 4); p.lineTo(4, 4); p.lineTo(4, 9)
        p.moveTo(15, 4); p.lineTo(20, 4); p.lineTo(20, 9)
        p.moveTo(20, 15); p.lineTo(20, 20); p.lineTo(15, 20)
        p.moveTo(9, 20); p.lineTo(4, 20); p.lineTo(4, 15)
    elif name == "calendar":
        p.addRoundedRect(QRectF(3.5, 5, 17, 15.5), 2.5, 2.5)
        p.moveTo(3.5, 10); p.lineTo(20.5, 10)
        p.moveTo(8, 3); p.lineTo(8, 7)
        p.moveTo(16, 3); p.lineTo(16, 7)
        p.moveTo(12, 12.5); p.lineTo(12, 18)
        p.moveTo(9.25, 15.25); p.lineTo(14.75, 15.25)
    elif name == "download":
        p.moveTo(12, 4); p.lineTo(12, 15)
        p.moveTo(7, 10); p.lineTo(12, 15); p.lineTo(17, 10)
        p.moveTo(4, 17); p.lineTo(4, 20); p.lineTo(20, 20); p.lineTo(20, 17)
    elif name == "upload":
        p.moveTo(12, 15); p.lineTo(12, 4)
        p.moveTo(7, 9); p.lineTo(12, 4); p.lineTo(17, 9)
        p.moveTo(4, 17); p.lineTo(4, 20); p.lineTo(20, 20); p.lineTo(20, 17)
    elif name == "clock":
        p.addEllipse(QRectF(3.5, 3.5, 17, 17))
        p.moveTo(12, 7.5); p.lineTo(12, 12); p.lineTo(15, 14)
    elif name == "trash":
        p.moveTo(4, 7); p.lineTo(20, 7)
        p.moveTo(9.5, 7); p.lineTo(9.5, 4.5); p.lineTo(14.5, 4.5); p.lineTo(14.5, 7)
        p.moveTo(6, 7); p.lineTo(7, 20); p.lineTo(17, 20); p.lineTo(18, 7)
    elif name == "sparkles":
        star = QPainterPath()
        star.moveTo(10, 3); star.quadTo(10.8, 9.2, 17, 10); star.quadTo(10.8, 10.8, 10, 17)
        star.quadTo(9.2, 10.8, 3, 10); star.quadTo(9.2, 9.2, 10, 3)
        small = QPainterPath()
        small.moveTo(18, 14); small.quadTo(18.4, 17.6, 21, 18); small.quadTo(18.4, 18.4, 18, 22)
        small.quadTo(17.6, 18.4, 15, 18); small.quadTo(17.6, 17.6, 18, 14)
        extra = [(star, True), (small, True)]
    elif name == "edit":
        p.moveTo(4, 20); p.lineTo(8, 19); p.lineTo(19, 8); p.lineTo(16, 5); p.lineTo(5, 16); p.closeSubpath()
        p.moveTo(14, 7); p.lineTo(17, 10)
    elif name == "folder":
        p.moveTo(3.5, 7); p.lineTo(3.5, 18.5); p.lineTo(20.5, 18.5); p.lineTo(20.5, 8.5)
        p.lineTo(12, 8.5); p.lineTo(10, 5.5); p.lineTo(3.5, 5.5); p.closeSubpath()
    elif name == "globe":
        p.addEllipse(QRectF(3.5, 3.5, 17, 17))
        p.addEllipse(QRectF(8.5, 3.5, 7, 17))
        p.moveTo(3.5, 12); p.lineTo(20.5, 12)
    elif name == "sort":
        p.moveTo(8, 4); p.lineTo(8, 20)
        p.moveTo(4.5, 16.5); p.lineTo(8, 20); p.lineTo(11.5, 16.5)
        p.moveTo(16, 20); p.lineTo(16, 4)
        p.moveTo(12.5, 7.5); p.lineTo(16, 4); p.lineTo(19.5, 7.5)
    else:
        raise KeyError(name)
    return [(p, False)] + extra


def icon_pixmap(name: str, size: int = 20, color: str = "#0F172A", stroke: float = 2.0) -> QPixmap:
    ratio = 2  # render at 2x for sharp results on HiDPI screens
    pixmap = QPixmap(size * ratio, size * ratio)
    pixmap.fill(Qt.transparent)
    painter = QPainter(pixmap)
    painter.setRenderHint(QPainter.Antialiasing)
    painter.scale(size * ratio / 24.0, size * ratio / 24.0)
    pen = QPen(QColor(color), stroke)
    pen.setCapStyle(Qt.RoundCap)
    pen.setJoinStyle(Qt.RoundJoin)
    for path, filled in _paths(name):
        if filled:
            painter.fillPath(path, QColor(color))
        else:
            painter.strokePath(path, pen)
    painter.end()
    pixmap.setDevicePixelRatio(ratio)
    return pixmap


def icon(name: str, size: int = 20, color: str = "#0F172A", stroke: float = 2.0) -> QIcon:
    return QIcon(icon_pixmap(name, size, color, stroke))
