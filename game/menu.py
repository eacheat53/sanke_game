"""
游戏菜单系统
"""

import pygame
import sys
from .constants import *


class Menu:
    """游戏菜单类"""
    
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.selected_option = 0
        self.menu_options = [
            "开始游戏",
            "设置",
            "查看最高分",
            "帮助",
            "退出游戏"
        ]
    
    def handle_events(self):
        """处理菜单事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.menu_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.menu_options)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    return self.get_selected_action()
                elif event.key == pygame.K_ESCAPE:
                    return "quit"
        
        return None
    
    def get_selected_action(self):
        """获取选中的动作"""
        actions = ["start_game", "settings", "high_score", "help", "quit"]
        return actions[self.selected_option]
    
    def draw(self):
        """绘制菜单"""
        self.screen.fill(BLACK)
        
        # 绘制标题
        title_text = self.font.render("🐍 贪吃蛇游戏 🐍", True, GREEN)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 150))
        self.screen.blit(title_text, title_rect)
        
        # 绘制菜单选项
        start_y = 250
        for i, option in enumerate(self.menu_options):
            color = WHITE if i == self.selected_option else GRAY
            if i == self.selected_option:
                # 高亮选中项
                option_text = f"► {option} ◄"
            else:
                option_text = f"  {option}  "
            
            text_surface = self.small_font.render(option_text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 40))
            self.screen.blit(text_surface, text_rect)
        
        # 绘制操作提示
        help_text = self.small_font.render("使用 ↑↓ 选择，回车确认，ESC退出", True, GRAY)
        help_rect = help_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(help_text, help_rect)
        
        pygame.display.flip()


class SettingsMenu:
    """设置菜单类"""
    
    def __init__(self, screen, font, small_font, config):
        self.screen = screen
        self.font = font
        self.small_font = small_font
        self.config = config
        self.selected_option = 0
        self.settings_options = [
            "难度设置",
            "音效开关",
            "音量调节",
            "显示网格",
            "返回主菜单"
        ]
    
    def handle_events(self):
        """处理设置菜单事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    self.selected_option = (self.selected_option - 1) % len(self.settings_options)
                elif event.key == pygame.K_DOWN:
                    self.selected_option = (self.selected_option + 1) % len(self.settings_options)
                elif event.key == pygame.K_LEFT or event.key == pygame.K_RIGHT:
                    self.adjust_setting(event.key == pygame.K_RIGHT)
                elif event.key == pygame.K_RETURN or event.key == pygame.K_SPACE:
                    if self.selected_option == len(self.settings_options) - 1:
                        return "back"
                    else:
                        self.adjust_setting(True)
                elif event.key == pygame.K_ESCAPE:
                    return "back"
        
        return None
    
    def adjust_setting(self, increase):
        """调整设置"""
        if self.selected_option == 0:  # 难度设置
            difficulties = ["easy", "normal", "hard"]
            current = self.config['game_settings']['difficulty']
            current_index = difficulties.index(current) if current in difficulties else 1
            if increase:
                new_index = (current_index + 1) % len(difficulties)
            else:
                new_index = (current_index - 1) % len(difficulties)
            self.config['game_settings']['difficulty'] = difficulties[new_index]
        
        elif self.selected_option == 1:  # 音效开关
            self.config['sound_settings']['enabled'] = not self.config['sound_settings']['enabled']
        
        elif self.selected_option == 2:  # 音量调节
            current_volume = self.config['sound_settings']['volume']
            if increase:
                new_volume = min(1.0, current_volume + 0.1)
            else:
                new_volume = max(0.0, current_volume - 0.1)
            self.config['sound_settings']['volume'] = round(new_volume, 1)
        
        elif self.selected_option == 3:  # 显示网格
            self.config['game_settings']['show_grid'] = not self.config['game_settings']['show_grid']
    
    def draw(self):
        """绘制设置菜单"""
        self.screen.fill(BLACK)
        
        # 绘制标题
        title_text = self.font.render("游戏设置", True, GREEN)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
        self.screen.blit(title_text, title_rect)
        
        # 绘制设置选项
        start_y = 200
        for i, option in enumerate(self.settings_options):
            color = WHITE if i == self.selected_option else GRAY
            
            # 获取当前设置值
            if i == 0:  # 难度
                value = self.config['game_settings']['difficulty']
                option_text = f"{option}: {value}"
            elif i == 1:  # 音效
                value = "开启" if self.config['sound_settings']['enabled'] else "关闭"
                option_text = f"{option}: {value}"
            elif i == 2:  # 音量
                value = int(self.config['sound_settings']['volume'] * 100)
                option_text = f"{option}: {value}%"
            elif i == 3:  # 网格
                value = "显示" if self.config['game_settings']['show_grid'] else "隐藏"
                option_text = f"{option}: {value}"
            else:
                option_text = option
            
            if i == self.selected_option and i < len(self.settings_options) - 1:
                option_text = f"► {option_text} ◄"
            elif i == self.selected_option:
                option_text = f"► {option_text} ◄"
            else:
                option_text = f"  {option_text}  "
            
            text_surface = self.small_font.render(option_text, True, color)
            text_rect = text_surface.get_rect(center=(WINDOW_WIDTH // 2, start_y + i * 40))
            self.screen.blit(text_surface, text_rect)
        
        # 绘制操作提示
        help_text = self.small_font.render("使用 ↑↓ 选择，←→ 调整，回车确认，ESC返回", True, GRAY)
        help_rect = help_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 50))
        self.screen.blit(help_text, help_rect)
        
        pygame.display.flip()


class HelpMenu:
    """帮助菜单类"""
    
    def __init__(self, screen, font, small_font):
        self.screen = screen
        self.font = font
        self.small_font = small_font
    
    def handle_events(self):
        """处理帮助菜单事件"""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return "quit"
            elif event.type == pygame.KEYDOWN:
                return "back"
        return None
    
    def draw(self):
        """绘制帮助菜单"""
        self.screen.fill(BLACK)
        
        # 绘制标题
        title_text = self.font.render("游戏帮助", True, GREEN)
        title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 80))
        self.screen.blit(title_text, title_rect)
        
        # 帮助内容
        help_content = [
            "游戏控制:",
            "  ↑ ↓ ← → : 控制蛇的移动方向",
            "  P : 暂停/继续游戏",
            "  ESC : 退出游戏",
            "  SPACE : 重新开始游戏（游戏结束时）",
            "",
            "游戏规则:",
            "  • 控制蛇吃红色食物",
            "  • 普通食物得10分，特殊食物得20分",
            "  • 每吃一个食物，蛇身变长",
            "  • 撞墙或撞到自己游戏结束",
            "  • 随着分数增加，游戏速度会提升",
            "",
            "特殊食物:",
            "  • 金色闪烁的食物价值更高",
            "  • 有时间限制，会自动消失",
            "",
            "按任意键返回主菜单"
        ]
        
        start_y = 140
        for i, line in enumerate(help_content):
            if line.startswith("游戏控制:") or line.startswith("游戏规则:") or line.startswith("特殊食物:"):
                color = GREEN
                font = self.small_font
            elif line.startswith("  "):
                color = WHITE
                font = self.small_font
            else:
                color = GRAY
                font = self.small_font
            
            text_surface = font.render(line, True, color)
            self.screen.blit(text_surface, (50, start_y + i * 25))
        
        pygame.display.flip()