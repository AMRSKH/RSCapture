# ui/selection_overlay.py
from PyQt6.QtWidgets import QApplication, QWidget
from PyQt6.QtGui import QPainter, QPen, QBrush, QColor, QFont # Import QFont
from PyQt6.QtCore import Qt, QRect, QPoint, pyqtSignal
from typing import Optional

class SelectionOverlay(QWidget):
    """
    A transparent, frameless overlay window for selecting a screen region.
    Emits a signal with the selected rectangle (x, y, width, height) when selection is complete.
    """
    selection_made = pyqtSignal(int, int, int, int) # x, y, width, height

    def __init__(self):
        super().__init__()
        self.setWindowFlags(
            Qt.WindowType.WindowStaysOnTopHint |
            Qt.WindowType.FramelessWindowHint |
            Qt.WindowType.SplashScreen # SplashScreen hides it from taskbar
        )
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        # Get the geometry of the primary screen using QApplication.primaryScreen()
        screen_rect = QApplication.primaryScreen().geometry()
        self.setGeometry(screen_rect)

        self.start_point: Optional[QPoint] = None
        self.end_point: Optional[QPoint] = None
        self.current_rect: Optional[QRect] = None

        self.setMouseTracking(True) # Ensure mouseMoveEvent is triggered even without button pressed

    def showEvent(self, event):
        """Called when the widget is shown."""
        super().showEvent(event)
        self.start_point = None
        self.end_point = None
        self.current_rect = None
        self.setCursor(Qt.CursorShape.CrossCursor) # Change cursor to crosshair
        self.grabMouse() # Grab mouse to ensure all events are captured by this widget

    def hideEvent(self, event):
        """Called when the widget is hidden."""
        super().hideEvent(event)
        self.releaseMouse() # Release mouse grab

    def paintEvent(self, event):
        """
        Draws the selection rectangle and darkens the unselected area.
        """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Draw a translucent dark overlay over the entire screen
        painter.setBrush(QBrush(QColor(0, 0, 0, 100))) # Dark translucent color
        painter.setPen(Qt.PenStyle.NoPen)
        painter.drawRect(self.rect())

        if self.current_rect is not None:
            # Draw the selected area with a transparent background
            painter.setBrush(QBrush(QColor(0, 0, 0, 0))) # Fully transparent
            painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.PenStyle.DashLine)) # White dashed border
            painter.drawRect(self.current_rect)

            # Draw a solid border around the selected area
            painter.setPen(QPen(QColor(255, 255, 255), 2, Qt.PenStyle.SolidLine)) # Solid white border
            self.current_rect = self.current_rect.normalized() # Ensure width/height are positive for accurate drawing
            painter.drawRect(self.current_rect.adjusted(1,1,-1,-1)) # Adjust slightly for solid line

            # Draw resolution text
            resolution_text = f"{self.current_rect.width()}x{self.current_rect.height()}"
            painter.setPen(QPen(QColor(255, 255, 255))) # White text

            # *** UPDATED: Create a QFont object explicitly ***
            font = QFont()
            font.setPointSize(10)
            painter.setFont(font)
            # *** END UPDATED CODE ***

            text_rect = self.current_rect.adjusted(0, -20, 0, 0) # Position above the selection
            painter.drawText(text_rect, Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft, resolution_text)


    def mousePressEvent(self, event):
        """
        Starts the selection when the left mouse button is pressed.
        """
        if event.button() == Qt.MouseButton.LeftButton:
            # globalPosition is better for multi-screen setups
            self.start_point = event.globalPosition().toPoint()
            self.end_point = self.start_point
            self.current_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseMoveEvent(self, event):
        """
        Updates the selection rectangle as the mouse is moved.
        """
        if self.start_point is not None:
            self.end_point = event.globalPosition().toPoint()
            self.current_rect = QRect(self.start_point, self.end_point).normalized()
            self.update()

    def mouseReleaseEvent(self, event):
        """
        Finalizes the selection when the left mouse button is released.
        Emits the selection_made signal.
        """
        if event.button() == Qt.MouseButton.LeftButton and self.start_point is not None:
            final_rect = self.current_rect
            if final_rect is not None and final_rect.width() > 0 and final_rect.height() > 0:
                self.selection_made.emit(final_rect.x(), final_rect.y(), final_rect.width(), final_rect.height())
            self.hide() # Hide the overlay after selection
            self.setCursor(Qt.CursorShape.ArrowCursor) # Restore default cursor
