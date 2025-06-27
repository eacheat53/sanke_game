"""
输入管理器
提供更好的输入处理和防抖功能
"""

import pygame
import time
from typing import Dict, Set, Callable, Optional
from .constants import *


class InputManager:
    """输入管理器"""
    
    def __init__(self):
        """初始化输入管理器"""
        self.pressed_keys: Set[int] = set()
        self.key_press_times: Dict[int, float] = {}
        self.key_repeat_delays: Dict[int, float] = {}
        self.key_callbacks: Dict[int, Callable] = {}
        
        # 默认防抖延迟（秒）
        self.default_debounce_delay = 0.1
        
        # 方向键特殊处理
        self.direction_keys = {
            pygame.K_UP: UP,
            pygame.K_DOWN: DOWN,
            pygame.K_LEFT: LEFT,
            pygame.K_RIGHT: RIGHT
        }
        
        # 最后一次方向改变的时间
        self.last_direction_change = 0
        self.direction_change_delay = 0.05  # 方向改变最小间隔
        
        # 组合键支持
        self.key_combinations: Dict[tuple, Callable] = {}
        
        # 长按检测
        self.long_press_threshold = 0.5  # 长按阈值（秒）
        self.long_press_callbacks: Dict[int, Callable] = {}
        self.long_press_triggered: Set[int] = set()
    
    def set_key_callback(self, key: int, callback: Callable, debounce_delay: float = None):
        """设置按键回调
        
        Args:
            key: 按键码
            callback: 回调函数
            debounce_delay: 防抖延迟，None使用默认值
        """
        self.key_callbacks[key] = callback
        if debounce_delay is not None:
            self.key_repeat_delays[key] = debounce_delay
    
    def set_long_press_callback(self, key: int, callback: Callable):
        """设置长按回调
        
        Args:
            key: 按键码
            callback: 长按回调函数
        """
        self.long_press_callbacks[key] = callback
    
    def set_key_combination(self, keys: tuple, callback: Callable):
        """设置组合键
        
        Args:
            keys: 按键组合元组
            callback: 回调函数
        """
        self.key_combinations[keys] = callback
    
    def handle_event(self, event: pygame.event.Event) -> bool:
        """处理输入事件
        
        Args:
            event: pygame事件
            
        Returns:
            事件是否被处理
        """
        if event.type == pygame.KEYDOWN:
            return self._handle_key_down(event.key)
        elif event.type == pygame.KEYUP:
            return self._handle_key_up(event.key)
        
        return False
    
    def _handle_key_down(self, key: int) -> bool:
        """处理按键按下事件"""
        current_time = time.time()
        
        # 检查防抖
        if key in self.key_press_times:
            delay = self.key_repeat_delays.get(key, self.default_debounce_delay)
            if current_time - self.key_press_times[key] < delay:
                return True  # 忽略重复按键
        
        # 记录按键状态
        self.pressed_keys.add(key)
        self.key_press_times[key] = current_time
        self.long_press_triggered.discard(key)  # 重置长按状态
        
        # 特殊处理方向键
        if key in self.direction_keys:
            if current_time - self.last_direction_change >= self.direction_change_delay:
                self.last_direction_change = current_time
                return self._handle_direction_key(key)
            else:
                return True  # 忽略过快的方向改变
        
        # 检查组合键
        if self._check_key_combinations():
            return True
        
        # 执行单键回调
        if key in self.key_callbacks:
            try:
                self.key_callbacks[key]()
                return True
            except Exception as e:
                print(f"按键回调执行失败 {key}: {e}")
        
        return False
    
    def _handle_key_up(self, key: int) -> bool:
        """处理按键释放事件"""
        self.pressed_keys.discard(key)
        self.long_press_triggered.discard(key)
        return False
    
    def _handle_direction_key(self, key: int) -> bool:
        """处理方向键"""
        direction = self.direction_keys[key]
        
        # 这里可以添加方向改变的回调
        if hasattr(self, 'direction_callback') and self.direction_callback:
            try:
                self.direction_callback(direction)
                return True
            except Exception as e:
                print(f"方向回调执行失败: {e}")
        
        return False
    
    def _check_key_combinations(self) -> bool:
        """检查组合键"""
        for key_combo, callback in self.key_combinations.items():
            if all(key in self.pressed_keys for key in key_combo):
                try:
                    callback()
                    return True
                except Exception as e:
                    print(f"组合键回调执行失败 {key_combo}: {e}")
        
        return False
    
    def update(self):
        """更新输入状态（每帧调用）"""
        current_time = time.time()
        
        # 检查长按
        for key in self.pressed_keys.copy():
            if key in self.long_press_callbacks and key not in self.long_press_triggered:
                if key in self.key_press_times:
                    if current_time - self.key_press_times[key] >= self.long_press_threshold:
                        self.long_press_triggered.add(key)
                        try:
                            self.long_press_callbacks[key]()
                        except Exception as e:
                            print(f"长按回调执行失败 {key}: {e}")
    
    def is_key_pressed(self, key: int) -> bool:
        """检查按键是否被按下
        
        Args:
            key: 按键码
            
        Returns:
            按键是否被按下
        """
        return key in self.pressed_keys
    
    def is_any_key_pressed(self, keys: list) -> bool:
        """检查是否有任意一个按键被按下
        
        Args:
            keys: 按键码列表
            
        Returns:
            是否有按键被按下
        """
        return any(key in self.pressed_keys for key in keys)
    
    def is_all_keys_pressed(self, keys: list) -> bool:
        """检查是否所有按键都被按下
        
        Args:
            keys: 按键码列表
            
        Returns:
            是否所有按键都被按下
        """
        return all(key in self.pressed_keys for key in keys)
    
    def get_pressed_keys(self) -> Set[int]:
        """获取当前按下的所有按键
        
        Returns:
            按键集合
        """
        return self.pressed_keys.copy()
    
    def clear_all(self):
        """清除所有输入状态"""
        self.pressed_keys.clear()
        self.key_press_times.clear()
        self.long_press_triggered.clear()
    
    def set_direction_callback(self, callback: Callable):
        """设置方向改变回调
        
        Args:
            callback: 方向改变回调函数，接受direction参数
        """
        self.direction_callback = callback
    
    def set_direction_change_delay(self, delay: float):
        """设置方向改变延迟
        
        Args:
            delay: 延迟时间（秒）
        """
        self.direction_change_delay = delay
    
    def get_input_statistics(self) -> Dict[str, int]:
        """获取输入统计信息
        
        Returns:
            统计信息字典
        """
        return {
            'pressed_keys_count': len(self.pressed_keys),
            'registered_callbacks': len(self.key_callbacks),
            'registered_combinations': len(self.key_combinations),
            'long_press_callbacks': len(self.long_press_callbacks)
        }


# 创建全局输入管理器实例
input_manager = InputManager()