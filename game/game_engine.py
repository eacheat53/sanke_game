"""
游戏引擎主类
"""

import pygame
import sys
import json
from .constants import *
from .snake import Snake
from .food import Food
from .sound_manager import SoundManager
from utils.helpers import load_high_score, save_high_score


class GameEngine:
    def __init__(self, initial_fps=None, initial_snake_length=None, sound_enabled=None, show_grid=None):
        """初始化游戏引擎"""
        pygame.init()
        
        self.config = self._load_config()
        
        # 应用传入的参数覆盖配置
        if initial_fps is not None:
            self.config['game_settings']['initial_fps'] = initial_fps
        if initial_snake_length is not None:
            self.config['game_settings']['initial_snake_length'] = initial_snake_length
        if sound_enabled is not None:
            self.config['sound_settings']['enabled'] = sound_enabled
        if show_grid is not None:
            self.config['game_settings']['show_grid'] = show_grid
        
        # 创建游戏窗口
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏 - Snake Game")
        
        # 创建时钟对象
        self.clock = pygame.time.Clock()
        
        # 初始化字体 - 使用系统字体支持中文
        try:
            # 尝试使用系统中文字体
            self.font = pygame.font.SysFont('simhei,microsoftyaheui,simsun,arial', FONT_SIZE)
            self.small_font = pygame.font.SysFont('simhei,microsoftyaheui,simsun,arial', SMALL_FONT_SIZE)
        except:
            # 如果系统字体不可用，使用默认字体
            self.font = pygame.font.Font(None, FONT_SIZE)
            self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
        
        # 游戏对象
        self.snake = Snake(self.config['game_settings']['initial_snake_length'])
        self.food = Food()
        
        # 游戏状态
        self.state = GAME_RUNNING
        self.score = 0
        self.high_score = load_high_score() # 加载最高分
        
        # 游戏速度相关
        self.current_fps = self.config['game_settings']['initial_fps'] # 初始帧率
        self.speed_increase_interval = self.config['game_settings']['speed_increase_interval'] # 每X分提高一次速度
        self.speed_increase_amount = self.config['game_settings']['speed_increase_amount'] # 每次提高X帧
        self.max_fps = self.config['game_settings']['max_fps'] # 最大帧率
        
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
        self.sound_manager.sound_enabled = self.config['sound_settings']['enabled']
        self.sound_manager.set_volume(self.config['sound_settings']['volume'])
        
        # 确保食物不在蛇身上
        self.food.respawn(self.snake.body)
    
    def handle_events(self):
        """处理游戏事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return False
                
                elif event.key == pygame.K_p: # 按P键暂停/恢复
                    if self.state == GAME_RUNNING:
                        self.state = GAME_PAUSED
                    elif self.state == GAME_PAUSED:
                        self.state = GAME_RUNNING
                
                elif self.state == GAME_RUNNING:
                    # 处理方向键
                    if event.key == pygame.K_UP:
                        self.snake.change_direction(UP)
                    elif event.key == pygame.K_DOWN:
                        self.snake.change_direction(DOWN)
                    elif event.key == pygame.K_LEFT:
                        self.snake.change_direction(LEFT)
                    elif event.key == pygame.K_RIGHT:
                        self.snake.change_direction(RIGHT)
                
                elif self.state == GAME_OVER:
                    # 游戏结束时按空格重新开始，按R键返回设置
                    if event.key == pygame.K_SPACE:
                        self.restart_game()
                    elif event.key == pygame.K_r:
                        return False  # 返回设置界面
        
        return True
    
    def update(self):
        """更新游戏逻辑"""
        if self.state == GAME_RUNNING:
            # 更新游戏时间
            self.game_time = (pygame.time.get_ticks() - self.start_time) // 1000
            # 更新蛇的位置
            self.snake.update()
            # 更新食物状态
            self.food.update()
            # 更新提示信息
            if self.message_timer > 0:
                self.message_timer -= 1
            
            # 检查是否吃到食物
            if self.snake.get_head_position() == self.food.get_position():
                self.snake.eat_food()
                food_value = self.food.get_value()
                self.score += food_value
                
                # 显示得分提示
                if food_value > 10:
                    self.show_message(f"特殊食物! +{food_value}分!", GOLD)
                else:
                    self.show_message(f"+{food_value}分", WHITE)
                
                self.food.respawn(self.snake.body)
                self.sound_manager.play_sound('eat_food') # 播放吃食物音效
                
                # 动态调整游戏速度
                if self.score > 0 and self.score % self.speed_increase_interval == 0:
                    self.current_fps = min(self.max_fps, self.current_fps + self.speed_increase_amount)
            
            # 检查碰撞
            if self.snake.check_collision():
                self.state = GAME_OVER
                self.sound_manager.play_sound('game_over') # 播放游戏结束音效
                if self.score > self.high_score:
                    self.high_score = self.score
                    save_high_score(self.high_score) # 保存最高分
    
    def draw(self):
        """绘制游戏画面"""
        # 清空屏幕
        self.screen.fill(BLACK)
        
        if self.state == GAME_RUNNING:
            # 绘制网格线（可选，根据配置决定）
            if self.config['game_settings']['show_grid']:
                self.draw_grid()
            
            # 绘制蛇和食物
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            
            # 绘制分数
            self.draw_score()
        
        elif self.state == GAME_PAUSED:
            # 绘制游戏内容（暂停时仍显示游戏画面）
            if self.config['game_settings']['show_grid']:
                self.draw_grid()
            self.snake.draw(self.screen)
            self.food.draw(self.screen)
            self.draw_score()
            # 绘制暂停覆盖层
            self.draw_paused()
        
        elif self.state == GAME_OVER:
            # 绘制游戏结束画面
            self.draw_game_over()
        
        # 更新显示
        pygame.display.flip()
    
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
        
        self.screen.blit(score_text, (10, 10))
        self.screen.blit(high_score_text, (10, 35))
        self.screen.blit(length_text, (10, 60))
        self.screen.blit(fps_text, (10, 85))
        self.screen.blit(time_text, (10, 110))
        
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
        
        # 游戏结束文本
        game_over_text = self.font.render("游戏结束!", True, RED)
        score_text = self.font.render(f"最终分数: {self.score}", True, WHITE)
        high_score_text = self.font.render(f"最高分: {self.high_score}", True, WHITE)
        restart_text = self.small_font.render("按空格键重新开始", True, WHITE)
        settings_text = self.small_font.render("按R键返回设置", True, ORANGE)
        quit_text = self.small_font.render("按ESC键退出", True, WHITE)
        
        # 居中显示文本
        texts = [game_over_text, score_text, high_score_text, restart_text, settings_text, quit_text]
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
        self.current_fps = self.config['game_settings']['initial_fps']
        # 重置游戏时间
        self.start_time = pygame.time.get_ticks()
        self.game_time = 0
        # 清除提示信息
        self.message = ""
        self.message_timer = 0
    
    def _load_config(self, config_file="config.json"):
        """加载配置文件"""
        try:
            with open(config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except FileNotFoundError:
            print(f"警告: 配置文件 {config_file} 不存在，使用默认配置。")
            return {
                "game_settings": {
                    "initial_fps": 10,
                    "initial_snake_length": 3,
                    "speed_increase_interval": 50,
                    "speed_increase_amount": 2,
                    "max_fps": 30,
                    "show_grid": true
                },
                "sound_settings": {
                    "enabled": true,
                    "volume": 0.5
                }
            }
        except json.JSONDecodeError as e:
            print(f"错误: 解析配置文件 {config_file} 失败: {e}，使用默认配置。")
            return {
                "game_settings": {
                    "initial_fps": 10,
                    "initial_snake_length": 3,
                    "speed_increase_interval": 50,
                    "speed_increase_amount": 2,
                    "max_fps": 30,
                    "show_grid": true
                },
                "sound_settings": {
                    "enabled": true,
                    "volume": 0.5
                }
            }
    
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
            
            # 控制帧率
            self.clock.tick(self.current_fps) # 使用动态帧率
        
        # 游戏结束，不退出程序，返回到调用者
    
    def show_message(self, text, color=WHITE):
        """显示提示信息"""
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
