"""
游戏资源管理器
用于缓存字体、图像和音效，提高性能
"""

import pygame
from typing import Dict, Tuple, Optional
from .constants import *


class ResourceManager:
    """游戏资源管理器"""
    
    def __init__(self):
        """初始化资源管理器"""
        # 确保pygame已初始化
        if not pygame.get_init():
            pygame.init()
        
        # 确保字体模块已初始化
        if not pygame.font.get_init():
            pygame.font.init()
            
        self.fonts: Dict[Tuple[str, int], pygame.font.Font] = {}
        self.text_surfaces: Dict[Tuple[str, str, Tuple[int, int, int]], pygame.Surface] = {}
        self.sounds: Dict[str, pygame.mixer.Sound] = {}
        self.images: Dict[str, pygame.Surface] = {}
        
        # 预加载常用字体
        self._preload_fonts()
    
    def _preload_fonts(self):
        """预加载常用字体"""
        font_names = ['simhei', 'microsoftyaheui', 'simsun', 'arial']
        sizes = [FONT_SIZE, SMALL_FONT_SIZE, 48]
        
        for size in sizes:
            try:
                # 尝试系统字体
                font = pygame.font.SysFont(','.join(font_names), size)
                self.fonts[('system', size)] = font
            except:
                # 使用默认字体
                font = pygame.font.Font(None, size)
                self.fonts[('default', size)] = font
    
    def get_font(self, font_type: str = 'system', size: int = FONT_SIZE) -> pygame.font.Font:
        """获取字体对象
        
        Args:
            font_type: 字体类型 ('system' 或 'default')
            size: 字体大小
            
        Returns:
            字体对象
        """
        key = (font_type, size)
        if key not in self.fonts:
            try:
                if font_type == 'system':
                    font_names = ['simhei', 'microsoftyaheui', 'simsun', 'arial']
                    self.fonts[key] = pygame.font.SysFont(','.join(font_names), size)
                else:
                    self.fonts[key] = pygame.font.Font(None, size)
            except:
                self.fonts[key] = pygame.font.Font(None, size)
        
        return self.fonts[key]
    
    def get_text_surface(self, text: str, font_type: str = 'system', 
                        size: int = FONT_SIZE, color: Tuple[int, int, int] = WHITE,
                        cache: bool = True) -> pygame.Surface:
        """获取文本表面，支持缓存
        
        Args:
            text: 文本内容
            font_type: 字体类型
            size: 字体大小
            color: 文本颜色
            cache: 是否缓存
            
        Returns:
            文本表面
        """
        cache_key = (text, f"{font_type}_{size}", color)
        
        if cache and cache_key in self.text_surfaces:
            return self.text_surfaces[cache_key]
        
        font = self.get_font(font_type, size)
        surface = font.render(text, True, color)
        
        if cache:
            # 限制缓存大小，避免内存泄漏
            if len(self.text_surfaces) > 100:
                # 清除最旧的一半缓存
                items = list(self.text_surfaces.items())
                for key, _ in items[:50]:
                    del self.text_surfaces[key]
            
            self.text_surfaces[cache_key] = surface
        
        return surface
    
    def clear_text_cache(self):
        """清除文本缓存"""
        self.text_surfaces.clear()
    
    def preload_game_texts(self):
        """预加载游戏中常用的文本"""
        common_texts = [
            ("游戏暂停", 'system', FONT_SIZE, WHITE),
            ("游戏结束!", 'system', FONT_SIZE, RED),
            ("按P键继续", 'system', SMALL_FONT_SIZE, WHITE),
            ("按空格键重新开始", 'system', SMALL_FONT_SIZE, WHITE),
            ("按R键返回设置", 'system', SMALL_FONT_SIZE, ORANGE),
            ("按ESC键退出", 'system', SMALL_FONT_SIZE, WHITE),
        ]
        
        for text, font_type, size, color in common_texts:
            self.get_text_surface(text, font_type, size, color)
    
    def get_memory_usage(self) -> Dict[str, int]:
        """获取内存使用情况"""
        return {
            'fonts': len(self.fonts),
            'text_surfaces': len(self.text_surfaces),
            'sounds': len(self.sounds),
            'images': len(self.images)
        }


# 创建全局资源管理器实例
resource_manager = ResourceManager()