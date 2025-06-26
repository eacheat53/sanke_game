"""
音效管理器
"""

import pygame
import os


class SoundManager:
    def __init__(self):
        """初始化音效管理器"""
        self.sounds = {}
        self.sound_enabled = True
        
        # 初始化pygame mixer
        try:
            pygame.mixer.init()
        except:
            self.sound_enabled = False
            print("警告: 无法初始化音效系统")
    
    def load_sound(self, name, filename):
        """加载音效文件"""
        if not self.sound_enabled:
            return
        
        try:
            sound_path = os.path.join("assets", "sounds", filename)
            if os.path.exists(sound_path):
                self.sounds[name] = pygame.mixer.Sound(sound_path)
            else:
                print(f"音效文件不存在: {sound_path}")
        except Exception as e:
            print(f"加载音效失败 {filename}: {e}")
    
    def play_sound(self, name):
        """播放音效"""
        if self.sound_enabled and name in self.sounds:
            try:
                self.sounds[name].play()
            except:
                pass
    
    def toggle_sound(self):
        """切换音效开关"""
        self.sound_enabled = not self.sound_enabled
        return self.sound_enabled
    
    def set_volume(self, volume):
        """设置音量 (0.0 - 1.0)"""
        if self.sound_enabled:
            for sound in self.sounds.values():
                sound.set_volume(volume)