from enum import Enum, auto
from PyQt5.QtCore import QTimer, QObject, pyqtSignal
from PyQt5.QtWidgets import QDesktopWidget
import random

class PetState(Enum):
    IDLE = auto()
    WALKING_LEFT = auto()
    WALKING_RIGHT = auto()
    DRAGGING = auto()
    CLICKING = auto()

class BehaviorManager(QObject):
    state_changed = pyqtSignal(PetState)
    position_changed = pyqtSignal(int, int)
    request_dialog = pyqtSignal()
    
    def __init__(self, pet_width: int = 500, pet_height: int = 600):
        super().__init__()
        self.pet_width = pet_width
        self.pet_height = pet_height
        self.state = PetState.IDLE
        self.enabled = True
        
        self.x = 100
        self.y = 100
        self.walk_speed = 2
        self.walk_direction = 0
        
        desktop = QDesktopWidget()
        screen = desktop.screenGeometry()
        self.screen_width = screen.width()
        self.screen_height = screen.height()
        
        self.walk_timer = QTimer()
        self.walk_timer.timeout.connect(self._walk_step)
        
        self.behavior_timer = QTimer()
        self.behavior_timer.timeout.connect(self._random_behavior)
        # 移除自动开启行为定时器，不再自动行走
        # self.behavior_timer.start(random.randint(15000, 30000))
        
        self.dialog_timer = QTimer()
        self.dialog_timer.timeout.connect(self._trigger_dialog)
        self.dialog_timer.start(random.randint(20000, 45000))
    
    def set_position(self, x: int, y: int):
        self.x = x
        self.y = y
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
        if not enabled:
            self.stop_walking()
    
    def _change_state(self, new_state: PetState):
        if self.state != new_state:
            self.state = new_state
            self.state_changed.emit(new_state)
    
    def start_idle(self):
        self.stop_walking()
        self._change_state(PetState.IDLE)
    
    def start_walking(self, direction: int = None):
        if not self.enabled:
            return
        
        if direction is None:
            direction = random.choice([-1, 1])
        
        self.walk_direction = direction
        
        if direction < 0:
            self._change_state(PetState.WALKING_LEFT)
        else:
            self._change_state(PetState.WALKING_RIGHT)
        
        self.walk_timer.start(50)
        
        QTimer.singleShot(random.randint(3000, 8000), self.start_idle)
    
    def stop_walking(self):
        self.walk_timer.stop()
    
    def _walk_step(self):
        new_x = self.x + (self.walk_speed * self.walk_direction)
        
        margin = 50
        if new_x < margin:
            new_x = margin
            self.start_idle()
        elif new_x > self.screen_width - self.pet_width - margin:
            new_x = self.screen_width - self.pet_width - margin
            self.start_idle()
        
        if new_x != self.x:
            self.x = new_x
            self.position_changed.emit(self.x, self.y)
    
    def start_dragging(self):
        self.stop_walking()
        self._change_state(PetState.DRAGGING)
    
    def stop_dragging(self):
        self._change_state(PetState.IDLE)
    
    def trigger_click(self):
        if self.state == PetState.DRAGGING:
            return
        
        self.stop_walking()
        self._change_state(PetState.CLICKING)
        
        QTimer.singleShot(1000, self.start_idle)
    
    def _random_behavior(self):
        # 即使定时器意外触发，如果不启用或正在拖动也不执行任何操作
        if not self.enabled or self.state == PetState.DRAGGING:
            return
        
        # 自动行走功能已移除，此处仅保留逻辑框架
        pass
    
    def _trigger_dialog(self):
        if self.enabled and self.state not in [PetState.DRAGGING]:
            self.request_dialog.emit()
        
        self.dialog_timer.start(random.randint(20000, 45000))
    
    def get_animation_name(self) -> str:
        mapping = {
            PetState.IDLE: "站立",
            PetState.WALKING_LEFT: "乖巧",
            PetState.WALKING_RIGHT: "乖巧",
            PetState.DRAGGING: "疑惑",
            PetState.CLICKING: "气鼓鼓",
        }
        return mapping.get(self.state, "站立")
