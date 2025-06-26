"""
辅助函数模块
"""

import pygame
import json
import os


def load_high_score(filename="high_score.json"):
    """加载最高分"""
    try:
        if os.path.exists(filename):
            with open(filename, 'r') as f:
                data = json.load(f)
                return data.get('high_score', 0)
    except:
        pass
    return 0


def save_high_score(score, filename="high_score.json"):
    """保存最高分"""
    try:
        data = {'high_score': score}
        with open(filename, 'w') as f:
            json.dump(data, f)
    except:
        pass


def clamp(value, min_value, max_value):
    """限制数值在指定范围内"""
    return max(min_value, min(value, max_value))


def get_distance(pos1, pos2):
    """计算两点之间的距离"""
    return ((pos1[0] - pos2[0]) ** 2 + (pos1[1] - pos2[1]) ** 2) ** 0.5


def create_text_surface(font, text, color, background=None):
    """创建文本表面"""
    if background:
        return font.render(text, True, color, background)
    else:
        return font.render(text, True, color)


def center_text(surface, text_surface):
    """将文本居中显示在表面上"""
    text_rect = text_surface.get_rect()
    surface_rect = surface.get_rect()
    text_rect.center = surface_rect.center
    return text_rect


def check_pygame_installation():
    """检查pygame是否正确安装"""
    try:
        import pygame
        return True
    except ImportError:
        print("错误: 未安装pygame库")
        print("请运行: pip install pygame")
        return False