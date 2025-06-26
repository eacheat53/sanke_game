"""
食物类实现
"""

import pygame
import random
from .constants import *


class Food:
    def __init__(self):
        """初始化食物"""
        self.position = self.generate_position()
        self.is_special = False  # 是否为特殊食物
        self.special_timer = 0   # 特殊食物计时器
        self.special_duration = 300  # 特殊食物持续时间（帧数）
    
    def generate_position(self):
        """生成随机食物位置"""
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
    
    def respawn(self, snake_body):
        """重新生成食物位置，确保不与蛇身重叠"""
        while True:
            new_position = self.generate_position()
            if new_position not in snake_body:
                self.position = new_position
                # 10%概率生成特殊食物
                self.is_special = random.random() < 0.1
                if self.is_special:
                    self.special_timer = self.special_duration
                break
    
    def draw(self, screen):
        """绘制食物"""
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        
        # 绘制圆形食物
        center_x = x + GRID_SIZE // 2
        center_y = y + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2
        
        if self.is_special:
            # 特殊食物：金色，带闪烁效果
            flash_intensity = abs((self.special_timer % 60) - 30) / 30.0
            gold_color = (255, int(215 * flash_intensity), 0)
            pygame.draw.circle(screen, gold_color, (center_x, center_y), radius)
            # 特殊高光
            pygame.draw.circle(screen, WHITE, (center_x - 2, center_y - 2), radius // 4)
        else:
            # 普通食物：红色
            pygame.draw.circle(screen, RED, (center_x, center_y), radius)
            # 添加高光效果
            pygame.draw.circle(screen, WHITE, (center_x - 3, center_y - 3), radius // 3)
    
    def get_position(self):
        """获取食物位置"""
        return self.position
    
    def update(self):
        """更新食物状态"""
        if self.is_special and self.special_timer > 0:
            self.special_timer -= 1
            if self.special_timer <= 0:
                self.is_special = False
    
    def get_value(self):
        """获取食物分值"""
        return 20 if self.is_special else 10