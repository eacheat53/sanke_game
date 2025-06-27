"""
食物类实现
"""

import pygame
import random
from typing import Tuple, List, Optional
from .constants import *


class Food:
    """食物类，处理食物的生成和显示"""
    
    # 功能性果实类型定义
    FRUIT_TYPES = {
        'normal': {'name': '普通果实', 'color': RED, 'probability': 0.70},
        'special': {'name': '特殊果实', 'color': GOLD, 'probability': 0.15},
        'double_score': {'name': '双倍分数', 'color': (255, 100, 255), 'probability': 0.05},
        'speed_up': {'name': '速度提升', 'color': ORANGE, 'probability': 0.03},
        'speed_down': {'name': '速度减慢', 'color': BLUE, 'probability': 0.03},
        'length_double': {'name': '长度翻倍', 'color': (0, 255, 255), 'probability': 0.02},
        'shrink': {'name': '蛇身缩短', 'color': PURPLE, 'probability': 0.015},
        'invincible': {'name': '短暂无敌', 'color': (255, 255, 0), 'probability': 0.005}
    }
    
    def __init__(self):
        """初始化食物"""
        self.position = self.generate_position()
        self.fruit_type = 'normal'
        self.special_timer = 0
        self.special_duration = 300  # 特殊食物持续时间（帧数）
        self.effect_data = {}  # 存储效果相关数据
    
    def generate_position(self) -> Tuple[int, int]:
        """生成随机食物位置
        
        Returns:
            食物位置坐标元组 (x, y)
        """
        x = random.randint(0, GRID_WIDTH - 1)
        y = random.randint(0, GRID_HEIGHT - 1)
        return (x, y)
    
    def respawn(self, snake_body: List[Tuple[int, int]], hazard_positions: List[Tuple[int, int]] = None):
        """重新生成食物位置，确保不与蛇身和危险区域重叠
        
        Args:
            snake_body: 蛇身体坐标列表
            hazard_positions: 危险区域坐标列表
        """
        if hazard_positions is None:
            hazard_positions = []
            
        while True:
            new_position = self.generate_position()
            if (new_position not in snake_body and 
                new_position not in hazard_positions):
                self.position = new_position
                self._generate_fruit_type()
                break
    
    def _generate_fruit_type(self):
        """根据概率生成果实类型"""
        rand = random.random()
        cumulative_prob = 0
        
        for fruit_type, data in self.FRUIT_TYPES.items():
            cumulative_prob += data['probability']
            if rand <= cumulative_prob:
                self.fruit_type = fruit_type
                if fruit_type != 'normal':
                    self.special_timer = self.special_duration
                else:
                    self.special_timer = 0
                break
        
        # 初始化效果数据
        self.effect_data = {}
        if self.fruit_type == 'double_score':
            self.effect_data['next_score_multiplier'] = 2.0
        elif self.fruit_type == 'speed_up':
            self.effect_data['speed_change'] = 5
        elif self.fruit_type == 'speed_down':
            self.effect_data['speed_change'] = -3
        elif self.fruit_type == 'invincible':
            self.effect_data['duration'] = 180  # 3秒无敌
    
    def draw(self, screen):
        """绘制食物"""
        x = self.position[0] * GRID_SIZE
        y = self.position[1] * GRID_SIZE
        
        # 绘制圆形食物
        center_x = x + GRID_SIZE // 2
        center_y = y + GRID_SIZE // 2
        radius = GRID_SIZE // 2 - 2
        
        fruit_data = self.FRUIT_TYPES[self.fruit_type]
        color = fruit_data['color']
        
        if self.fruit_type != 'normal':
            # 特殊食物：带闪烁效果
            flash_intensity = abs((self.special_timer % 60) - 30) / 30.0
            if isinstance(color, tuple) and len(color) == 3:
                flash_color = (
                    int(color[0] * (0.7 + 0.3 * flash_intensity)),
                    int(color[1] * (0.7 + 0.3 * flash_intensity)),
                    int(color[2] * (0.7 + 0.3 * flash_intensity))
                )
            else:
                flash_color = color
            pygame.draw.circle(screen, flash_color, (center_x, center_y), radius)
            
            # 特殊标记
            if self.fruit_type == 'double_score':
                # 双倍分数：绘制"2x"
                font = pygame.font.Font(None, 16)
                text = font.render("2x", True, WHITE)
                text_rect = text.get_rect(center=(center_x, center_y))
                screen.blit(text, text_rect)
            elif self.fruit_type == 'speed_up':
                # 速度提升：向上箭头
                pygame.draw.polygon(screen, WHITE, [
                    (center_x, center_y - 5),
                    (center_x - 3, center_y + 2),
                    (center_x + 3, center_y + 2)
                ])
            elif self.fruit_type == 'speed_down':
                # 速度减慢：向下箭头
                pygame.draw.polygon(screen, WHITE, [
                    (center_x, center_y + 5),
                    (center_x - 3, center_y - 2),
                    (center_x + 3, center_y - 2)
                ])
            elif self.fruit_type == 'length_double':
                # 长度翻倍：绘制"+"
                pygame.draw.line(screen, WHITE, (center_x - 4, center_y), (center_x + 4, center_y), 2)
                pygame.draw.line(screen, WHITE, (center_x, center_y - 4), (center_x, center_y + 4), 2)
            elif self.fruit_type == 'shrink':
                # 蛇身缩短：绘制"-"
                pygame.draw.line(screen, WHITE, (center_x - 4, center_y), (center_x + 4, center_y), 2)
            elif self.fruit_type == 'invincible':
                # 无敌：绘制星形
                points = []
                for i in range(5):
                    angle = i * 72 - 90
                    outer_x = center_x + int(4 * pygame.math.Vector2(1, 0).rotate(angle).x)
                    outer_y = center_y + int(4 * pygame.math.Vector2(1, 0).rotate(angle).y)
                    points.append((outer_x, outer_y))
                pygame.draw.polygon(screen, WHITE, points)
            
            # 特殊高光
            pygame.draw.circle(screen, WHITE, (center_x - 2, center_y - 2), radius // 4)
        else:
            # 普通食物：红色
            pygame.draw.circle(screen, color, (center_x, center_y), radius)
            # 添加高光效果
            pygame.draw.circle(screen, WHITE, (center_x - 3, center_y - 3), radius // 3)
    
    def get_position(self):
        """获取食物位置"""
        return self.position
    
    def update(self):
        """更新食物状态"""
        if self.fruit_type != 'normal' and self.special_timer > 0:
            old_timer = self.special_timer
            self.special_timer -= 1
            if self.special_timer <= 0:
                self.fruit_type = 'normal'
                # 特殊食物状态改变时标记为脏区域
                from .render_optimizer import render_optimizer
                render_optimizer.mark_dirty_grid(self.position[0], self.position[1])
            elif old_timer % 10 == 0:  # 每10帧更新一次闪烁效果
                from .render_optimizer import render_optimizer
                render_optimizer.mark_dirty_grid(self.position[0], self.position[1])
    
    def get_value(self):
        """获取食物分值"""
        if self.fruit_type == 'special':
            return 20
        elif self.fruit_type in ['double_score', 'length_double', 'invincible']:
            return 30
        elif self.fruit_type in ['speed_up', 'speed_down']:
            return 15
        elif self.fruit_type == 'shrink':
            return 5  # 负面效果，分数较低
        else:
            return 10  # 普通食物
    
    def get_growth(self):
        """获取食物导致的增长段数"""
        if self.fruit_type == 'special':
            return 2  # 特殊果实增加2段
        elif self.fruit_type == 'length_double':
            return 0  # 长度翻倍果实通过特殊效果处理
        else:
            return 1  # 普通果实增加1段
    
    def get_effect(self):
        """获取食物效果"""
        return {
            'type': self.fruit_type,
            'data': self.effect_data.copy()
        }