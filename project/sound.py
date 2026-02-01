from pathlib import Path

class SoundManager:
    def __init__(self, sounds_dir: Path):
        self.sounds_dir = sounds_dir
        self.enabled = True
        self.volume = 0.5
        self.sounds = {}
        self._mixer_initialized = False
        
        self._init_mixer()
        self._load_sounds()
    
    def _init_mixer(self):
        try:
            import pygame
            pygame.mixer.init()
            self._mixer_initialized = True
        except Exception as e:
            print(f"音效初始化失败: {e}")
            self._mixer_initialized = False
    
    def _load_sounds(self):
        if not self._mixer_initialized or not self.sounds_dir.exists():
            return
        
        import pygame
        extensions = [".wav", ".mp3", ".ogg"]
        
        for file in self.sounds_dir.iterdir():
            if file.suffix.lower() in extensions:
                try:
                    sound = pygame.mixer.Sound(str(file))
                    self.sounds[file.stem] = sound
                except Exception as e:
                    print(f"加载音效失败 {file.name}: {e}")
    
    def play(self, name: str):
        if not self.enabled or not self._mixer_initialized:
            return
        
        if name in self.sounds:
            try:
                self.sounds[name].set_volume(self.volume)
                self.sounds[name].play()
            except Exception:
                pass
    
    def set_volume(self, volume: float):
        self.volume = max(0.0, min(1.0, volume))
    
    def set_enabled(self, enabled: bool):
        self.enabled = enabled
    
    def stop_all(self):
        if self._mixer_initialized:
            try:
                import pygame
                pygame.mixer.stop()
            except Exception:
                pass
