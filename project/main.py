import sys
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

from pet import Pet
from tray import TrayManager
from config import config

class FireflyPetApp:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.app.setQuitOnLastWindowClosed(False)
        
        self.pet = Pet()
        
        # 设置程序图标
        icon_path = config.assets_dir / "characters" / "firefly" / "icon" / "firfly_64_64.ico"
        if icon_path.exists():
            self.app_icon = QIcon(str(icon_path))
            self.app.setWindowIcon(self.app_icon)
            self.pet.setWindowIcon(self.app_icon)
        else:
            self.app_icon = QIcon(str(config.assets_dir / "icon.png"))
            
        self.tray = TrayManager(icon_path if icon_path.exists() else config.assets_dir / "icon.png")
        
        self._connect_signals()
        self._sync_tray_state()
    
    def _connect_signals(self):
        self.tray.show_hide_toggled.connect(self.pet.toggle_visibility)
        self.tray.sound_toggled.connect(self.pet.set_sound)
        self.tray.dialog_toggled.connect(self.pet.set_dialog)
        self.tray.quit_requested.connect(self._quit)
        self.pet.quit_requested.connect(self._quit)
    
    def _sync_tray_state(self):
        self.tray.set_sound(config.get("sound_enabled", True))
        self.tray.set_dialog(config.get("dialog_enabled", True))
    
    def _quit(self):
        self.pet.cleanup()
        self.tray.hide()
        self.app.quit()
    
    def run(self):
        self.pet.show()
        self.tray.show()
        
        return self.app.exec_()

def main():
    app = FireflyPetApp()
    sys.exit(app.run())

if __name__ == "__main__":
    main()
