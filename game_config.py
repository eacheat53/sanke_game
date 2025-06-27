#!/usr/bin/env python3
"""
游戏配置管理器
提供更灵活的配置选项
"""

import json
import os
from typing import Any, Dict, Optional
from utils.env_loader import env


class GameConfig:
    """游戏配置管理类"""
    
    def __init__(self, config_file="config.json"):
        self.config_file = config_file
        self.config = self._load_config()
        self._apply_env_overrides()
        self._validate_config()
    
    def _load_config(self):
        """加载配置文件"""
        default_config = self._get_default_config()
        
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
    
    def _validate_config(self):
        """验证配置的有效性"""
        try:
            # 验证游戏设置
            game_settings = self.config.get('game_settings', {})
            
            # 验证FPS范围
            initial_fps = game_settings.get('initial_fps', 10)
            if not isinstance(initial_fps, int) or initial_fps < 1 or initial_fps > 60:
                print(f"警告: initial_fps 值无效 ({initial_fps})，使用默认值 10")
                game_settings['initial_fps'] = 10
            
            max_fps = game_settings.get('max_fps', 30)
            if not isinstance(max_fps, int) or max_fps < initial_fps or max_fps > 120:
                print(f"警告: max_fps 值无效 ({max_fps})，使用默认值 30")
                game_settings['max_fps'] = 30
            
            # 验证蛇长度
            snake_length = game_settings.get('initial_snake_length', 3)
            if not isinstance(snake_length, int) or snake_length < 1 or snake_length > 20:
                print(f"警告: initial_snake_length 值无效 ({snake_length})，使用默认值 3")
                game_settings['initial_snake_length'] = 3
            
            # 验证难度设置
            difficulty = game_settings.get('difficulty', 'normal')
            if difficulty not in ['easy', 'normal', 'hard']:
                print(f"警告: difficulty 值无效 ({difficulty})，使用默认值 'normal'")
                game_settings['difficulty'] = 'normal'
            
            # 验证音效设置
            sound_settings = self.config.get('sound_settings', {})
            volume = sound_settings.get('volume', 0.5)
            if not isinstance(volume, (int, float)) or volume < 0.0 or volume > 1.0:
                print(f"警告: volume 值无效 ({volume})，使用默认值 0.5")
                sound_settings['volume'] = 0.5
            
            # 验证颜色设置
            colors = self.config.get('colors', {})
            for color_name, color_value in colors.items():
                if not isinstance(color_value, list) or len(color_value) != 3:
                    print(f"警告: 颜色 {color_name} 格式无效，使用默认值")
                    continue
                for i, component in enumerate(color_value):
                    if not isinstance(component, int) or component < 0 or component > 255:
                        print(f"警告: 颜色 {color_name} 的分量 {i} 无效，使用默认值")
                        colors[color_name] = [0, 0, 0]  # 默认黑色
                        break
            
        except Exception as e:
            print(f"配置验证失败: {e}")
    
    def update_setting(self, section: str, key: str, value: Any) -> bool:
        """更新配置设置并验证
        
        Args:
            section: 配置节名
            key: 配置键名
            value: 新值
            
        Returns:
            是否更新成功
        """
        try:
            if section not in self.config:
                self.config[section] = {}
            
            old_value = self.config[section].get(key)
            self.config[section][key] = value
            
            # 重新验证配置
            self._validate_config()
            
            # 如果验证后值发生变化，说明新值无效
            if self.config[section][key] != value:
                print(f"设置 {section}.{key} 的值 {value} 无效，已恢复为 {self.config[section][key]}")
                return False
            
            return True
        except Exception as e:
            print(f"更新设置失败: {e}")
            return False
    
    def reset_to_defaults(self):
        """重置为默认配置"""
        self.config = self._get_default_config()
        self._apply_env_overrides()
        self._validate_config()
        print("配置已重置为默认值")
    
    def _get_default_config(self) -> Dict[str, Any]:
        """获取默认配置"""
        return {
            "game_settings": {
                "initial_fps": 10,
                "initial_snake_length": 3,
                "speed_increase_interval": 50,
                "speed_increase_amount": 2,
                "max_fps": 30,
                "show_grid": True,
                "difficulty": "normal",
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
    
    def save_config(self):
        """保存配置到文件"""
        try:
            # 创建备份
            if os.path.exists(self.config_file):
                backup_file = f"{self.config_file}.backup"
                with open(self.config_file, 'r', encoding='utf-8') as src:
                    with open(backup_file, 'w', encoding='utf-8') as dst:
                        dst.write(src.read())
            
            # 保存新配置
            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, indent=4, ensure_ascii=False)
            print(f"配置已保存到 {self.config_file}")
        except Exception as e:
            print(f"保存配置文件失败: {e}")
            # 尝试恢复备份
            backup_file = f"{self.config_file}.backup"
            if os.path.exists(backup_file):
                try:
                    with open(backup_file, 'r', encoding='utf-8') as src:
                        with open(self.config_file, 'w', encoding='utf-8') as dst:
                            dst.write(src.read())
                    print("已恢复配置文件备份")
                except:
                    print("恢复配置文件备份失败")


# 创建全局配置实例
game_config = GameConfig()