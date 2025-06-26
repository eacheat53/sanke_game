#!/usr/bin/env python3
"""
游戏配置管理器
提供更灵活的配置选项
"""

import json
import os
from utils.env_loader import env


class GameConfig:
    """游戏配置管理类"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self._apply_env_overrides()
    
    def _load_config(self):
        """加载配置文件"""
        default_config = {
            "game_settings": {
                "initial_fps": 10,
                "initial_snake_length": 3,
                "speed_increase_interval": 50,
                "speed_increase_amount": 2,
                "max_fps": 30,
                "show_grid": True,
                "difficulty": "normal",  # easy, normal, hard
                "special_food_probability": 0.1
            },
            "sound_settings": {
                "enabled": True,
                "volume": 0.5
            },
            "display_settings": {
                "window_width": 800,
                "window_height": 600,
                "grid_size": 20,
                "fullscreen": False
            },
            "colors": {
                "background": [0, 0, 0],
                "snake_head": [0, 200, 0],
                "snake_body": [0, 255, 0],
                "food": [255, 0, 0],
                "special_food": [255, 215, 0],
                "text": [255, 255, 255],
                "grid": [128, 128, 128]
            }
        }
        
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    loaded_config = json.load(f)
                    # 合并配置，保留默认值
                    self._merge_config(default_config, loaded_config)
            return default_config
        except Exception as e:
            print(f"警告: 加载配置文件失败: {e}，使用默认配置")
            return default_config
    
    def _merge_config(self, default, loaded):
        """递归合并配置"""
        for key, value in loaded.items():
            if key in default:
                if isinstance(value, dict) and isinstance(default[key], dict):
                    self._merge_config(default[key], value)
                else:
                    default[key] = value
    
    def _apply_env_overrides(self):
        """应用环境变量覆盖"""
        # 游戏设置
        if env.get('SNAKE_GAME_DIFFICULTY'):
            self.config['game_settings']['difficulty'] = env.get('SNAKE_GAME_DIFFICULTY')
        
        if env.get('SNAKE_GAME_FPS'):
            self.config['game_settings']['initial_fps'] = env.get_int('SNAKE_GAME_FPS')
        
        # 显示设置
        if env.get('SNAKE_GAME_FULLSCREEN'):
            self.config['display_settings']['fullscreen'] = env.get_bool('SNAKE_GAME_FULLSCREEN')
        
        # 音效设置
        if env.get('SNAKE_GAME_SOUND'):
            self.config['sound_settings']['enabled'] = env.get_bool('SNAKE_GAME_SOUND')
        
        if env.get('SNAKE_GAME_VOLUME'):
            self.config['sound_settings']['volume'] = env.get_float('SNAKE_GAME_VOLUME')
        
        # 颜色设置
        color_mappings = {
            'SNAKE_GAME_COLOR_BACKGROUND': 'background',
            'SNAKE_GAME_COLOR_SNAKE_HEAD': 'snake_head',
            'SNAKE_GAME_COLOR_SNAKE_BODY': 'snake_body',
            'SNAKE_GAME_COLOR_FOOD': 'food'
        }
        
        for env_key, config_key in color_mappings.items():
            if env.get(env_key):
                self.config['colors'][config_key] = env.get_rgb(env_key)
    
    def get(self, section, key, default=None):
        """获取配置值"""
        return self.config.get(section, {}).get(key, default)
    
    def get_difficulty_settings(self):
        """根据难度获取游戏设置"""
        difficulty = self.config['game_settings']['difficulty']
        
        if difficulty == 'easy':
            return {
                'initial_fps': 8,
                'speed_increase_interval': 100,
                'speed_increase_amount': 1,
                'max_fps': 20
            }
        elif difficulty == 'hard':
            return {
                'initial_fps': 15,
                'speed_increase_interval': 30,
                'speed_increase_amount': 3,
                'max_fps': 50
            }
        else:  # normal
            return {
                'initial_fps': self.config['game_settings']['initial_fps'],
                'speed_increase_interval': self.config['game_settings']['speed_increase_interval'],
                'speed_increase_amount': self.config['game_settings']['speed_increase_amount'],
                'max_fps': self.config['game_settings']['max_fps']
            }
    
    def save_config(self):
        """保存配置到文件"""
        try:
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
        except Exception as e:
            print(f"保存配置文件失败: {e}")


# 创建全局配置实例
game_config = GameConfig()