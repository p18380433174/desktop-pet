from PyQt5.QtWidgets import QWidget, QLabel, QMenu, QAction
from PyQt5.QtCore import Qt, QPoint, QTimer, pyqtSignal
from PyQt5.QtGui import QPixmap, QPainter, QColor
import random

from config import config
from animation import AnimationManager
from behavior import BehaviorManager, PetState
from sound import SoundManager
from dialog import DialogBubble

class Pet(QWidget):
    BASE_WIDTH = 350
    BASE_HEIGHT = 420
    
    quit_requested = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        
        self.scale = config.get("scale", 1.0)
        self.PET_WIDTH = int(self.BASE_WIDTH * self.scale)
        self.PET_HEIGHT = int(self.BASE_HEIGHT * self.scale)
        
        self.drag_position = QPoint()
        self.is_dragging = False
        self.mouse_press_pos = QPoint()
        self.click_count = 0
        self.is_playing_angry = False
        self.saved_anim_state = None  # 记录交互前的动画状态 (name, frame, loop, is_click)
        self.click_reset_timer = QTimer()
        self.click_reset_timer.setSingleShot(True)
        self.click_reset_timer.timeout.connect(self._reset_click_count)
        self.is_click_animation = False  # 标记是否正在播放点击触发的动画
        
        self._setup_window()
        self._setup_components()
        self._connect_signals()
        self._load_config()
        
        self._start()
    
    def _setup_window(self):
        self.setWindowFlags(
            Qt.FramelessWindowHint |
            Qt.WindowStaysOnTopHint |
            Qt.Tool
        )
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.PET_WIDTH, self.PET_HEIGHT)
        
        self.image_label = QLabel(self)
        self.image_label.setFixedSize(self.PET_WIDTH, self.PET_HEIGHT)
        self.image_label.setAlignment(Qt.AlignCenter)
        
        self._set_placeholder_image()
    
    def _set_placeholder_image(self):
        pixmap = QPixmap(self.PET_WIDTH, self.PET_HEIGHT)
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.setBrush(QColor(255, 182, 193, 200))
        painter.setPen(QColor(255, 105, 180))
        painter.drawEllipse(10, 10, self.PET_WIDTH - 20, self.PET_HEIGHT - 20)
        
        painter.setPen(QColor(80, 80, 80))
        font = painter.font()
        font.setPointSize(12)
        font.setBold(True)
        painter.setFont(font)
        painter.drawText(pixmap.rect(), Qt.AlignCenter, "流萤")
        
        painter.end()
        
        self.image_label.setPixmap(pixmap)
        self.placeholder_pixmap = pixmap
    
    def _setup_components(self):
        self.animation_manager = AnimationManager(
            config.animations_dir, 
            self.PET_WIDTH,
            self.PET_HEIGHT
        )
        
        self.behavior_manager = BehaviorManager(self.PET_WIDTH, self.PET_HEIGHT)
        
        self.sound_manager = SoundManager(config.sounds_dir)
        
        self.dialog_bubble = DialogBubble()
        self.dialog_bubble.set_dialogs(config.load_dialogs())
    
    def _connect_signals(self):
        self.animation_manager.frame_changed.connect(self._on_frame_changed)
        self.animation_manager.animation_finished.connect(self._on_animation_finished)
        
        self.behavior_manager.state_changed.connect(self._on_state_changed)
        self.behavior_manager.position_changed.connect(self._on_position_changed)
        self.behavior_manager.request_dialog.connect(self._show_dialog)
    
    def _load_config(self):
        x = config.get("pet_x", 100)
        y = config.get("pet_y", 100)
        self.move(x, y)
        self.behavior_manager.set_position(x, y)
        
        self.sound_manager.set_enabled(config.get("sound_enabled", True))
        self.sound_manager.set_volume(config.get("volume", 0.5))
        
        self.behavior_manager.set_enabled(config.get("auto_walk", True))
        self.dialog_bubble.set_enabled(config.get("dialog_enabled", True))
    
    def _start(self):
        if self.animation_manager.has_animation("站立"):
            self.animation_manager.play("站立")
        elif self.animation_manager.get_animation_names():
            self.animation_manager.play_random()
        
        self.behavior_manager.start_idle()
    
    def _on_frame_changed(self, pixmap: QPixmap):
        if not pixmap.isNull():
            self.image_label.setPixmap(pixmap)
    
    def _on_animation_finished(self, name: str):
        # 如果是“气鼓鼓”播放完，重置状态并恢复
        if name == "气鼓鼓":
            self.is_playing_angry = False
            self.is_click_animation = False
            self.click_count = 0
            
            # 如果有保存的状态，优先恢复
            if self.saved_anim_state:
                self._restore_animation_state()
            else:
                # 否则恢复当前逻辑状态对应的动画
                self._on_state_changed(self.behavior_manager.state)
            return

        # 如果正在播放“气鼓鼓”，忽略其他动画结束信号（防止干扰）
        if self.is_playing_angry:
            return

        # 如果是点击触发的动画播放完成，重置标记
        if self.is_click_animation:
            self.is_click_animation = False

        mode = config.get("animation_mode", "random")
        if mode == "random":
            # 随机模式下，一个动画播完自动播下一个
            self.animation_manager.play_random(loop_override=False)
        else:
            # 保持模式下，播完重播同一个动画
            if self.animation_manager.current_animation:
                self.animation_manager.play(self.animation_manager.current_animation.name, loop_override=True)
    
    def _reset_click_count(self):
        self.click_count = 0

    def _on_state_changed(self, state: PetState):
        # 如果正在播放“气鼓鼓”，拦截所有状态改变导致的动画切换，确保完整播放
        if self.is_playing_angry:
            return

        # 如果有保存的状态（例如刚结束拖动），且当前不是拖动状态，则恢复
        if state != PetState.DRAGGING and self.saved_anim_state:
            self._restore_animation_state()
            return

        anim_name = self.behavior_manager.get_animation_name()
        mode = config.get("animation_mode", "random")
        
        # 拖动状态特殊处理
        if state == PetState.DRAGGING:
            self._save_current_animation_state()
            if self.animation_manager.has_animation("拖动"):
                self.animation_manager.play("拖动", loop_override=True)
                return
            return

        if state == PetState.IDLE and mode == "random":
            self.animation_manager.play_random(loop_override=False)
            return

        if self.animation_manager.has_animation(anim_name):
            loop = (mode == "keep")
            # 某些动作强制不循环
            if anim_name in ["气鼓鼓"]:
                loop = False
            self.animation_manager.play(anim_name, loop_override=loop)
        else:
            loop = (mode == "keep")
            self.animation_manager.play("站立", loop_override=loop)
        
        if state == PetState.CLICKING:
            self.sound_manager.play("click")
        elif state in [PetState.WALKING_LEFT, PetState.WALKING_RIGHT]:
            self.sound_manager.play("walk")
    
    def _on_position_changed(self, x: int, y: int):
        self.move(x, y)
        self.dialog_bubble.update_position(x, y, self.PET_WIDTH, self.PET_HEIGHT)
    
    def _show_dialog(self):
        pos = self.pos()
        self.dialog_bubble.show_random(pos.x(), pos.y(), self.PET_WIDTH, self.PET_HEIGHT)
        self.sound_manager.play("dialog")

    def _save_current_animation_state(self):
        # 如果已经存过状态了（例如在生气中又发生了状态切换），不覆盖最原始的状态
        if self.saved_anim_state:
            return
            
        curr = self.animation_manager.current_animation
        if curr:
            self.saved_anim_state = {
                "name": curr.name,
                "frame": curr.current_frame,
                "loop": curr.loop,
                "is_click": self.is_click_animation
            }

    def _restore_animation_state(self):
        if not self.saved_anim_state:
            return
            
        state = self.saved_anim_state
        self.saved_anim_state = None
        
        self.is_click_animation = state["is_click"]
        self.animation_manager.play(
            state["name"], 
            loop_override=state["loop"], 
            start_frame=state["frame"]
        )
    
    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.is_dragging = False
            self.mouse_press_pos = event.globalPos()
            self.drag_position = event.globalPos() - self.frameGeometry().topLeft()
            event.accept()
    
    def mouseMoveEvent(self, event):
        if event.buttons() == Qt.LeftButton:
            # 只有移动距离超过阈值才认为是拖动
            if not self.is_dragging:
                if (event.globalPos() - self.mouse_press_pos).manhattanLength() > 5:
                    self.is_dragging = True
                    self.behavior_manager.start_dragging()
            
            if self.is_dragging:
                new_pos = event.globalPos() - self.drag_position
                self.move(new_pos)
                self.behavior_manager.set_position(new_pos.x(), new_pos.y())
                self.dialog_bubble.update_position(new_pos.x(), new_pos.y(), self.PET_WIDTH, self.PET_HEIGHT)
                event.accept()
    
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            if self.is_dragging:
                self.is_dragging = False
                self.behavior_manager.stop_dragging()
                
                pos = self.pos()
                config.set("pet_x", pos.x())
                config.set("pet_y", pos.y())
            else:
                # 认为是单击
                self._handle_click()
            event.accept()

    def _handle_click(self):
        # 如果正在播放“气鼓鼓”，则不响应任何点击事件（互斥）
        if self.is_playing_angry:
            return
            
        self.click_count += 1
        self.click_reset_timer.start(2000)  # 2秒内没点击则重置计数
        
        if self.click_count >= 3 and self.animation_manager.has_animation("气鼓鼓"):
            # 记录生气前的状态
            self._save_current_animation_state()
            # 触发多次点击事件：播放“气鼓鼓”
            self.is_playing_angry = True
            self.is_click_animation = True
            self.animation_manager.play("气鼓鼓", loop_override=False)
            self.sound_manager.play("click")
            # 多次点击事件触发后，不执行单次点击的对话逻辑（或者执行特定的）
        else:
            # 单次点击事件：播放随机动画并显示对话
            self.is_click_animation = True
            self.animation_manager.play_random(loop_override=False)
            self.sound_manager.play("click")
            self._show_dialog()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.behavior_manager.trigger_click()
            self._show_dialog()
            event.accept()
    
    def contextMenuEvent(self, event):
        menu = QMenu(self)
        
        # 动画模式子菜单
        mode_menu = menu.addMenu("动画模式")
        
        keep_action = QAction("保持", mode_menu, checkable=True)
        keep_action.setChecked(config.get("animation_mode") == "keep")
        keep_action.triggered.connect(lambda: self._set_animation_mode("keep"))
        mode_menu.addAction(keep_action)
        
        random_action = QAction("随机", mode_menu, checkable=True)
        random_action.setChecked(config.get("animation_mode") == "random")
        random_action.triggered.connect(lambda: self._set_animation_mode("random"))
        mode_menu.addAction(random_action)
        
        menu.addSeparator()
        
        # 人物比例子菜单
        scale_menu = menu.addMenu("人物比例")
        scales = [0.5, 0.75, 1.0, 1.25, 1.5, 2.0]
        for s in scales:
            scale_action = QAction(f"{int(s*100)}%", scale_menu, checkable=True)
            scale_action.setChecked(abs(self.scale - s) < 0.01)
            scale_action.triggered.connect(lambda checked, val=s: self._set_scale(val))
            scale_menu.addAction(scale_action)

        menu.addSeparator()
        
        # 改变动作子菜单
        change_anim_menu = menu.addMenu("改变动作")
        anim_names = self.animation_manager.get_animation_names()
        # 排除掉特殊的交互动画，使列表更整洁
        display_names = [n for n in anim_names if n not in ["拖动", "气鼓鼓", "click"]]
        if not display_names:
            display_names = anim_names
            
        for name in sorted(display_names):
            anim_action = QAction(name, change_anim_menu)
            anim_action.triggered.connect(lambda checked, n=name: self._change_to_animation(n))
            change_anim_menu.addAction(anim_action)

        menu.addSeparator()
        
        dialog_action = QAction("说话", menu)
        dialog_action.triggered.connect(self._show_dialog)
        menu.addAction(dialog_action)
        
        menu.addSeparator()
        
        quit_action = QAction("退出", menu)
        quit_action.triggered.connect(self.quit_requested.emit)
        menu.addAction(quit_action)
        
        menu.exec_(event.globalPos())

    def _set_animation_mode(self, mode: str):
        config.set("animation_mode", mode)
        # 如果切换到保持模式，当前动画应该循环
        if mode == "keep":
            if self.animation_manager.current_animation:
                self.animation_manager.current_animation.loop = True
        else:
            # 如果切换到随机，且当前动画已完成，则立即随机一个
            if self.animation_manager.current_animation:
                self.animation_manager.current_animation.loop = False

    def _change_to_animation(self, name: str):
        # 手动切换动作时，重置一些交互状态
        self.is_playing_angry = False
        self.is_click_animation = False
        self.click_count = 0
        self.saved_anim_state = None
        
        # 播放指定的动画
        # 模式参考：如果当前是保持模式，则循环播放该动作
        loop = (config.get("animation_mode") == "keep")
        self.animation_manager.play(name, loop_override=loop)

    def _set_scale(self, scale: float):
        if abs(self.scale - scale) < 0.01:
            return
            
        self.scale = scale
        config.set("scale", scale)
        
        # 更新实际尺寸
        self.PET_WIDTH = int(self.BASE_WIDTH * scale)
        self.PET_HEIGHT = int(self.BASE_HEIGHT * scale)
        
        # 调整窗口大小
        self.setFixedSize(self.PET_WIDTH, self.PET_HEIGHT)
        self.image_label.setFixedSize(self.PET_WIDTH, self.PET_HEIGHT)
        
        # 通知动画管理器更新
        self.animation_manager.update_size(self.PET_WIDTH, self.PET_HEIGHT)
        
        # 通知行为管理器更新（如果有需要边界检测）
        if hasattr(self.behavior_manager, 'update_pet_size'):
            self.behavior_manager.update_pet_size(self.PET_WIDTH, self.PET_HEIGHT)
    
    def toggle_visibility(self):
        if self.isVisible():
            self.hide()
            self.dialog_bubble.hide()
        else:
            self.show()
    
    def set_sound(self, enabled: bool):
        self.sound_manager.set_enabled(enabled)
        config.set("sound_enabled", enabled)
    
    def set_dialog(self, enabled: bool):
        self.dialog_bubble.set_enabled(enabled)
        config.set("dialog_enabled", enabled)
    
    def cleanup(self):
        pos = self.pos()
        config.set("pet_x", pos.x())
        config.set("pet_y", pos.y())
        
        self.animation_manager.stop()
        self.sound_manager.stop_all()
        self.dialog_bubble.hide()
