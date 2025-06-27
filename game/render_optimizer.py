"""
渲染优化器
实现脏矩形更新和渲染优化
"""

import pygame
from typing import List, Set, Tuple, Optional
from .constants import *


class DirtyRect:
    """脏矩形类"""
    
    def __init__(self, x: int, y: int, width: int, height: int):
        self.rect = pygame.Rect(x, y, width, height)
        self.merged = False
    
    def intersects(self, other: 'DirtyRect') -> bool:
        """检查是否与另一个脏矩形相交"""
        return self.rect.colliderect(other.rect)
    
    def merge(self, other: 'DirtyRect') -> 'DirtyRect':
        """合并两个脏矩形"""
        union_rect = self.rect.union(other.rect)
        return DirtyRect(union_rect.x, union_rect.y, union_rect.width, union_rect.height)


class RenderOptimizer:
    """渲染优化器"""
    
    def __init__(self, screen_width: int, screen_height: int):
        """初始化渲染优化器
        
        Args:
            screen_width: 屏幕宽度
            screen_height: 屏幕高度
        """
        # 确保pygame已初始化
        if not pygame.get_init():
            pygame.init()
        self.screen_width = screen_width
        self.screen_height = screen_height
        self.dirty_rects: List[DirtyRect] = []
        self.full_update = True  # 首次渲染需要全屏更新
        
        # 性能统计
        self.frame_count = 0
        self.dirty_rect_count = 0
        self.merge_count = 0
    
    def mark_dirty(self, x: int, y: int, width: int, height: int):
        """标记脏矩形区域
        
        Args:
            x: 左上角x坐标
            y: 左上角y坐标
            width: 宽度
            height: 高度
        """
        # 确保坐标在屏幕范围内
        x = max(0, min(x, self.screen_width))
        y = max(0, min(y, self.screen_height))
        width = min(width, self.screen_width - x)
        height = min(height, self.screen_height - y)
        
        if width <= 0 or height <= 0:
            return
        
        dirty_rect = DirtyRect(x, y, width, height)
        self.dirty_rects.append(dirty_rect)
        self.dirty_rect_count += 1
    
    def mark_dirty_grid(self, grid_x: int, grid_y: int, grid_count_x: int = 1, grid_count_y: int = 1):
        """标记网格单元为脏区域
        
        Args:
            grid_x: 网格x坐标
            grid_y: 网格y坐标
            grid_count_x: x方向网格数量
            grid_count_y: y方向网格数量
        """
        x = grid_x * GRID_SIZE
        y = grid_y * GRID_SIZE
        width = grid_count_x * GRID_SIZE
        height = grid_count_y * GRID_SIZE
        self.mark_dirty(x, y, width, height)
    
    def mark_full_update(self):
        """标记需要全屏更新"""
        self.full_update = True
        self.dirty_rects.clear()
    
    def optimize_dirty_rects(self) -> List[pygame.Rect]:
        """优化脏矩形，合并重叠的区域
        
        Returns:
            优化后的矩形列表
        """
        if self.full_update:
            self.full_update = False
            return [pygame.Rect(0, 0, self.screen_width, self.screen_height)]
        
        if not self.dirty_rects:
            return []
        
        # 合并重叠的脏矩形
        merged_rects = []
        unprocessed = self.dirty_rects.copy()
        
        while unprocessed:
            current = unprocessed.pop(0)
            merged = False
            
            # 尝试与已合并的矩形合并
            for i, merged_rect in enumerate(merged_rects):
                if current.intersects(merged_rect):
                    merged_rects[i] = current.merge(merged_rect)
                    merged = True
                    self.merge_count += 1
                    break
            
            if not merged:
                merged_rects.append(current)
        
        # 清除脏矩形列表
        self.dirty_rects.clear()
        
        # 转换为pygame.Rect列表
        return [rect.rect for rect in merged_rects]
    
    def should_use_dirty_rects(self) -> bool:
        """判断是否应该使用脏矩形更新
        
        Returns:
            是否使用脏矩形更新
        """
        # 如果脏矩形太多，直接全屏更新可能更高效
        if len(self.dirty_rects) > 10:
            return False
        
        # 计算脏矩形总面积
        total_dirty_area = sum(rect.rect.width * rect.rect.height for rect in self.dirty_rects)
        screen_area = self.screen_width * self.screen_height
        
        # 如果脏区域超过屏幕面积的50%，使用全屏更新
        return total_dirty_area < screen_area * 0.5
    
    def update_display(self, screen: pygame.Surface) -> int:
        """更新显示，返回更新的矩形数量
        
        Args:
            screen: 屏幕表面
            
        Returns:
            更新的矩形数量
        """
        self.frame_count += 1
        
        if not self.should_use_dirty_rects():
            pygame.display.flip()
            self.dirty_rects.clear()
            return 1
        
        dirty_rects = self.optimize_dirty_rects()
        if dirty_rects:
            pygame.display.update(dirty_rects)
            return len(dirty_rects)
        else:
            return 0
    
    def get_performance_stats(self) -> dict:
        """获取性能统计信息
        
        Returns:
            性能统计字典
        """
        return {
            'frame_count': self.frame_count,
            'dirty_rect_count': self.dirty_rect_count,
            'merge_count': self.merge_count,
            'avg_dirty_rects_per_frame': self.dirty_rect_count / max(1, self.frame_count),
            'avg_merges_per_frame': self.merge_count / max(1, self.frame_count)
        }
    
    def reset_stats(self):
        """重置性能统计"""
        self.frame_count = 0
        self.dirty_rect_count = 0
        self.merge_count = 0


# 创建全局渲染优化器实例
render_optimizer = RenderOptimizer(WINDOW_WIDTH, WINDOW_HEIGHT)