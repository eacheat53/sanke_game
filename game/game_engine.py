"""
游戏引擎主类
"""

import pygame
import sys
import json
import random
import time
from typing import Dict, List, Tuple, Optional, Any, Set, Union
from .constants import *
from .snake import Snake
from .food import Food
from .sound_manager import SoundManager
from utils.helpers import load_high_score, save_high_score

# 确保pygame初始化
pygame.init()
pygame.font.init()

# 导入管理器实例
from .resource_manager import resource_manager
from .render_optimizer import render_optimizer
from .save_manager import save_manager
from .game_modes import game_mode_manager
from .achievement_system import achievement_system
from .animation_manager import animation_manager
from .input_manager import input_manager


class GameEngine:
    """游戏引擎主类，负责游戏逻辑和渲染"""
    
    def __init__(self, initial_fps: Optional[int] = None, 
                initial_snake_length: Optional[int] = None, 
                sound_enabled: Optional[bool] = None, 
                show_grid: Optional[bool] = None):
        """初始化游戏引擎"""
        # pygame已在模块级别初始化
        
        # 使用统一的配置管理器
        from game_config import game_config
        self.config = game_config
        
        # 应用传入的参数覆盖配置
        if initial_fps is not None:
            self.config.config['game_settings']['initial_fps'] = initial_fps
        if initial_snake_length is not None:
            self.config.config['game_settings']['initial_snake_length'] = initial_snake_length
        if sound_enabled is not None:
            self.config.config['sound_settings']['enabled'] = sound_enabled
        if show_grid is not None:
            self.config.config['game_settings']['show_grid'] = show_grid
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏 - Snake Game")
        
        # 创建时钟对象
        self.clock = pygame.time.Clock()
        
        # 使用资源管理器获取字体
        self.font = resource_manager.get_font('system', FONT_SIZE)
        self.small_font = resource_manager.get_font('system', SMALL_FONT_SIZE)
        
        # 预加载常用文本
        resource_manager.preload_game_texts()
        
        # 游戏对象
        self.snake = Snake(self.config.get('game_settings', 'initial_snake_length'))
        self.food = Food()
        
        # 游戏状态
        self.state = GAME_RUNNING
        self.score = 0
        self.high_score = load_high_score() # 加载最高分
        
        # 功能性果实效果
        self.active_effects = {}
        self.next_score_multiplier = 1.0  # 下一次得分的倍数
        self.invincible_timer = 0  # 无敌时间
        
        # 游戏速度相关
        self.current_fps = self.config.get('game_settings', 'initial_fps') # 初始帧率
        self.speed_increase_interval = self.config.get('game_settings', 'speed_increase_interval') # 每X分提高一次速度
        self.speed_increase_amount = self.config.get('game_settings', 'speed_increase_amount') # 每次提高X帧
        self.max_fps = self.config.get('game_settings', 'max_fps') # 最大帧率
        
        # 游戏时间统计
        self.start_time = pygame.time.get_ticks()
        self.game_time = 0
        
        # 提示信息系统
        self.message = ""
        self.message_timer = 0
        self.message_duration = 120  # 提示显示时间（帧数）
        
        # 输入控制优化
        self.last_direction_change = 0
        self.direction_change_delay = 3  # 方向改变的最小间隔（帧数）
        
        # 初始化音效管理器并加载音效
        self.sound_manager = SoundManager()
        self.sound_manager.load_sound('eat_food', 'eat.wav')
        self.sound_manager.load_sound('game_over', 'game_over.wav')
        
        # 根据配置设置音效开关和音量
        self.sound_manager.sound_enabled = self.config.get('sound_settings', 'enabled')
        self.sound_manager.set_volume(self.config.get('sound_settings', 'volume'))
        
        # 确保食物不在蛇身上
        self.food.respawn(self.snake.body)
        
        # 初始化时标记全屏更新
        render_optimizer.mark_full_update()
        
        # 启动当前游戏模式
        game_mode_manager.start_current_mode(self)
        
        # 设置输入回调
        self._setup_input_callbacks()
        
        # 控制是否返回设置界面
        self._return_to_settings = False
    
    def handle_events(self) -> bool:
        """处理游戏事件
        
        Returns:
            是否继续游戏
        """
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            # 使用输入管理器处理事件
            if input_manager.handle_event(event):
                continue  # 事件已被处理
            
            # 处理其他事件
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
        
        # 更新输入管理器
        input_manager.update()
        
        return True
    
    def update(self):
        """更新游戏逻辑"""
        if self.state == GAME_RUNNING:
            # 更新游戏时间
            self.game_time = (pygame.time.get_ticks() - self.start_time) // 1000
            
            # 更新游戏模式
            if not game_mode_manager.update_current_mode(self):
                return  # 游戏模式要求结束
            
            # 更新蛇的位置
            self.snake.update()
            # 更新食物状态
            self.food.update()
            # 更新提示信息
            if self.message_timer > 0:
                self.message_timer -= 1
            
            # 更新动画
            animation_manager.update()
            
            # 更新功能性果实效果
            self._update_fruit_effects()
            
            # 检查是否吃到食物
            if self.snake.get_head_position() == self.food.get_position():
                # 标记旧食物位置为脏区域
                old_food_pos = self.food.get_position()
                render_optimizer.mark_dirty_grid(old_food_pos[0], old_food_pos[1])
                
                # 获取食物效果
                food_effect = self.food.get_effect()
                
                # 获取食物的增长段数
                growth = self.food.get_growth()
                
                # 根据增长段数多次调用eat_food
                for _ in range(growth):
                    self.snake.eat_food()
                
                food_value = self.food.get_value()
                
                # 应用功能性果实的分数倍数
                fruit_multiplier = self.next_score_multiplier
                self.next_score_multiplier = 1.0  # 重置
                
                # 应用游戏模式分数倍数
                mode_multiplier = game_mode_manager.get_current_mode().get_score_multiplier()
                final_score = int(food_value * mode_multiplier * fruit_multiplier)
                self.score += final_score
                
                # 处理功能性果实效果
                self._apply_fruit_effect(food_effect)
                
                # 显示得分提示和动画效果
                food_pos_pixel = (old_food_pos[0] * GRID_SIZE + GRID_SIZE // 2,
                                 old_food_pos[1] * GRID_SIZE + GRID_SIZE // 2)
                
                if fruit_multiplier > 1.0:
                    self.show_message(f"双倍分数! +{final_score}分!", (255, 100, 255))
                    animation_manager.create_score_effect(food_pos_pixel, (255, 100, 255))
                elif food_value > 10:
                    self.show_message(f"特殊食物! +{final_score}分!", GOLD)
                    animation_manager.create_score_effect(food_pos_pixel, GOLD)
                else:
                    self.show_message(f"+{final_score}分", WHITE)
                    animation_manager.create_score_effect(food_pos_pixel, GREEN)
                
                # 获取危险区域位置（用于生存模式）
                hazard_positions = self._get_hazard_positions()
                self.food.respawn(self.snake.body, hazard_positions)
                
                # 标记新食物位置为脏区域
                new_food_pos = self.food.get_position()
                render_optimizer.mark_dirty_grid(new_food_pos[0], new_food_pos[1])
                
                self.sound_manager.play_sound('eat_food') # 播放吃食物音效
                
                # 动态调整游戏速度
                if self.score > 0 and self.score % self.speed_increase_interval == 0:
                    self.current_fps = min(self.max_fps, self.current_fps + self.speed_increase_amount)
            
            # 检查碰撞（考虑无敌状态和禅模式穿墙）
            current_mode = game_mode_manager.get_current_mode()
            is_zen_mode = current_mode.name == "禅模式"
            
            if is_zen_mode:
                # 禅模式：处理穿墙效果
                if self.snake.handle_wall_wrap():
                    self.show_message("穿越边界!", BLUE)
                    current_mode.mode_data['zen_points'] = current_mode.mode_data.get('zen_points', 0) + 10
                
                # 禅模式只检查自身碰撞
                if self.snake.check_collision(allow_wall_pass=True) and self.invincible_timer <= 0:
                    self.state = GAME_OVER
                    self.sound_manager.play_sound('game_over')
            else:
                # 其他模式：正常碰撞检测
                if self.snake.check_collision() and self.invincible_timer <= 0:
                    self.state = GAME_OVER
                    self.sound_manager.play_sound('game_over') # 播放游戏结束音效
                    
                    # 标记全屏更新，确保蛇的尸体正确显示
                    render_optimizer.mark_full_update()
                    
                    # 创建爆炸效果
                    head_pos = self.snake.get_head_position()
                    head_pos_pixel = (head_pos[0] * GRID_SIZE + GRID_SIZE // 2, 
                                     head_pos[1] * GRID_SIZE + GRID_SIZE // 2)
                    animation_manager.create_explosion_effect(head_pos_pixel, RED)
                    
                    # 更新成就统计
                    self._update_achievements()
                    
                    if self.score > self.high_score:
                        self.high_score = self.score
                        save_high_score(self.high_score) # 保存最高分
                    
                    # 结束游戏模式
                    game_mode_manager.end_current_mode(self)
                    
                    # 显示游戏结束消息
                    self.show_message("游戏结束!", RED)
                    
                    # 根据用户要求，游戏结束时自动返回设置界面（主菜单）
                    self._return_to_settings = True
    
    def draw(self):
        """绘制游戏画面"""
        # 清空屏幕
        self.screen.fill(BLACK)
        
        if self.state == GAME_RUNNING:
            # 绘制网格线（可选，根据配置决定）
            if self.config.get('game_settings', 'show_grid'):
                self.draw_grid()
            
            # 绘制蛇和食物
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # 绘制环境危险（生存模式）
            self._draw_environmental_hazards()
            
            # 绘制分数
            self.draw_score()
        
        elif self.state == GAME_PAUSED:
            # 绘制游戏内容（暂停时仍显示游戏画面）
            if self.config.get('game_settings', 'show_grid'):
                self.draw_grid()
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            self.draw_score()
            # 绘制暂停覆盖层
            self.draw_paused()
        
        elif self.state == GAME_OVER:
            # 绘制游戏结束画面
            self.draw_game_over()
        
        # 绘制动画效果
        animation_manager.draw(self.screen)
        
        # 使用渲染优化器更新显示
        render_optimizer.update_display(self.screen)
    
    def draw_grid(self):
        """绘制网格线"""
        for x in range(0, WINDOW_WIDTH, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (x, 0), (x, WINDOW_HEIGHT))
        for y in range(0, WINDOW_HEIGHT, GRID_SIZE):
            pygame.draw.line(self.screen, GRAY, (0, y), (WINDOW_WIDTH, y))
    
    def draw_score(self):
        """绘制分数"""
        score_text = self.small_font.render(f"分数: {self.score}", True, WHITE)
        high_score_text = self.small_font.render(f"最高分: {self.high_score}", True, WHITE)
        length_text = self.small_font.render(f"长度: {self.snake.get_length()}", True, WHITE)
        fps_text = self.small_font.render(f"速度: {self.current_fps} FPS", True, WHITE)
        time_text = self.small_font.render(f"时间: {self.game_time}s", True, WHITE)
        
        # 获取当前游戏模式信息
        current_mode = game_mode_manager.get_current_mode()
        mode_text = self.small_font.render(f"模式: {current_mode.name}", True, ORANGE)
        multiplier = current_mode.get_score_multiplier()
        multiplier_text = self.small_font.render(f"倍数: {multiplier:.1f}x", True, GOLD)
        
        # 获取模式状态文本
        status_text_content = current_mode.get_status_text()
        if status_text_content:
            status_text = self.small_font.render(status_text_content, True, GREEN)
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 35))
        self.screen.blit(length_text, (10, 60))
        self.screen.blit(fps_text, (10, 85))
        self.screen.blit(time_text, (10, 110))
        self.screen.blit(mode_text, (10, 135))
        self.screen.blit(multiplier_text, (10, 160))
        
        # 绘制模式状态
        if status_text_content:
            self.screen.blit(status_text, (10, 185))
        
        # 绘制功能性果实状态
        y_offset = 210
        if self.next_score_multiplier > 1.0:
            next_bonus_text = self.small_font.render(f"下次分数: {self.next_score_multiplier:.1f}x", True, (255, 100, 255))
            self.screen.blit(next_bonus_text, (10, y_offset))
            y_offset += 25
        
        if self.invincible_timer > 0:
            invincible_text = self.small_font.render(f"无敌时间: {self.invincible_timer // 60 + 1}s", True, (255, 255, 0))
            self.screen.blit(invincible_text, (10, y_offset))
        
        # 绘制提示信息
        if self.message_timer > 0:
            self.draw_message()
    
    def draw_game_over(self):
        """绘制游戏结束画面"""
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 导入名言系统
        from .quotes import get_random_quote
        quote = get_random_quote()
        
        # 游戏结束文本
        game_over_text = self.font.render("游戏结束!", True, RED)
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        high_score_text = self.font.render(f"最高分: {self.high_score}", True, WHITE)
        
        # 名言显示（可能需要分行）
        quote_words = quote.split()
        quote_lines = []
        current_line = ""
        
        for word in quote_words:
            if len(current_line + " " + word) > 60:  # 控制每行字符数
                quote_lines.append(current_line)
                current_line = word
            else:
                current_line = current_line + " " + word if current_line else word
        
        if current_line:
            quote_lines.append(current_line)
            
        # 操作提示
        restart_text = self.small_font.render("按空格键重新开始", True, WHITE)
        settings_text = self.small_font.render("按R键返回设置", True, ORANGE)
        quit_text = self.small_font.render("按ESC键退出", True, WHITE)
        
        # 居中显示文本
        texts = [game_over_text, score_text, high_score_text]
        
        # 添加名言
        for line in quote_lines:
            quote_text = self.small_font.render(line, True, GOLD)
            texts.append(quote_text)
            
        # 添加操作提示
        texts.extend([restart_text, settings_text, quit_text])
        
        y_offset = WINDOW_HEIGHT // 2 - len(texts) * 30 // 2
        
        for i, text in enumerate(texts):
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + i * 35))
            self.screen.blit(text, text_rect)
    
    def restart_game(self):
        """重新开始游戏"""
        self.snake.reset()
        self.food.respawn(self.snake.body)
        self.score = 0
        self.state = GAME_RUNNING
        # 重置游戏速度到初始值
        self.current_fps = self.config.get('game_settings', 'initial_fps')
        # 重置游戏时间
        self.start_time = pygame.time.get_ticks()
        self.game_time = 0
        # 清除提示信息
        self.message = ""
        self.message_timer = 0
        
        # 重新启动游戏模式
        game_mode_manager.start_current_mode(self)
    
    
    def draw_paused(self):
        """绘制暂停画面"""
        # 半透明背景
        overlay = pygame.Surface((WINDOW_WIDTH, WINDOW_HEIGHT))
        overlay.set_alpha(128)
        overlay.fill(BLACK)
        self.screen.blit(overlay, (0, 0))
        
        # 暂停文本
        paused_text = self.font.render("游戏暂停", True, WHITE)
        resume_text = self.small_font.render("按P键继续", True, WHITE)
        
        # 居中显示文本
        texts = [paused_text, resume_text]
        y_offset = WINDOW_HEIGHT // 2 - len(texts) * 30 // 2
        
        for i, text in enumerate(texts):
            text_rect = text.get_rect(center=(WINDOW_WIDTH // 2, y_offset + i * 40))
            self.screen.blit(text, text_rect)
    
    def run(self):
        """运行游戏主循环"""
        running = True
        
        while running:
            # 处理事件
            running = self.handle_events()
            
            # 更新游戏逻辑
            self.update()
            
            # 绘制画面
            self.draw()
            
            # 如果游戏结束，显示游戏结束画面，但不立即退出
            if self.state == GAME_OVER:
                # 绘制游戏结束画面
                self.draw_game_over()
                pygame.display.flip()
                
                # 等待用户按键
                waiting_for_key = True
                while waiting_for_key and running:
                    for event in pygame.event.get():
                        if event.type == pygame.QUIT:
                            running = False
                            waiting_for_key = False
                        elif event.type == pygame.KEYDOWN:
                            if event.key == pygame.K_ESCAPE:
                                running = False
                                waiting_for_key = False
                            elif event.key == pygame.K_r:
                                self._return_to_settings = True
                                running = False
                                waiting_for_key = False
                            elif event.key == pygame.K_SPACE:
                                self.restart_game()
                                waiting_for_key = False
                    
                    # 控制帧率
                    self.clock.tick(10)  # 降低帧率以减少CPU使用
            
            # 控制帧率
            self.clock.tick(self.current_fps) # 使用动态帧率
        
        return self._return_to_settings
    
    def show_message(self, text: str, color: Tuple[int, int, int] = WHITE):
        """显示提示信息
        
        Args:
            text: 提示文本
            color: 文本颜色
        """
        self.message = text
        self.message_color = color
        self.message_timer = self.message_duration
    
    def draw_message(self):
        """绘制提示信息"""
        if self.message:
            message_surface = self.small_font.render(self.message, True, self.message_color)
            # 居中显示在屏幕上方
            x = (WINDOW_WIDTH - message_surface.get_width()) // 2
            y = 150
            self.screen.blit(message_surface, (x, y))
    
    def save_game(self, slot_name: str = None) -> bool:
        """保存游戏状态
        
        Args:
            slot_name: 存档槽名称
            
        Returns:
            是否保存成功
        """
        try:
            game_state = {
                'score': self.score,
                'snake_body': self.snake.body,
                'snake_direction': self.snake.direction,
                'food_position': self.food.position,
                'food_is_special': self.food.is_special,
                'food_special_timer': self.food.special_timer,
                'current_fps': self.current_fps,
                'game_time': self.game_time,
                'snake_length': self.snake.get_length(),
                'difficulty': game_mode_manager.get_current_mode().name,
                'mode_data': game_mode_manager.get_current_mode().mode_data
            }
            
            success = save_manager.save_game(game_state, slot_name)
            if success:
                self.show_message("游戏已保存!", GREEN)
            else:
                self.show_message("保存失败!", RED)
            return success
            
        except Exception as e:
            print(f"保存游戏失败: {e}")
            self.show_message("保存失败!", RED)
            return False
    
    def load_game(self, slot_name: str) -> bool:
        """加载游戏状态
        
        Args:
            slot_name: 存档槽名称
            
        Returns:
            是否加载成功
        """
        try:
            game_state = save_manager.load_game(slot_name)
            if not game_state:
                self.show_message("加载失败!", RED)
                return False
            
            # 恢复游戏状态
            self.score = game_state.get('score', 0)
            self.snake.body = game_state.get('snake_body', [(10, 10)])
            self.snake.direction = tuple(game_state.get('snake_direction', RIGHT))
            self.snake.next_direction = self.snake.direction
            
            self.food.position = tuple(game_state.get('food_position', (15, 15)))
            self.food.is_special = game_state.get('food_is_special', False)
            self.food.special_timer = game_state.get('food_special_timer', 0)
            
            self.current_fps = game_state.get('current_fps', 10)
            self.game_time = game_state.get('game_time', 0)
            
            # 恢复游戏模式数据
            mode_data = game_state.get('mode_data', {})
            game_mode_manager.get_current_mode().mode_data = mode_data
            
            self.state = GAME_RUNNING
            self.start_time = pygame.time.get_ticks() - self.game_time * 1000
            
            self.show_message("游戏已加载!", GREEN)
            render_optimizer.mark_full_update()
            return True
            
        except Exception as e:
            print(f"加载游戏失败: {e}")
            self.show_message("加载失败!", RED)
            return False
    
    def _update_achievements(self):
        """更新成就统计"""
        try:
            # 更新统计数据
            achievement_system.update_stats(
                total_games=1,
                total_score=self.score,
                highest_score=self.score,
                max_snake_length=self.snake.get_length(),
                max_game_time=self.game_time
            )
            
            # 保存成就进度
            achievement_system.save_achievements()
            
        except Exception as e:
            print(f"更新成就失败: {e}")
    
    def _setup_input_callbacks(self):
        """设置输入回调"""
        # 设置方向改变回调
        input_manager.set_direction_callback(self._on_direction_change)
        
        # 设置暂停键
        input_manager.set_key_callback(pygame.K_p, self._toggle_pause)
        
        # 设置游戏结束时的按键
        input_manager.set_key_callback(pygame.K_SPACE, self._on_space_key)
        input_manager.set_key_callback(pygame.K_r, self._on_return_key)
        input_manager.set_key_callback(pygame.K_s, self._on_save_key)
        
        # 设置方向改变延迟
        input_manager.set_direction_change_delay(0.05)
    
    def _on_direction_change(self, direction):
        """方向改变回调"""
        if self.state == GAME_RUNNING:
            self.snake.change_direction(direction)
    
    def _toggle_pause(self):
        """切换暂停状态"""
        if self.state == GAME_RUNNING:
            self.state = GAME_PAUSED
            self.show_message("游戏暂停", WHITE)
        elif self.state == GAME_PAUSED:
            self.state = GAME_RUNNING
            self.show_message("游戏继续", WHITE)
    
    def _on_space_key(self):
        """空格键回调"""
        pass # 清空原有逻辑
    
    def _on_return_key(self):
        """返回键回调"""
        pass # 清空原有逻辑
    
    def _on_save_key(self):
        """保存键回调"""
        if self.state == GAME_OVER:
            self.save_game()
    
    def _update_fruit_effects(self):
        """更新功能性果实效果"""
        # 更新无敌时间
        if self.invincible_timer > 0:
            self.invincible_timer -= 1
            if self.invincible_timer <= 0:
                self.show_message("无敌状态结束", WHITE)
    
    def _apply_fruit_effect(self, food_effect):
        """应用功能性果实效果"""
        effect_type = food_effect['type']
        effect_data = food_effect['data']
        
        if effect_type == 'double_score':
            self.next_score_multiplier = effect_data.get('next_score_multiplier', 2.0)
            self.show_message("下一个果实双倍分数!", (255, 100, 255))
            
        elif effect_type == 'speed_up':
            speed_change = effect_data.get('speed_change', 5)
            self.current_fps = min(50, self.current_fps + speed_change)
            self.show_message(f"速度提升! {self.current_fps} FPS", ORANGE)
            
        elif effect_type == 'speed_down':
            speed_change = effect_data.get('speed_change', -3)
            self.current_fps = max(5, self.current_fps + speed_change)
            self.show_message(f"速度减慢! {self.current_fps} FPS", BLUE)
            
        elif effect_type == 'length_double':
            # 蛇身长度翻倍
            current_length = len(self.snake.body)
            for _ in range(current_length):
                self.snake.eat_food()
            self.show_message("蛇身长度翻倍!", (0, 255, 255))
            
        elif effect_type == 'shrink':
            # 蛇身缩短
            if len(self.snake.body) > 3:
                shrink_count = max(1, len(self.snake.body) // 3)
                for _ in range(shrink_count):
                    if len(self.snake.body) > 3:
                        self.snake.body.pop()
                self.show_message(f"蛇身缩短 -{shrink_count}节!", PURPLE)
            
        elif effect_type == 'invincible':
            duration = effect_data.get('duration', 180)
            self.invincible_timer = duration
            self.show_message("获得无敌状态!", (255, 255, 0))
    
    def _get_hazard_positions(self):
        """获取危险区域位置（用于生存模式）"""
        hazard_positions = []
        current_mode = game_mode_manager.get_current_mode()
        
        if hasattr(current_mode, 'mode_data') and 'environmental_hazards' in current_mode.mode_data:
            for hazard in current_mode.mode_data['environmental_hazards']:
                hazard_pos = hazard.get('position')
                hazard_radius = hazard.get('radius', 1)
                
                # 添加危险区域及其周围的位置
                for dx in range(-hazard_radius, hazard_radius + 1):
                    for dy in range(-hazard_radius, hazard_radius + 1):
                        pos = (hazard_pos[0] + dx, hazard_pos[1] + dy)
                        if (0 <= pos[0] < GRID_WIDTH and 0 <= pos[1] < GRID_HEIGHT):
                            hazard_positions.append(pos)
        
        return hazard_positions
    
    def _draw_environmental_hazards(self):
        """绘制环境危险区域"""
        current_mode = game_mode_manager.get_current_mode()
        
        if hasattr(current_mode, 'mode_data') and 'environmental_hazards' in current_mode.mode_data:
            for hazard in current_mode.mode_data['environmental_hazards']:
                hazard_pos = hazard.get('position')
                hazard_type = hazard.get('type')
                hazard_radius = hazard.get('radius', 1)
                duration = hazard.get('duration', 0)
                
                # 计算透明度（剩余时间越少越透明）
                max_duration = 20 * self.current_fps if hazard_type == 'speed_trap' else 15 * self.current_fps
                alpha = min(255, int(255 * (duration / max_duration)))
                
                # 绘制危险区域
                for dx in range(-hazard_radius, hazard_radius + 1):
                    for dy in range(-hazard_radius, hazard_radius + 1):
                        distance = abs(dx) + abs(dy)  # 曼哈顿距离
                        if distance <= hazard_radius:
                            x = (hazard_pos[0] + dx) * GRID_SIZE
                            y = (hazard_pos[1] + dy) * GRID_SIZE
                            
                            # 检查是否在屏幕范围内
                            if (0 <= hazard_pos[0] + dx < GRID_WIDTH and 
                                0 <= hazard_pos[1] + dy < GRID_HEIGHT):
                                
                                # 创建带透明度的表面
                                hazard_surface = pygame.Surface((GRID_SIZE, GRID_SIZE))
                                hazard_surface.set_alpha(alpha // 2)  # 半透明效果
                                
                                if hazard_type == 'poison_zone':
                                    # 毒区：紫色，带毒气效果
                                    hazard_surface.fill(PURPLE)
                                    self.screen.blit(hazard_surface, (x, y))
                                    
                                    # 添加毒气粒子效果
                                    if duration % 20 < 10:  # 闪烁效果
                                        center_x = x + GRID_SIZE // 2
                                        center_y = y + GRID_SIZE // 2
                                        pygame.draw.circle(self.screen, (200, 0, 200), 
                                                         (center_x, center_y), 3)
                                
                                elif hazard_type == 'speed_trap':
                                    # 减速陷阱：蓝色，带漩涡效果
                                    hazard_surface.fill(BLUE)
                                    self.screen.blit(hazard_surface, (x, y))
                                    
                                    # 添加漩涡效果
                                    center_x = x + GRID_SIZE // 2
                                    center_y = y + GRID_SIZE // 2
                                    angle = (duration * 5) % 360
                                    for i in range(3):
                                        offset_angle = angle + i * 120
                                        offset_x = int(5 * pygame.math.Vector2(1, 0).rotate(offset_angle).x)
                                        offset_y = int(5 * pygame.math.Vector2(1, 0).rotate(offset_angle).y)
                                        pygame.draw.circle(self.screen, WHITE, 
                                                         (center_x + offset_x, center_y + offset_y), 2)
