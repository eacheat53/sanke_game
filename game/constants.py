"""
游戏常量配置文件
"""

# 屏幕尺寸
WINDOW_WIDTH = 800
WINDOW_HEIGHT = 600
GRID_SIZE = 20

# 计算网格数量
GRID_WIDTH = WINDOW_WIDTH // GRID_SIZE
GRID_HEIGHT = WINDOW_HEIGHT // GRID_SIZE

# 颜色定义 (RGB)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
GREEN = (0, 255, 0)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
DARK_GREEN = (0, 200, 0)
GRAY = (128, 128, 128)
GOLD = (255, 215, 0)
ORANGE = (255, 165, 0)
PURPLE = (128, 0, 128)

# 方向常量
UP = (0, -1)
DOWN = (0, 1)
LEFT = (-1, 0)
RIGHT = (1, 0)

# 游戏状态
GAME_RUNNING = "running"
GAME_OVER = "game_over"
GAME_PAUSED = "paused"

# 字体设置
FONT_SIZE = 36
SMALL_FONT_SIZE = 24
