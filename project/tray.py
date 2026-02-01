from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QApplication
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import pyqtSignal, QObject
from pathlib import Path

class TrayManager(QObject):
    show_hide_toggled = pyqtSignal()
    sound_toggled = pyqtSignal(bool)
    dialog_toggled = pyqtSignal(bool)
    quit_requested = pyqtSignal()
    
    def __init__(self, icon_path: Path = None):
        super().__init__()
        
        self.tray = QSystemTrayIcon()
        
        if icon_path and icon_path.exists():
            self.tray.setIcon(QIcon(str(icon_path)))
        else:
            self.tray.setIcon(QApplication.style().standardIcon(
                QApplication.style().SP_ComputerIcon
            ))
        
        self.tray.setToolTip("流萤桌面宠物")
        
        self._create_menu()
        
        self.tray.activated.connect(self._on_activated)
    
    def _create_menu(self):
        self.menu = QMenu()
        
        self.show_action = QAction("显示/隐藏", self.menu)
        self.show_action.triggered.connect(self.show_hide_toggled.emit)
        self.menu.addAction(self.show_action)
        
        self.menu.addSeparator()
        
        self.sound_action = QAction("音效", self.menu)
        self.sound_action.setCheckable(True)
        self.sound_action.setChecked(True)
        self.sound_action.triggered.connect(
            lambda checked: self.sound_toggled.emit(checked)
        )
        self.menu.addAction(self.sound_action)
        
        self.dialog_action = QAction("对话气泡", self.menu)
        self.dialog_action.setCheckable(True)
        self.dialog_action.setChecked(True)
        self.dialog_action.triggered.connect(
            lambda checked: self.dialog_toggled.emit(checked)
        )
        self.menu.addAction(self.dialog_action)
        
        self.menu.addSeparator()
        
        quit_action = QAction("退出", self.menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        self.menu.addAction(quit_action)
        
        self.tray.setContextMenu(self.menu)
    
    def _on_activated(self, reason):
        if reason == QSystemTrayIcon.DoubleClick:
            self.show_hide_toggled.emit()
    
    def show(self):
        self.tray.show()
    
    def hide(self):
        self.tray.hide()
    
    def set_sound(self, enabled: bool):
        self.sound_action.setChecked(enabled)
    
    def set_dialog(self, enabled: bool):
        self.dialog_action.setChecked(enabled)
