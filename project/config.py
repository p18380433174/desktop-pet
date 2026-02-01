import json
import os
from pathlib import Path

class Config:
    DEFAULT_CONFIG = {
        "pet_x": 100,
        "pet_y": 100,
        "volume": 0.5,
        "sound_enabled": True,
        "auto_walk": True,
        "dialog_enabled": True,
        "character": "firefly",
        "animation_mode": "random", # "keep" or "random"
        "scale": 1.0,
    }
    
    def __init__(self):
        self.base_dir = Path(__file__).parent
        self.config_path = self.base_dir / "config.json"
        self.assets_dir = self.base_dir / "assets"
        
        self.data = self.load()
        self._update_paths()

    def _update_paths(self):
        character = self.get("character", "firefly")
        self.character_dir = self.assets_dir / "characters" / character
        self.animations_dir = self.character_dir / "animations"
        self.sounds_dir = self.assets_dir / "sounds"
        self.dialogs_path = self.assets_dir / "dialogs.json"
    
    def load(self) -> dict:
        if self.config_path.exists():
            try:
                with open(self.config_path, "r", encoding="utf-8") as f:
                    loaded = json.load(f)
                    return {**self.DEFAULT_CONFIG, **loaded}
            except (json.JSONDecodeError, IOError):
                pass
        return self.DEFAULT_CONFIG.copy()
    
    def save(self):
        try:
            with open(self.config_path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2, ensure_ascii=False)
        except IOError as e:
            print(f"保存配置失败: {e}")
    
    def get(self, key: str, default=None):
        return self.data.get(key, default)
    
    def set(self, key: str, value):
        self.data[key] = value
        if key == "character":
            self._update_paths()
        self.save()
    
    def load_dialogs(self) -> list:
        if self.dialogs_path.exists():
            try:
                with open(self.dialogs_path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
        return self.get_default_dialogs()
    
    def get_default_dialogs(self) -> list:
        return [
            "开拓者，今天也要一起努力哦！",
            "我是流萤...很高兴认识你。",
            "要一起去看星星吗？",
            "匹诺康尼的夜晚真美呢。",
            "我会一直陪在你身边的。",
            "有什么我能帮忙的吗？",
            "今天的天气真不错呢~",
            "开拓者，记得要休息哦。",
            "萤火虫的光芒，是为了照亮黑暗。",
            "无论发生什么，我都不会放弃希望。",
        ]

config = Config()
