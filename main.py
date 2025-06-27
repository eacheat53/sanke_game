#!/usr/bin/env python3
"""
贪吃蛇游戏启动页面
简洁的游戏参数设置界面
"""

import sys
import os

# 添加项目根目录到Python路径
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

# 检查pygame是否安装
from utils.helpers import check_pygame_installation
if not check_pygame_installation():
    sys.exit(1)

# 初始化pygame
import pygame
pygame.init()
pygame.font.init()

from game.constants import *
from game.game_engine import GameEngine


class GameStartScreen:
    """游戏开始页面类"""
    
    def __init__(self):
        """初始化游戏开始页面"""
        # pygame已在模块级别初始化
        
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
            'game_mode': 'classic',   # 游戏模式
            'difficulty': 'normal',   # easy, normal, hard
            'speed': 10,              # 游戏速度 (FPS)
            'snake_length': 3,        # 初始蛇长度
            'sound_enabled': True,    # 音效开关
            'show_grid': True,        # 显示网格
            'view_achievements': False # 是否查看成就
        }
        
        # 当前选中的设置项
        self.selected_setting = 0
        self.setting_names = [
            '游戏模式',
            '游戏难度',
            '游戏速度', 
            '初始蛇长',
            '音效开关',
            '显示网格',
            '查看成就',
            '开始游戏'
        ]
        
        # 设置选项
        self.difficulty_options = ['简单', '普通', '困难']
        self.difficulty_values = ['easy', 'normal', 'hard']
        
        # 游戏模式选项
        self.game_mode_options = ['经典模式', '时间挑战', '生存模式', '禅模式', '混沌模式', '竞速模式', '完美模式']
        self.game_mode_values = ['classic', 'time_attack', 'survival', 'zen', 'chaos', 'speedrun', 'perfection']
        
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
                    elif self.selected_setting == 6:  # 查看成就
                        self.show_achievements()
                    else:
                        self.adjust_setting(True)
        
        return True
    
    def adjust_setting(self, increase):
        """调整设置"""
        if self.selected_setting == 0:  # 游戏模式
            current_index = self.game_mode_values.index(self.settings['game_mode'])
            if increase:
                
                new_index = (current_index + 1) % len(self.game_mode_values)
            else:
                
                new_index = (current_index - 1) % len(self.game_mode_values)
            self.settings['game_mode'] = self.game_mode_values[new_index]
            
        elif self.selected_setting == 1:  # 游戏难度
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
        
        elif self.selected_setting == 2:  # 游戏速度
            if increase:
                self.settings['speed'] = min(30, self.settings['speed'] + 2)
            else:
                self.settings['speed'] = max(5, self.settings['speed'] - 2)
        
        elif self.selected_setting == 3:  # 初始蛇长
            if increase:
                self.settings['snake_length'] = min(10, self.settings['snake_length'] + 1)
            else:
                self.settings['snake_length'] = max(1, self.settings['snake_length'] - 1)
        
        elif self.selected_setting == 4:  # 音效开关
            self.settings['sound_enabled'] = not self.settings['sound_enabled']
        
        elif self.selected_setting == 5:  # 显示网格
            self.settings['show_grid'] = not self.settings['show_grid']
            
        elif self.selected_setting == 6:  # 查看成就
            self.settings['view_achievements'] = True
            self.show_achievements()
    
    def get_setting_value_text(self, setting_index):
        """获取设置值的显示文本"""
        if setting_index == 0:  # 游戏模式
            mode_index = self.game_mode_values.index(self.settings['game_mode'])
            return self.game_mode_options[mode_index]
        elif setting_index == 1:  # 游戏难度
            difficulty_index = self.difficulty_values.index(self.settings['difficulty'])
            return self.difficulty_options[difficulty_index]
        elif setting_index == 2:  # 游戏速度
            return f"{self.settings['speed']} FPS"
        elif setting_index == 3:  # 初始蛇长
            return f"{self.settings['snake_length']} 节"
        elif setting_index == 4:  # 音效开关
            return "开启" if self.settings['sound_enabled'] else "关闭"
        elif setting_index == 5:  # 显示网格
            return "显示" if self.settings['show_grid'] else "隐藏"
        elif setting_index == 6:  # 查看成就
            return "点击查看"
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
            y_pos = start_y + i * 60
            
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
            help_rect = help_text.get_rect(center=(WINDOW_WIDTH // 2, help_start_y + i * 25))
            self.screen.blit(help_text, help_rect)
        
        pygame.display.flip()
    
    def show_achievements(self):
        """显示成就界面"""
        # 导入成就系统
        from game.achievement_system import achievement_system
        
        viewing_achievements = True
        scroll_offset = 0
        max_scroll = 0
        
        # 获取成就列表
        unlocked_raw = achievement_system.get_unlocked_achievements()
        locked_raw = achievement_system.get_locked_achievements(include_hidden=False)
        
        # 确保unlocked和locked是列表，以防achievement_system返回非预期类型
        unlocked = unlocked_raw if isinstance(unlocked_raw, list) else []
        locked = locked_raw if isinstance(locked_raw, list) else []
        
        # 计算总成就数和完成百分比
        total_achievements = len(unlocked) + len(locked)
        completion_percentage = achievement_system.get_completion_percentage()
        total_points = achievement_system.get_total_points()
        
        achievements = unlocked + locked
        
        # 如果没有成就，显示提示
        if not achievements:
            # 导入Achievement类来创建占位符对象
            from game.achievement_system import Achievement
            achievements = [Achievement("no_achievements", "暂无成就", "继续游戏解锁更多成就", lambda s: False, hidden=False)]
        
        # 计算最大滚动范围
        
        max_scroll = max(0, len(achievements) * 60 - (WINDOW_HEIGHT - 250))
        
        while viewing_achievements:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    viewing_achievements = False
                    self.running = False
                    
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE or event.key == pygame.K_RETURN:
                        viewing_achievements = False
                    
                    elif event.key == pygame.K_UP:
                        scroll_offset = max(0, scroll_offset - 30)
                    
                    elif event.key == pygame.K_DOWN:
                        scroll_offset = min(max_scroll, scroll_offset + 30)
            
            # 绘制成就界面
            self.screen.fill(BLACK)
            
            # 绘制标题
            title_text = self.title_font.render("🏆 成就系统 🏆", True, GOLD)
            title_rect = title_text.get_rect(center=(WINDOW_WIDTH // 2, 50))
            self.screen.blit(title_text, title_rect)
            
            # 绘制统计信息
            
            stats_text = self.small_font.render(f"完成度: {completion_percentage:.1f}% | 总分: {total_points} | 已解锁: {len(unlocked)}/{total_achievements}", True, WHITE)
            stats_rect = stats_text.get_rect(center=(WINDOW_WIDTH // 2, 100))
            self.screen.blit(stats_text, stats_rect)
            
            # 绘制成就列表
            y_pos = 150 - scroll_offset
            for i, achievement in enumerate(achievements):
                if y_pos > -60 and y_pos < WINDOW_HEIGHT:
                    # 成就框
                    pygame.draw.rect(self.screen, GRAY, (50, y_pos, WINDOW_WIDTH - 100, 50), 1, 5)
                    
                    # 成就名称和描述
                    name = achievement.name
                    description = achievement.description
                    is_unlocked = achievement.unlocked
                    
                    # 根据解锁状态设置颜色
                    name_color = GREEN if is_unlocked else GRAY
                    desc_color = WHITE if is_unlocked else GRAY
                    
                    # 绘制成就名称
                    name_text = self.small_font.render(name, True, name_color)
                    self.screen.blit(name_text, (60, y_pos + 10))
                    
                    # 绘制成就描述
                    desc_text = self.small_font.render(description, True, desc_color)
                    self.screen.blit(desc_text, (60, y_pos + 30))
                    
                    # 绘制解锁状态
                    status_text = self.small_font.render("已解锁" if is_unlocked else "未解锁", True, GREEN if is_unlocked else RED)
                    status_rect = status_text.get_rect()
                    status_rect.right = WINDOW_WIDTH - 60
                    status_rect.centery = y_pos + 25
                    self.screen.blit(status_text, status_rect)
                
                y_pos += 60
            
            # 绘制返回提示
            back_text = self.small_font.render("按ESC或回车返回", True, ORANGE)
            back_rect = back_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 30))
            self.screen.blit(back_text, back_rect)
            
            # 绘制滚动提示
            if max_scroll > 0:
                scroll_text = self.small_font.render("使用↑↓键滚动", True, WHITE)
                scroll_rect = scroll_text.get_rect(center=(WINDOW_WIDTH // 2, WINDOW_HEIGHT - 60))
                self.screen.blit(scroll_text, scroll_rect)
            
            pygame.display.flip()
            self.clock.tick(30)
    
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
        # pygame已在模块级别初始化和检查
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
                
                # 设置游戏模式
                from game.game_modes import game_mode_manager
                game_mode_manager.set_mode(settings['game_mode'])
                
                # 创建并运行游戏
                game = GameEngine(
                    initial_fps=settings['speed'],
                    initial_snake_length=settings['snake_length'],
                    sound_enabled=settings['sound_enabled'],
                    show_grid=settings['show_grid']
                )
                
                # 运行游戏，游戏结束后会返回到这里
                return_to_settings = game.run()
                
                if not return_to_settings:
                    self.running = False # 游戏结束，退出应用
                
                print("\n游戏结束，返回设置界面...")
                
        finally:
            pygame.quit()
            print("\n感谢游玩贪吃蛇游戏! 👋")


def main():
    """主函数"""
    app = GameApplication()
    app.run()


if __name__ == "__main__":
    main()