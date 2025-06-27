"""
贪吃蛇类实现
"""

import pygame
from typing import List, Tuple, Optional
from .constants import *


class Snake:
    """蛇类，处理蛇的移动、碰撞检测等"""
    
    def __init__(self, initial_length: int):
        """初始化蛇"""
        self.initial_length = initial_length
        self.reset()
    
    def reset(self):
        """重置蛇到初始状态"""
        # 蛇的初始位置（屏幕中央）
        start_x = GRID_WIDTH // 2
        start_y = GRID_HEIGHT // 2
        
        # 蛇身体，每个元素是一个(x, y)坐标
        self.body = []
        for i in range(self.initial_length):
            self.body.append((start_x - i, start_y))
        
        # 初始方向向右
        self.direction = RIGHT
        self.next_direction = RIGHT
        
        # 是否需要增长
        self.grow = False
    
    def update(self):
        """更新蛇的位置"""
        # 记录旧的尾部位置（用于脏矩形更新）
        old_tail = None
        if not self.grow and len(self.body) > 0:
            old_tail = self.body[-1]
        
        # 更新方向（防止直接反向）
        if self.next_direction != (-self.direction[0], -self.direction[1]):
            self.direction = self.next_direction
        
        # 计算新的头部位置
        head_x, head_y = self.body[0]
        new_head = (head_x + self.direction[0], head_y + self.direction[1])
        
        # 添加新头部
        self.body.insert(0, new_head)
        
        # 如果不需要增长，移除尾部
        if not self.grow:
            removed_tail = self.body.pop()
            # 标记旧尾部位置为脏区域
            if old_tail:
                from .render_optimizer import render_optimizer
                render_optimizer.mark_dirty_grid(old_tail[0], old_tail[1])
        else:
            self.grow = False
        
        # 标记新头部位置为脏区域
        from .render_optimizer import render_optimizer
        render_optimizer.mark_dirty_grid(new_head[0], new_head[1])
    
    def change_direction(self, new_direction):
        """改变蛇的移动方向"""
        self.next_direction = new_direction
    
    def eat_food(self):
        """蛇吃到食物"""
        self.grow = True
    
    def check_collision(self, allow_wall_pass=False):
        """检查碰撞
        
        Args:
            allow_wall_pass: 是否允许穿墙
        """
        head_x, head_y = self.body[0]
        
        # 检查是否撞墙（如果允许穿墙则不算碰撞）
        if not allow_wall_pass:
            if (head_x < 0 or head_x >= GRID_WIDTH or 
                head_y < 0 or head_y >= GRID_HEIGHT):
                return True
        
        # 检查是否撞到自己
        if (head_x, head_y) in self.body[1:]:
            return True
        
        return False
    
    def handle_wall_wrap(self):
        """处理穿墙效果"""
        head_x, head_y = self.body[0]
        new_x, new_y = head_x, head_y
        
        # 水平穿墙
        if head_x < 0:
            new_x = GRID_WIDTH - 1
        elif head_x >= GRID_WIDTH:
            new_x = 0
        
        # 垂直穿墙
        if head_y < 0:
            new_y = GRID_HEIGHT - 1
        elif head_y >= GRID_HEIGHT:
            new_y = 0
        
        # 更新蛇头位置
        if new_x != head_x or new_y != head_y:
            self.body[0] = (new_x, new_y)
            return True  # 发生了穿墙
        
        return False  # 没有穿墙
    
    def get_head_position(self):
        """获取蛇头位置"""
        return self.body[0]
    
    def draw(self, screen):
        """绘制蛇"""
        for i, segment in enumerate(self.body):
            x = segment[0] * GRID_SIZE
            y = segment[1] * GRID_SIZE
            
            if i == 0:
                # 蛇头：更大，带眼睛
                color = DARK_GREEN
                pygame.draw.rect(screen, color, (x, y, GRID_SIZE, GRID_SIZE))
                pygame.draw.rect(screen, BLACK, (x, y, GRID_SIZE, GRID_SIZE), 2)
                
                # 绘制眼睛
                eye_size = 3
                eye_offset = 5
                if self.direction == UP:
                    eye1_pos = (x + eye_offset, y + eye_offset)
                    eye2_pos = (x + GRID_SIZE - eye_offset, y + eye_offset)
                elif self.direction == DOWN:
                    eye1_pos = (x + eye_offset, y + GRID_SIZE - eye_offset)
                    eye2_pos = (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset)
                elif self.direction == LEFT:
                    eye1_pos = (x + eye_offset, y + eye_offset)
                    eye2_pos = (x + eye_offset, y + GRID_SIZE - eye_offset)
                else:  # RIGHT
                    eye1_pos = (x + GRID_SIZE - eye_offset, y + eye_offset)
                    eye2_pos = (x + GRID_SIZE - eye_offset, y + GRID_SIZE - eye_offset)
                
                pygame.draw.circle(screen, WHITE, eye1_pos, eye_size)
                pygame.draw.circle(screen, WHITE, eye2_pos, eye_size)
                pygame.draw.circle(screen, BLACK, eye1_pos, eye_size - 1)
                pygame.draw.circle(screen, BLACK, eye2_pos, eye_size - 1)
            else:
                # 蛇身：渐变效果
                alpha = max(100, 255 - i * 10)  # 越往后越透明
                color = GREEN
                pygame.draw.rect(screen, color, (x, y, GRID_SIZE, GRID_SIZE))
                # 添加边框
                pygame.draw.rect(screen, BLACK, (x, y, GRID_SIZE, GRID_SIZE), 1)
    
    def get_length(self):
        """获取蛇的长度"""
        return len(self.body)
