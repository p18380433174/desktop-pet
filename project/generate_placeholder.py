"""
占位素材生成脚本
运行此脚本生成简单的占位动画帧，之后可替换为正式素材
"""
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
import math

def create_placeholder_frames():
    base_dir = Path(__file__).parent / "assets" / "animations"
    size = 128
    
    idle_dir = base_dir / "idle"
    idle_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(8):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        offset = int(math.sin(i * math.pi / 4) * 3)
        
        draw.ellipse(
            [15, 15 + offset, size - 15, size - 15 + offset],
            fill=(255, 182, 193, 220),
            outline=(255, 105, 180, 255),
            width=2
        )
        
        eye_y = 45 + offset
        draw.ellipse([40, eye_y, 50, eye_y + 10], fill=(60, 60, 60, 255))
        draw.ellipse([78, eye_y, 88, eye_y + 10], fill=(60, 60, 60, 255))
        
        mouth_y = 70 + offset
        draw.arc([50, mouth_y, 78, mouth_y + 15], 0, 180, fill=(60, 60, 60, 255), width=2)
        
        img.save(idle_dir / f"idle_{i:03d}.png")
    
    print(f"已生成 idle 动画帧: {idle_dir}")
    
    walk_left_dir = base_dir / "walk_left"
    walk_left_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(8):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bounce = int(abs(math.sin(i * math.pi / 2)) * 5)
        
        draw.ellipse(
            [15, 15 - bounce, size - 15, size - 15 - bounce],
            fill=(255, 182, 193, 220),
            outline=(255, 105, 180, 255),
            width=2
        )
        
        eye_y = 45 - bounce
        draw.ellipse([35, eye_y, 45, eye_y + 10], fill=(60, 60, 60, 255))
        draw.ellipse([73, eye_y, 83, eye_y + 10], fill=(60, 60, 60, 255))
        
        mouth_y = 70 - bounce
        draw.arc([50, mouth_y, 78, mouth_y + 15], 0, 180, fill=(60, 60, 60, 255), width=2)
        
        img.save(walk_left_dir / f"walk_{i:03d}.png")
    
    print(f"已生成 walk_left 动画帧: {walk_left_dir}")
    
    walk_right_dir = base_dir / "walk_right"
    walk_right_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(8):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        bounce = int(abs(math.sin(i * math.pi / 2)) * 5)
        
        draw.ellipse(
            [15, 15 - bounce, size - 15, size - 15 - bounce],
            fill=(255, 182, 193, 220),
            outline=(255, 105, 180, 255),
            width=2
        )
        
        eye_y = 45 - bounce
        draw.ellipse([45, eye_y, 55, eye_y + 10], fill=(60, 60, 60, 255))
        draw.ellipse([83, eye_y, 93, eye_y + 10], fill=(60, 60, 60, 255))
        
        mouth_y = 70 - bounce
        draw.arc([50, mouth_y, 78, mouth_y + 15], 0, 180, fill=(60, 60, 60, 255), width=2)
        
        img.save(walk_right_dir / f"walk_{i:03d}.png")
    
    print(f"已生成 walk_right 动画帧: {walk_right_dir}")
    
    click_dir = base_dir / "click"
    click_dir.mkdir(parents=True, exist_ok=True)
    
    for i in range(4):
        img = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        scale = 1.0 + (0.1 if i < 2 else 0)
        r = int((size - 30) * scale / 2)
        center = size // 2
        
        draw.ellipse(
            [center - r, center - r, center + r, center + r],
            fill=(255, 150, 170, 220),
            outline=(255, 80, 150, 255),
            width=3
        )
        
        eye_y = 45
        draw.ellipse([40, eye_y - 5, 55, eye_y + 15], fill=(60, 60, 60, 255))
        draw.ellipse([73, eye_y - 5, 88, eye_y + 15], fill=(60, 60, 60, 255))
        
        mouth_y = 65
        draw.ellipse([50, mouth_y, 78, mouth_y + 20], fill=(60, 60, 60, 255))
        
        img.save(click_dir / f"click_{i:03d}.png")
    
    print(f"已生成 click 动画帧: {click_dir}")
    
    icon_path = base_dir.parent / "icon.png"
    icon = Image.new("RGBA", (64, 64), (0, 0, 0, 0))
    draw = ImageDraw.Draw(icon)
    draw.ellipse([5, 5, 59, 59], fill=(255, 182, 193, 255), outline=(255, 105, 180, 255), width=2)
    draw.ellipse([18, 20, 26, 28], fill=(60, 60, 60, 255))
    draw.ellipse([38, 20, 46, 28], fill=(60, 60, 60, 255))
    draw.arc([22, 32, 42, 45], 0, 180, fill=(60, 60, 60, 255), width=2)
    icon.save(icon_path)
    
    print(f"已生成托盘图标: {icon_path}")
    print("\n占位素材生成完成！你可以将其替换为正式的流萤素材。")

if __name__ == "__main__":
    create_placeholder_frames()
