from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QFont
import random

class DialogBubble(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.dialogs = []
        self.enabled = True
        
        self._setup_ui()
        
        self.hide_timer = QTimer()
        self.hide_timer.timeout.connect(self.hide_bubble)
        self.hide_timer.setSingleShot(True)
    
    def _setup_ui(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        
        self.label = QLabel(self)
        self.label.setStyleSheet("""
            QLabel {
                background-color: rgba(255, 255, 255, 230);
                border: 2px solid #FFB6C1;
                border-radius: 15px;
                padding: 10px 15px;
                color: #333333;
            }
        """)
        self.label.setFont(QFont("Microsoft YaHei", 10))
        self.label.setWordWrap(True)
        self.label.setMaximumWidth(200)
    
    def set_dialogs(self, dialogs: list):
        self.dialogs = dialogs
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self.hide()
    
    def show_random(self, pet_x: int, pet_y: int, pet_width: int, pet_height: int):
        if not self.enabled or not self.dialogs:
            return
        
        text = random.choice(self.dialogs)
        self.show_message(text, pet_x, pet_y, pet_width, pet_height)
    
    def show_message(self, text: str, pet_x: int, pet_y: int, pet_width: int, pet_height: int):
        if not self.enabled:
            return
        
        self.label.setText(text)
        self.label.adjustSize()
        
        self.setFixedSize(self.label.size())
        
        bubble_x = pet_x + pet_width // 2 - self.width() // 2
        bubble_y = pet_y - self.height() - 10
        
        if bubble_y < 0:
            bubble_y = pet_y + pet_height + 10
        
        self.move(bubble_x, bubble_y)
        self.show()
        
        self.hide_timer.start(3000)
    
    def hide_bubble(self):
        self.hide()
    
    def update_position(self, pet_x: int, pet_y: int, pet_width: int, pet_height: int):
        if self.isVisible():
            bubble_x = pet_x + pet_width // 2 - self.width() // 2
            bubble_y = pet_y - self.height() - 10
            
            if bubble_y < 0:
                bubble_y = pet_y + pet_height + 10
            
            self.move(bubble_x, bubble_y)
