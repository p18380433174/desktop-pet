from pathlib import Path
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer, pyqtSignal, QObject
import random

class Animation:
    def __init__(self, name: str, frames: list, loop: bool = True):
        self.name = name
        self.frames = frames
        self.loop = loop
        self.current_frame = 0
    
    def get_frame(self) -> QPixmap:
        if not self.frames:
            return QPixmap()
        return self.frames[self.current_frame]
    
    def next_frame(self) -> bool:
        self.current_frame += 1
        if self.current_frame >= len(self.frames):
            if self.loop:
                self.current_frame = 0
            else:
                self.current_frame = len(self.frames) - 1
                return False
        return True
    
    def reset(self):
        self.current_frame = 0

class AnimationManager(QObject):
    frame_changed = pyqtSignal(QPixmap)
    animation_finished = pyqtSignal(str)
    
    def __init__(self, animations_dir: Path, width: int = 500, height: int = 600):
        super().__init__()
        self.animations_dir = animations_dir
        self.width = width
        self.height = height
        self.animations = {}
        self.current_animation = None
        
        self.timer = QTimer()
        self.timer.timeout.connect(self._update_frame)
        self.fps = 24  # 加快动画速度
        
        self._load_animations()
    
    def _load_animations(self):
        if not self.animations_dir.exists():
            return
        
        for anim_dir in self.animations_dir.iterdir():
            if anim_dir.is_dir():
                frames = self._load_frames(anim_dir)
                if frames:
                    # 默认除了点击和拖动外都循环
                    loop = anim_dir.name not in ["click", "拖动", "气鼓鼓"]
                    self.animations[anim_dir.name] = Animation(anim_dir.name, frames, loop)
    
    def _load_frames(self, directory: Path) -> list:
        frames = []
        extensions = [".png", ".jpg", ".jpeg", ".gif"]
        
        files = sorted([f for f in directory.iterdir() 
                       if f.suffix.lower() in extensions])
        
        for file in files:
            pixmap = QPixmap(str(file))
            if not pixmap.isNull():
                scaled = pixmap.scaled(self.width, self.height)
                frames.append(scaled)
        
        return frames
    
    def play(self, name: str, loop_override: bool = None, start_frame: int = 0):
        if name not in self.animations:
            if "站立" in self.animations:
                name = "站立"
            elif self.animations:
                name = list(self.animations.keys())[0]
            else:
                return
            
        self.current_animation = self.animations[name]
        if start_frame == 0:
            self.current_animation.reset()
        else:
            # 确保帧索引有效
            max_idx = max(0, len(self.current_animation.frames) - 1)
            self.current_animation.current_frame = max(0, min(start_frame, max_idx))
                
        if loop_override is not None:
            self.current_animation.loop = loop_override
            
        self.frame_changed.emit(self.current_animation.get_frame())
    
        self.timer.start(1000 // self.fps)
    
    def stop(self):
        self.timer.stop()
    
    def _update_frame(self):
        if not self.current_animation:
            return
        
        if not self.current_animation.next_frame():
            self.timer.stop()
            self.animation_finished.emit(self.current_animation.name)
            return
        
        self.frame_changed.emit(self.current_animation.get_frame())
    
    def get_current_frame(self) -> QPixmap:
        if self.current_animation:
            return self.current_animation.get_frame()
        return QPixmap()
    
    def has_animation(self, name: str) -> bool:
        return name in self.animations
    
    def get_animation_names(self) -> list:
        return list(self.animations.keys())

    def update_size(self, width: int, height: int):
        self.width = width
        self.height = height
        # 重新加载所有动画以应用新尺寸
        self.animations.clear()
        self._load_animations()
        
        # 如果当前有正在播放的动画，尝试恢复
        if self.current_animation:
            name = self.current_animation.name
            frame = self.current_animation.current_frame
            loop = self.current_animation.loop
            self.play(name, loop_override=loop, start_frame=frame)

    def play_random(self, loop_override: bool = None):
        names = self.get_animation_names()
        if names:
            normal_anims = [n for n in names if n not in ["拖动", "气鼓鼓"]]
            if not normal_anims:
                normal_anims = names
            self.play(random.choice(normal_anims), loop_override=loop_override)
