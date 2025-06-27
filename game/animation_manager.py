"""
动画管理器
提供各种动画效果
"""

import random
import pygame
import math
import time
from typing import List, Dict, Any, Callable, Optional, Tuple
from .constants import *


class Animation:
    """动画基类"""
    
    def __init__(self, duration: float, easing_func: Callable = None):
        """初始化动画
        
        Args:
            duration: 动画持续时间（秒）
            easing_func: 缓动函数
        """
        self.duration = duration
        self.start_time = time.time()
        self.is_finished = False
        self.easing_func = easing_func or self._linear
    
    def _linear(self, t: float) -> float:
        """线性缓动"""
        return t
    
    def _ease_in_out(self, t: float) -> float:
        """缓入缓出"""
        return 3 * t * t - 2 * t * t * t
    
    def _ease_out_bounce(self, t: float) -> float:
        """弹跳缓出"""
        if t < 1/2.75:
            return 7.5625 * t * t
        elif t < 2/2.75:
            t -= 1.5/2.75
            return 7.5625 * t * t + 0.75
        elif t < 2.5/2.75:
            t -= 2.25/2.75
            return 7.5625 * t * t + 0.9375
        else:
            t -= 2.625/2.75
            return 7.5625 * t * t + 0.984375
    
    def get_progress(self) -> float:
        """获取动画进度 (0.0 - 1.0)"""
        elapsed = time.time() - self.start_time
        progress = min(1.0, elapsed / self.duration)
        
        if progress >= 1.0:
            self.is_finished = True
        
        return self.easing_func(progress)
    
    def update(self) -> bool:
        """更新动画
        
        Returns:
            动画是否继续
        """
        return not self.is_finished
    
    def draw(self, screen: pygame.Surface):
        """绘制动画"""
        pass


class FadeAnimation(Animation):
    """淡入淡出动画"""
    
    def __init__(self, surface: pygame.Surface, start_alpha: int, 
                 end_alpha: int, duration: float, fade_in: bool = True):
        """初始化淡入淡出动画
        
        Args:
            surface: 要应用动画的表面
            start_alpha: 起始透明度 (0-255)
            end_alpha: 结束透明度 (0-255)
            duration: 动画持续时间
            fade_in: 是否为淡入动画
        """
        super().__init__(duration, self._ease_in_out)
        self.surface = surface
        self.start_alpha = start_alpha
        self.end_alpha = end_alpha
        self.fade_in = fade_in
        
        # 确保表面支持alpha
        self.surface = self.surface.convert_alpha()
    
    def update(self) -> bool:
        if self.is_finished:
            return False
        
        progress = self.get_progress()
        current_alpha = int(self.start_alpha + (self.end_alpha - self.start_alpha) * progress)
        self.surface.set_alpha(current_alpha)
        
        return not self.is_finished
    
    def draw(self, screen: pygame.Surface):
        """绘制淡入淡出效果"""
        # 淡入淡出效果已经应用到surface的alpha上
        pass


class ScaleAnimation(Animation):
    """缩放动画"""
    
    def __init__(self, start_scale: float, end_scale: float, duration: float,
                 center: Tuple[int, int] = None):
        """初始化缩放动画
        
        Args:
            start_scale: 起始缩放比例
            end_scale: 结束缩放比例
            duration: 动画持续时间
            center: 缩放中心点
        """
        super().__init__(duration, self._ease_out_bounce)
        self.start_scale = start_scale
        self.end_scale = end_scale
        self.center = center or (WINDOW_WIDTH // 2, WINDOW_HEIGHT // 2)
        self.current_scale = start_scale
    
    def update(self) -> bool:
        if self.is_finished:
            return False
        
        progress = self.get_progress()
        self.current_scale = self.start_scale + (self.end_scale - self.start_scale) * progress
        
        return not self.is_finished
    
    def get_current_scale(self) -> float:
        """获取当前缩放比例"""
        return self.current_scale


class SlideAnimation(Animation):
    """滑动动画"""
    
    def __init__(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int], 
                 duration: float):
        """初始化滑动动画
        
        Args:
            start_pos: 起始位置
            end_pos: 结束位置
            duration: 动画持续时间
        """
        super().__init__(duration, self._ease_in_out)
        self.start_pos = start_pos
        self.end_pos = end_pos
        self.current_pos = start_pos
    
    def update(self) -> bool:
        if self.is_finished:
            return False
        
        progress = self.get_progress()
        x = int(self.start_pos[0] + (self.end_pos[0] - self.start_pos[0]) * progress)
        y = int(self.start_pos[1] + (self.end_pos[1] - self.start_pos[1]) * progress)
        self.current_pos = (x, y)
        
        return not self.is_finished
    
    def get_current_pos(self) -> Tuple[int, int]:
        """获取当前位置"""
        return self.current_pos


class PulseAnimation(Animation):
    """脉冲动画"""
    
    def __init__(self, base_scale: float, pulse_scale: float, duration: float):
        """初始化脉冲动画
        
        Args:
            base_scale: 基础缩放
            pulse_scale: 脉冲缩放
            duration: 动画持续时间
        """
        super().__init__(duration)
        self.base_scale = base_scale
        self.pulse_scale = pulse_scale
        self.current_scale = base_scale
    
    def update(self) -> bool:
        progress = self.get_progress()
        # 使用正弦波创建脉冲效果
        pulse_factor = math.sin(progress * math.pi * 4) * 0.5 + 0.5
        self.current_scale = self.base_scale + (self.pulse_scale - self.base_scale) * pulse_factor
        
        # 脉冲动画可以循环
        if self.is_finished:
            self.start_time = time.time()
            self.is_finished = False
        
        return True
    
    def get_current_scale(self) -> float:
        """获取当前缩放比例"""
        return self.current_scale


