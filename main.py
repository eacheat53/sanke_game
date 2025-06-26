#!/usr/bin/env python3
"""
贪吃蛇游戏启动页面
简洁的游戏参数设置界面
"""

import pygame
import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from game.constants import *
from game.game_engine import GameEngine
from utils.helpers import check_pygame_installation


class GameStartScreen:
    """游戏开始页面类"""
    
    def __init__(self):
        """初始化游戏开始页面"""
        pygame.init()
        
        # 创建窗口
        self.screen = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
        pygame.display.set_caption("贪吃蛇游戏 - 游戏设置")
        
        # 创建时钟
        self.clock = pygame.time.Clock()
        
        # 初始化字体
        try:
            self.font = pygame.font.SysFont('simhei,microsoftyaheui,simsun,arial', FONT_SIZE)
            self.small_font = pygame.font.SysFont('simhei,microsoftyaheui,simsun,arial', SMALL_FONT_SIZE)
            self.title_font = pygame.font.SysFont('simhei,microsoftyaheui,simsun,arial', 48)
        except:
            self.font = pygame.font.Font(None, FONT_SIZE)
            self.small_font = pygame.font.Font(None, SMALL_FONT_SIZE)
            self.title_font = pygame.font.Font(None, 48)
        
        # 游戏设置
        self.settings = {
            'difficulty': 'normal',  # easy, normal, hard
            'speed': 10,             # 游戏速度 (FPS)
            'snake_length': 3,       # 初始蛇长度
            'sound_enabled': True,   # 音效开关
            'show_grid': True        # 显示网格
        }
        
        # 当前选中的设置项
        self.selected_setting = 0
        self.setting_names = [
            '游戏难度',
            '游戏速度', 
            '初始蛇长',
            '音效开关',
            '显示网格',
            '开始游戏'
        ]
        
        # 设置选项
        self.difficulty_options = ['简单', '普通', '困难']
        self.difficulty_values = ['easy', 'normal', 'hard']
        
        # 运行状态
        self.running = True
        self.start_game = False
    
    def handle_events(self):
        """处理事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
                return False
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                    return False
                
                elif event.key == pygame.K_UP:
                    self.selected_setting = (self.selected_setting - 1) % len(self.setting_names)
                
                elif event.key == pygame.K_DOWN:
                    self.selected_setting = (self.selected_setting + 1) % len(self.setting_names)
                
                elif event.key == pygame.K_LEFT:
                    self.adjust_setting(False)
                
                elif event.key == pygame.K_RIGHT:
                    self.adjust_setting(True)
                
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_setting == len(self.setting_names) - 1:  # 开始游戏
                        self.start_game = True
                        self.running = False
                        return False
                    else:
                        self.adjust_setting(True)
        
        return True
    
    def adjust_setting(self, increase):
        """调整设置"""
        if self.selected_setting == 0:  # 游戏难度
            current_index = self.difficulty_values.index(self.settings['difficulty'])
            if increase:
                new_index = (current_index + 1) % len(self.difficulty_values)
            else:
                new_index = (current_index - 1) % len(self.difficulty_values)
            self.settings['difficulty'] = self.difficulty_values[new_index]
            
            # 根据难度自动调整速度
            if self.settings['difficulty'] == 'easy':
                self.settings['speed'] = 8
            elif self.settings['difficulty'] == 'normal':
                self.settings['speed'] = 10
            else:  # hard
                self.settings['speed'] = 15
        
        elif self.selected_setting == 1:  # 游戏速度
            if increase:
                self.settings['speed'] = min(30, self.settings['speed'] + 2)
            else:
                self.settings['speed'] = max(5, self.settings['speed'] - 2)
        
        elif self.selected_setting == 2:  # 初始蛇长
            if increase:
                self.settings['snake_length'] = min(10, self.settings['snake_length'] + 1)
            else:
                self.settings['snake_length'] = max(1, self.settings['snake_length'] - 1)
        
        elif self.selected_setting == 3:  # 音效开关
            self.settings['sound_enabled'] = not self.settings['sound_enabled']
        
        elif self.selected_setting == 4:  # 显示网格
            self.settings['show_grid'] = not self.settings['show_grid']
    
    def get_setting_value_text(self, setting_index):
        """获取设置值的显示文本"""
        if setting_index == 0:  # 游戏难度
            difficulty_index = self.difficulty_values.index(self.settings['difficulty'])
            return self.difficulty_options[difficulty_index]
        elif setting_index == 1:  # 游戏速度
            return f"{self.settings['speed']} FPS"
        elif setting_index == 2:  # 初始蛇长
            return f"{self.settings['snake_length']} 节"
        elif setting_index == 3:  # 音效开关
            return "开启" if self.settings['sound_enabled'] else "关闭"
        elif setting_index == 4:  # 显示网格
            return "显示" if self.settings['show_grid'] else "隐藏"
        else:
            return ""
    
    def draw(self):
        """绘制界面"""
        self.screen.fill(BLACK)
        
        # 绘制标题
        title_text = self.title_font.render("🐍 贪吃蛇游戏设置 🐍", True, GREEN)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # 绘制设置项
        start_y = 180
        for i, setting_name in enumerate(self.setting_names):
            y_pos = start_y + i * 50
            
            # 设置项名称
            if i == self.selected_setting:
                color = WHITE
                prefix = "► "
                suffix = " ◄"
            else:
                color = GRAY
                prefix = "  "
                suffix = "  "
            
            if i < len(self.setting_names) - 1:  # 不是"开始游戏"按钮
                # 设置名称
                name_text = self.font.render(f"{prefix}{setting_name}:", True, color)
                name_rect = name_text.get_rect(center=(WINDOW_WIDTH // 2 - 100, y_pos))
                self.screen.blit(name_text, name_rect)
                
                # 设置值
                value_text = self.get_setting_value_text(i)
                value_surface = self.font.render(value_text, True, color)
                value_rect = value_surface.get_rect(center=(WINDOW_WIDTH // 2 + 100, y_pos))
                self.screen.blit(value_surface, value_rect)
            else:
                # "开始游戏"按钮
                button_text = self.font.render(f"{prefix}{setting_name}{suffix}", True, color)
                button_rect = button_text.get_rect(center=(WINDOW_WIDTH // 2, y_pos))
                self.screen.blit(button_text, button_rect)
        
        # 绘制操作提示
        help_lines = [
            "操作说明:",
            "↑↓ - 选择设置项",
            "←→ - 调整设置值", 
            "回车 - 确认/开始游戏",
            "ESC - 退出"
        ]
        
        help_start_y = WINDOW_HEIGHT - 120
        for i, line in enumerate(help_lines):
            color = ORANGE if i == 0 else GRAY
            help_text = self.small_font.render(line, True, color)
            help_rect = help_text.get_rect(center=(WINDOW_WIDTH // 2, help_start_y + i * 20))
            self.screen.blit(help_text, help_rect)
        
        pygame.display.flip()
    
    def run(self):
        """运行游戏开始页面"""
        while self.running:
            if not self.handle_events():
                break
            
            self.draw()
            self.clock.tick(30)
        
        return self.start_game, self.settings


class GameApplication:
    """游戏应用主类 - 管理设置界面和游戏循环"""
    
    def __init__(self):
        """初始化游戏应用"""
        # 检查pygame是否安装
        if not check_pygame_installation():
            sys.exit(1)
        
        pygame.init()
        self.running = True
        
        print("=" * 50)
        print("🐍 欢迎来到贪吃蛇游戏! 🐍")
        print("=" * 50)
        print("正在启动游戏...")
    
    def run(self):
        """运行游戏应用主循环"""
        try:
            while self.running:
                # 显示设置界面
                start_screen = GameStartScreen()
                should_start, settings = start_screen.run()
                
                if not should_start:
                    # 用户选择退出
                    self.running = False
                    break
                
                # 显示游戏设置
                print("\n游戏设置:")
                print(f"难度: {settings['difficulty']}")
                print(f"速度: {settings['speed']} FPS")
                print(f"初始蛇长: {settings['snake_length']} 节")
                print(f"音效: {'开启' if settings['sound_enabled'] else '关闭'}")
                print(f"网格: {'显示' if settings['show_grid'] else '隐藏'}")
                print("\n正在启动游戏...")
                
                # 创建并运行游戏
                game = GameEngine(
                    initial_fps=settings['speed'],
                    initial_snake_length=settings['snake_length'],
                    sound_enabled=settings['sound_enabled'],
                    show_grid=settings['show_grid']
                )
                
                # 运行游戏，游戏结束后会返回到这里
                game.run()
                
                print("\n游戏结束，返回设置界面...")
                
        except KeyboardInterrupt:
            print("\n游戏被用户中断")
        
        except Exception as e:
            print(f"\n游戏运行出错: {e}")
            print("请检查pygame是否正确安装")
        
        finally:
            pygame.quit()
            print("\n感谢游玩贪吃蛇游戏! 👋")


def main():
    """主函数"""
    app = GameApplication()
    app.run()


if __name__ == "__main__":
    main()