class ParticleEffect:
    """粒子效果"""
    
    def __init__(self, pos: Tuple[int, int], color: Tuple[int, int, int],
                 count: int = 10, lifetime: float = 1.0):
        """初始化粒子效果
        
        Args:
            pos: 发射位置
            color: 粒子颜色
            count: 粒子数量
            lifetime: 粒子生命周期
        """
        self.particles = []
        self.lifetime = lifetime
        
        for _ in range(count):
            particle = {
                'x': pos[0],
                'y': pos[1],
                'vx': (random.random() - 0.5) * 200,  # 随机速度
                'vy': (random.random() - 0.5) * 200,
                'life': lifetime,
                'max_life': lifetime,
                'color': color,
                'size': random.randint(2, 6)
            }
            self.particles.append(particle)
    
    def update(self, dt: float) -> bool:
        """更新粒子
        
        Args:
            dt: 时间增量
            
        Returns:
            是否还有活跃粒子
        """
        active_particles = []
        
        for particle in self.particles:
            particle['life'] -= dt
            if particle['life'] > 0:
                # 更新位置
                particle['x'] += particle['vx'] * dt
                particle['y'] += particle['vy'] * dt
                
                # 应用重力
                particle['vy'] += 300 * dt
                
                active_particles.append(particle)
        
        self.particles = active_particles
        return len(self.particles) > 0
    
    def draw(self, screen: pygame.Surface):
        """绘制粒子"""
        for particle in self.particles:
            # 根据生命周期计算透明度
            alpha = int(255 * (particle['life'] / particle['max_life']))
            color = (*particle['color'], alpha)
            
            # 创建带透明度的表面
            particle_surface = pygame.Surface((particle['size'] * 2, particle['size'] * 2), pygame.SRCALPHA)
            pygame.draw.circle(particle_surface, color, 
                             (particle['size'], particle['size']), particle['size'])
            
            screen.blit(particle_surface, (int(particle['x'] - particle['size']), 
                                         int(particle['y'] - particle['size'])))


class AnimationManager:
    """动画管理器"""
    
    def __init__(self):
        """初始化动画管理器"""
        # 确保pygame已初始化
        if not pygame.get_init():
            pygame.init()
            
        self.animations: List[Animation] = []
        self.particle_effects: List[ParticleEffect] = []
        self.last_update_time = time.time()
    
    def add_animation(self, animation: Animation):
        """添加动画"""
        self.animations.append(animation)
    
    def add_particle_effect(self, effect: ParticleEffect):
        """添加粒子效果"""
        self.particle_effects.append(effect)
    
    def create_fade_in(self, surface: pygame.Surface, duration: float = 0.5) -> FadeAnimation:
        """创建淡入动画"""
        animation = FadeAnimation(surface, 0, 255, duration, True)
        self.add_animation(animation)
        return animation
    
    def create_fade_out(self, surface: pygame.Surface, duration: float = 0.5) -> FadeAnimation:
        """创建淡出动画"""
        animation = FadeAnimation(surface, 255, 0, duration, False)
        self.add_animation(animation)
        return animation
    
    def create_scale_animation(self, start_scale: float, end_scale: float, 
                              duration: float = 0.3) -> ScaleAnimation:
        """创建缩放动画"""
        animation = ScaleAnimation(start_scale, end_scale, duration)
        self.add_animation(animation)
        return animation
    
    def create_slide_animation(self, start_pos: Tuple[int, int], end_pos: Tuple[int, int],
                              duration: float = 0.5) -> SlideAnimation:
        """创建滑动动画"""
        animation = SlideAnimation(start_pos, end_pos, duration)
        self.add_animation(animation)
        return animation
    
    def create_pulse_animation(self, base_scale: float = 1.0, pulse_scale: float = 1.2,
                              duration: float = 1.0) -> PulseAnimation:
        """创建脉冲动画"""
        animation = PulseAnimation(base_scale, pulse_scale, duration)
        self.add_animation(animation)
        return animation
    
    def create_explosion_effect(self, pos: Tuple[int, int], color: Tuple[int, int, int] = RED):
        """创建爆炸效果"""
        effect = ParticleEffect(pos, color, count=15, lifetime=1.5)
        self.add_particle_effect(effect)
    
    def create_score_effect(self, pos: Tuple[int, int], color: Tuple[int, int, int] = GOLD):
        """创建得分效果"""
        effect = ParticleEffect(pos, color, count=8, lifetime=1.0)
        self.add_particle_effect(effect)
    
    def update(self):
        """更新所有动画"""
        current_time = time.time()
        dt = current_time - self.last_update_time
        self.last_update_time = current_time
        
        # 更新动画
        active_animations = []
        for animation in self.animations:
            if animation.update():
                active_animations.append(animation)
        self.animations = active_animations
        
        # 更新粒子效果
        active_effects = []
        for effect in self.particle_effects:
            if effect.update(dt):
                active_effects.append(effect)
        self.particle_effects = active_effects
    
    def draw(self, screen: pygame.Surface):
        """绘制所有动画效果"""
        # 绘制动画
        for animation in self.animations:
            animation.draw(screen)
        
        # 绘制粒子效果
        for effect in self.particle_effects:
            effect.draw(screen)
    
    def clear_all(self):
        """清除所有动画"""
        self.animations.clear()
        self.particle_effects.clear()
    
    def get_animation_count(self) -> int:
        """获取活跃动画数量"""
        return len(self.animations) + len(self.particle_effects)


# 创建全局动画管理器实例
animation_manager = AnimationManager()