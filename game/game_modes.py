"""
游戏模式管理器
支持多种游戏模式
"""

import random
import time
from typing import Dict, Any, Callable, Optional
from .constants import *


class GameMode:
    """游戏模式基类"""
    
    def __init__(self, name: str, description: str):
        """初始化游戏模式
        
        Args:
            name: 模式名称
            description: 模式描述
        """
        self.name = name
        self.description = description
        self.is_active = False
        self.start_time = 0
        self.mode_data = {}
    
    def start(self, game_engine) -> bool:
        """开始游戏模式
        
        Args:
            game_engine: 游戏引擎实例
            
        Returns:
            是否成功开始
        """
        self.is_active = True
        self.start_time = time.time()
        self.mode_data.clear()
        return True
    
    def update(self, game_engine) -> bool:
        """更新游戏模式
        
        Args:
            game_engine: 游戏引擎实例
            
        Returns:
            模式是否继续
        """
        return True
    
    def end(self, game_engine):
        """结束游戏模式
        
        Args:
            game_engine: 游戏引擎实例
        """
        self.is_active = False
    
    def get_status_text(self) -> str:
        """获取模式状态文本
        
        Returns:
            状态文本
        """
        return ""
    
    def get_score_multiplier(self) -> float:
        """获取分数倍数
        
        Returns:
            分数倍数
        """
        return 1.0


class ClassicMode(GameMode):
    """经典模式"""
    
    def __init__(self):
        super().__init__(
            "经典模式",
            "传统的贪吃蛇游戏，随着分数增加速度会提升"
        )


class TimeAttackMode(GameMode):
    """时间挑战模式 - 争分夺秒"""
    
    def __init__(self, time_limit: int = 120):
        super().__init__(
            "时间挑战",
            f"在{time_limit}秒内获得尽可能高的分数，时间紧迫时有特殊奖励"
        )
        self.time_limit = time_limit
    
    def start(self, game_engine) -> bool:
        super().start(game_engine)
        self.mode_data['remaining_time'] = self.time_limit
        self.mode_data['time_bonus_triggered'] = False
        self.mode_data['rush_mode'] = False
        self.mode_data['combo_count'] = 0
        self.mode_data['last_eat_time'] = time.time()
        return True
    
    def update(self, game_engine) -> bool:
        if not self.is_active:
            return False
        
        elapsed = time.time() - self.start_time
        remaining = max(0, self.time_limit - elapsed)
        self.mode_data['remaining_time'] = remaining
        
        # 时间紧迫时进入冲刺模式
        if remaining <= 30 and not self.mode_data['rush_mode']:
            self.mode_data['rush_mode'] = True
            game_engine.current_fps = min(25, game_engine.current_fps + 5)
            game_engine.show_message("冲刺模式! 速度提升!", GOLD)
        
        # 最后10秒的疯狂模式
        if remaining <= 10 and not self.mode_data['time_bonus_triggered']:
            self.mode_data['time_bonus_triggered'] = True
            game_engine.show_message("疯狂时刻! 双倍分数!", RED)
        
        # 检查连击
        current_time = time.time()
        if current_time - self.mode_data['last_eat_time'] > 3:  # 3秒内没吃到食物，连击重置
            self.mode_data['combo_count'] = 0
        
        # 检查是否吃到食物（通过分数变化判断）
        if hasattr(self, '_last_score') and game_engine.score > self._last_score:
            self.mode_data['combo_count'] += 1
            self.mode_data['last_eat_time'] = current_time
            
            # 连击奖励
            if self.mode_data['combo_count'] >= 5:
                game_engine.show_message(f"连击 x{self.mode_data['combo_count']}!", ORANGE)
        
        self._last_score = game_engine.score
        
        if remaining <= 0:
            game_engine.state = GAME_OVER
            final_score = game_engine.score
            combo_bonus = self.mode_data['combo_count'] * 10
            game_engine.score += combo_bonus
            game_engine.show_message(f"时间到! 连击奖励: +{combo_bonus}", RED)
            return False
        
        return True
    
    def get_status_text(self) -> str:
        remaining = self.mode_data.get('remaining_time', 0)
        combo = self.mode_data.get('combo_count', 0)
        status = f"剩余时间: {remaining:.1f}s"
        
        if combo > 0:
            status += f" | 连击: x{combo}"
        
        if self.mode_data.get('rush_mode', False):
            status += " | 冲刺模式"
        
        return status
    
    def get_score_multiplier(self) -> float:
        base_multiplier = 1.5
        
        # 冲刺模式额外加成
        if self.mode_data.get('rush_mode', False):
            base_multiplier += 0.5
        
        # 疯狂时刻双倍
        if self.mode_data.get('time_bonus_triggered', False):
            base_multiplier *= 2
        
        # 连击加成
        combo = self.mode_data.get('combo_count', 0)
        if combo >= 10:
            base_multiplier += 1.0
        elif combo >= 5:
            base_multiplier += 0.5
        elif combo >= 3:
            base_multiplier += 0.2
        
        return base_multiplier


class SurvivalMode(GameMode):
    """生存模式 - 极限生存挑战"""
    
    def __init__(self):
        super().__init__(
            "生存模式",
            "速度持续增加，环境逐渐恶化，测试你的生存极限"
        )
    
    def start(self, game_engine) -> bool:
        super().start(game_engine)
        self.mode_data['speed_increase_timer'] = 0
        self.mode_data['current_multiplier'] = 1.0
        self.mode_data['survival_level'] = 1
        self.mode_data['environmental_hazards'] = []
        self.mode_data['hazard_timer'] = 0
        self.mode_data['survival_time'] = 0
        return True
    
    def update(self, game_engine) -> bool:
        if not self.is_active:
            return False
        
        self.mode_data['survival_time'] += 1
        
        # 每20秒增加一次速度（比原来更频繁）
        self.mode_data['speed_increase_timer'] += 1
        if self.mode_data['speed_increase_timer'] >= 20 * game_engine.current_fps:
            game_engine.current_fps = min(60, game_engine.current_fps + 2)
            self.mode_data['speed_increase_timer'] = 0
            self.mode_data['current_multiplier'] += 0.15
            self.mode_data['survival_level'] += 1
            game_engine.show_message(f"生存等级提升! Lv.{self.mode_data['survival_level']}", ORANGE)
        
        # 随着生存等级提升，添加环境危险
        self.mode_data['hazard_timer'] += 1
        hazard_interval = max(300, 600 - self.mode_data['survival_level'] * 30)  # 危险出现频率增加
        
        if self.mode_data['hazard_timer'] >= hazard_interval:
            self._add_environmental_hazard(game_engine)
            self.mode_data['hazard_timer'] = 0
        
        # 更新环境危险
        self._update_hazards(game_engine)
        
        return True
    
    def _add_environmental_hazard(self, game_engine):
        """添加环境危险"""
        hazard_types = ['poison_zone', 'speed_trap', 'shrinking_boundary']
        
        if self.mode_data['survival_level'] >= 3:
            hazard_type = random.choice(hazard_types)
            
            if hazard_type == 'poison_zone':
                # 毒区：进入会持续减少蛇身
                x = random.randint(5, GRID_WIDTH - 6)
                y = random.randint(5, GRID_HEIGHT - 6)
                self.mode_data['environmental_hazards'].append({
                    'type': 'poison_zone',
                    'position': (x, y),
                    'radius': 3,
                    'duration': 15 * game_engine.current_fps
                })
                game_engine.show_message("毒区出现!", PURPLE)
            
            elif hazard_type == 'speed_trap':
                # 减速陷阱
                x = random.randint(3, GRID_WIDTH - 4)
                y = random.randint(3, GRID_HEIGHT - 4)
                self.mode_data['environmental_hazards'].append({
                    'type': 'speed_trap',
                    'position': (x, y),
                    'radius': 2,
                    'duration': 20 * game_engine.current_fps
                })
                game_engine.show_message("减速陷阱!", BLUE)
    
    def _update_hazards(self, game_engine):
        """更新环境危险"""
        active_hazards = []
        snake_head = game_engine.snake.get_head_position()
        
        for hazard in self.mode_data['environmental_hazards']:
            hazard['duration'] -= 1
            
            if hazard['duration'] > 0:
                # 检查蛇是否进入危险区域
                distance = abs(snake_head[0] - hazard['position'][0]) + abs(snake_head[1] - hazard['position'][1])
                
                if distance <= hazard['radius']:
                    if hazard['type'] == 'poison_zone':
                        # 毒区效果：缩短蛇身
                        if len(game_engine.snake.body) > 3 and random.random() < 0.1:
                            game_engine.snake.body.pop()
                            game_engine.show_message("中毒! 蛇身缩短", PURPLE)
                    
                    elif hazard['type'] == 'speed_trap':
                        # 减速陷阱效果
                        game_engine.current_fps = max(5, game_engine.current_fps - 1)
                        game_engine.show_message("陷入减速陷阱!", BLUE)
                
                active_hazards.append(hazard)
            else:
                game_engine.show_message(f"{hazard['type']} 消失", WHITE)
        
        self.mode_data['environmental_hazards'] = active_hazards
    
    def get_status_text(self) -> str:
        level = self.mode_data.get('survival_level', 1)
        hazards = len(self.mode_data.get('environmental_hazards', []))
        survival_time = self.mode_data.get('survival_time', 0) // 60  # 转换为秒
        return f"生存等级: Lv.{level} | 危险数: {hazards} | 生存时间: {survival_time}s"
    
    def get_score_multiplier(self) -> float:
        base_multiplier = self.mode_data.get('current_multiplier', 1.0)
        # 生存时间越长，额外奖励越高
        survival_bonus = min(2.0, self.mode_data.get('survival_time', 0) / (60 * 60))  # 每分钟增加奖励
        return base_multiplier + survival_bonus


class ZenMode(GameMode):
    """禅模式 - 轻松休闲模式"""
    
    def __init__(self):
        super().__init__(
            "禅模式",
            "慢节奏的休闲体验，无压力游戏，可穿墙"
        )
    
    def start(self, game_engine) -> bool:
        super().start(game_engine)
        self.mode_data['zen_level'] = 1
        self.mode_data['zen_points'] = 0
        self.mode_data['original_fps'] = 6  # 极慢的速度
        self.mode_data['quote_timer'] = 0
        game_engine.current_fps = self.mode_data['original_fps']
        return True
    
    def update(self, game_engine) -> bool:
        if not self.is_active:
            return False
        
        # 保持极慢的固定速度，营造轻松氛围
        game_engine.current_fps = self.mode_data['original_fps']
        
        # 累积休闲点数
        self.mode_data['zen_points'] += 0.1
        
        # 每100分提升等级
        if game_engine.score > 0 and game_engine.score % 100 == 0:
            if game_engine.score // 100 > self.mode_data['zen_level'] - 1:
                self.mode_data['zen_level'] += 1
                game_engine.show_message(f"休闲等级提升! Lv.{self.mode_data['zen_level']}", GOLD)
        
        # 禅模式的死亡处理（自身碰撞时重生）
        if game_engine.state == GAME_OVER:
            # 重置状态，实现"重生"
            game_engine.state = GAME_RUNNING
            game_engine.snake.reset()
            game_engine.show_message("重新开始...", PURPLE)
            self.mode_data['zen_points'] += 5  # 重生获得点数
        
        return True
    
    def get_status_text(self) -> str:
        level = self.mode_data.get('zen_level', 1)
        points = int(self.mode_data.get('zen_points', 0))
        return f"休闲等级: Lv.{level} | 休闲点数: {points}"
    
    def get_score_multiplier(self) -> float:
        # 等级越高，分数倍数越高
        level = self.mode_data.get('zen_level', 1)
        return 0.5 + (level * 0.1)  # 从0.6倍开始，每级增加0.1倍


class ChaosMode(GameMode):
    """混沌模式 - 极限挑战模式"""
    
    def __init__(self):
        super().__init__(
            "混沌模式",
            "极端随机事件，测试你的适应能力和反应速度"
        )
    
    def start(self, game_engine) -> bool:
        super().start(game_engine)
        self.mode_data['event_timer'] = 0
        self.mode_data['active_effects'] = []
        self.mode_data['chaos_level'] = 1
        self.mode_data['total_events'] = 0
        self.mode_data['event_history'] = []
        return True
    
    def update(self, game_engine) -> bool:
        if not self.is_active:
            return False
        
        # 混沌等级越高，事件触发越频繁
        base_interval = max(8, 25 - self.mode_data['chaos_level'] * 2)
        event_interval = random.randint(base_interval, base_interval + 10) * game_engine.current_fps
        
        self.mode_data['event_timer'] += 1
        if self.mode_data['event_timer'] >= event_interval:
            self._trigger_random_event(game_engine)
            self.mode_data['event_timer'] = 0
        
        # 每触发10个事件，混沌等级提升
        if self.mode_data['total_events'] > 0 and self.mode_data['total_events'] % 10 == 0:
            if self.mode_data['total_events'] // 10 > self.mode_data['chaos_level'] - 1:
                self.mode_data['chaos_level'] += 1
                game_engine.show_message(f"混沌等级提升! Lv.{self.mode_data['chaos_level']}", RED)
        
        # 更新活跃效果
        self._update_effects(game_engine)
        
        return True
    
    def _trigger_random_event(self, game_engine):
        """触发随机事件"""
        events = [
            self._speed_boost,
            self._speed_slow,
            self._double_food,
            self._invisible_walls,
            self._reverse_controls,
            self._shrink_snake,
            self._multiply_food,
            self._teleport_snake,
            self._gravity_shift,
            self._time_distortion
        ]
        
        # 高混沌等级时可能同时触发多个事件
        num_events = 1
        if self.mode_data['chaos_level'] >= 3 and random.random() < 0.3:
            num_events = 2
        elif self.mode_data['chaos_level'] >= 5 and random.random() < 0.2:
            num_events = 3
        
        selected_events = random.sample(events, min(num_events, len(events)))
        for event in selected_events:
            event(game_engine)
        
        self.mode_data['total_events'] += len(selected_events)
    
    def _speed_boost(self, game_engine):
        """速度提升事件"""
        game_engine.current_fps = min(40, game_engine.current_fps + 5)
        game_engine.show_message("速度提升!", ORANGE)
        self.mode_data['active_effects'].append({
            'type': 'speed_boost',
            'duration': 10 * game_engine.current_fps,
            'original_fps': game_engine.current_fps - 5
        })
    
    def _speed_slow(self, game_engine):
        """速度减慢事件"""
        game_engine.current_fps = max(5, game_engine.current_fps - 3)
        game_engine.show_message("速度减慢!", BLUE)
        self.mode_data['active_effects'].append({
            'type': 'speed_slow',
            'duration': 8 * game_engine.current_fps,
            'original_fps': game_engine.current_fps + 3
        })
    
    def _double_food(self, game_engine):
        """双倍食物事件"""
        game_engine.show_message("双倍分数!", GOLD)
        self.mode_data['active_effects'].append({
            'type': 'double_score',
            'duration': 15 * game_engine.current_fps
        })
    
    def _invisible_walls(self, game_engine):
        """隐形墙壁事件"""
        game_engine.show_message("穿墙模式!", PURPLE)
        self.mode_data['active_effects'].append({
            'type': 'no_walls',
            'duration': 20 * game_engine.current_fps
        })
    
    def _reverse_controls(self, game_engine):
        """反向控制事件"""
        game_engine.show_message("控制反转!", RED)
        self.mode_data['active_effects'].append({
            'type': 'reverse_controls',
            'duration': 12 * game_engine.current_fps
        })
    
    def _shrink_snake(self, game_engine):
        """缩短蛇身事件"""
        if len(game_engine.snake.body) > 3:
            # 移除蛇尾的一半长度
            remove_count = max(1, len(game_engine.snake.body) // 3)
            for _ in range(remove_count):
                if len(game_engine.snake.body) > 3:
                    game_engine.snake.body.pop()
            game_engine.show_message(f"蛇身缩短! -{remove_count}节", ORANGE)
    
    def _multiply_food(self, game_engine):
        """多重食物事件"""
        game_engine.show_message("食物增殖!", GREEN)
        self.mode_data['active_effects'].append({
            'type': 'multiply_food',
            'duration': 20 * game_engine.current_fps,
            'extra_foods': []
        })
        # 在随机位置生成3-5个额外食物
        for _ in range(random.randint(3, 5)):
            while True:
                x = random.randint(0, GRID_WIDTH - 1)
                y = random.randint(0, GRID_HEIGHT - 1)
                if (x, y) not in game_engine.snake.body:
                    self.mode_data['active_effects'][-1]['extra_foods'].append((x, y))
                    break
    
    def _teleport_snake(self, game_engine):
        """传送蛇头事件"""
        # 随机传送蛇头到新位置
        while True:
            new_x = random.randint(2, GRID_WIDTH - 3)
            new_y = random.randint(2, GRID_HEIGHT - 3)
            if (new_x, new_y) not in game_engine.snake.body[1:]:  # 不能传送到自己身体上
                game_engine.snake.body[0] = (new_x, new_y)
                game_engine.show_message("瞬间移动!", PURPLE)
                break
    
    def _gravity_shift(self, game_engine):
        """重力转换事件"""
        game_engine.show_message("重力异常!", BLUE)
        self.mode_data['active_effects'].append({
            'type': 'gravity_shift',
            'duration': 15 * game_engine.current_fps,
            'direction': random.choice([UP, DOWN, LEFT, RIGHT])
        })
    
    def _time_distortion(self, game_engine):
        """时间扭曲事件"""
        if random.random() < 0.5:
            # 时间加速
            game_engine.current_fps = min(30, game_engine.current_fps + 8)
            game_engine.show_message("时间加速!", GOLD)
            effect_type = 'time_fast'
        else:
            # 时间减慢
            game_engine.current_fps = max(3, game_engine.current_fps - 5)
            game_engine.show_message("时间减慢!", BLUE)
            effect_type = 'time_slow'
        
        self.mode_data['active_effects'].append({
            'type': effect_type,
            'duration': 10 * game_engine.current_fps,
            'original_fps': game_engine.current_fps - (8 if effect_type == 'time_fast' else -5)
        })
    
    def _update_effects(self, game_engine):
        """更新活跃效果"""
        active_effects = []
        
        for effect in self.mode_data['active_effects']:
            effect['duration'] -= 1
            
            if effect['duration'] > 0:
                active_effects.append(effect)
            else:
                # 效果结束，恢复原状
                if effect['type'] in ['speed_boost', 'speed_slow', 'time_fast', 'time_slow']:
                    game_engine.current_fps = effect['original_fps']
                    game_engine.show_message("速度恢复正常", WHITE)
                elif effect['type'] == 'multiply_food':
                    game_engine.show_message("额外食物消失", WHITE)
        
        self.mode_data['active_effects'] = active_effects
    
    def has_effect(self, effect_type: str) -> bool:
        """检查是否有特定效果"""
        return any(effect['type'] == effect_type for effect in self.mode_data.get('active_effects', []))
    
    def get_status_text(self) -> str:
        chaos_level = self.mode_data.get('chaos_level', 1)
        total_events = self.mode_data.get('total_events', 0)
        effects = self.mode_data.get('active_effects', [])
        
        status = f"混沌等级: Lv.{chaos_level} | 事件数: {total_events}"
        if effects:
            effect_count = len(effects)
            status += f" | 活跃效果: {effect_count}个"
        
        return status
    
    def get_score_multiplier(self) -> float:
        base_multiplier = 1.0 + (self.mode_data.get('chaos_level', 1) * 0.2)  # 每级增加0.2倍
        
        if self.has_effect('double_score'):
            base_multiplier *= 2.0
        
        # 活跃效果越多，分数倍数越高
        effect_count = len(self.mode_data.get('active_effects', []))
        if effect_count > 0:
            base_multiplier += effect_count * 0.1
        
        return base_multiplier


class SpeedRunMode(GameMode):
    """竞速模式 - 追求极限速度"""
    
    def __init__(self):
        super().__init__(
            "竞速模式",
            "追求极限速度，每吃一个食物速度都会提升"
        )
    
    def start(self, game_engine) -> bool:
        super().start(game_engine)
        self.mode_data['speed_level'] = 1
        self.mode_data['max_speed_reached'] = game_engine.current_fps
        self.mode_data['food_eaten'] = 0
        self.mode_data['speed_boost_timer'] = 0
        return True
    
    def update(self, game_engine) -> bool:
        if not self.is_active:
            return False
        
        # 检查是否吃到食物
        current_length = game_engine.snake.get_length()
        if current_length > self.mode_data['food_eaten'] + 3:  # 初始长度是3
            self.mode_data['food_eaten'] = current_length - 3
            
            # 每吃一个食物，速度提升
            game_engine.current_fps = min(50, game_engine.current_fps + 2)
            self.mode_data['speed_level'] += 1
            
            if game_engine.current_fps > self.mode_data['max_speed_reached']:
                self.mode_data['max_speed_reached'] = game_engine.current_fps
            
            game_engine.show_message(f"速度提升! Lv.{self.mode_data['speed_level']}", ORANGE)
            
            # 短暂的速度爆发效果
            self.mode_data['speed_boost_timer'] = 3 * game_engine.current_fps
        
        # 处理速度爆发效果
        if self.mode_data['speed_boost_timer'] > 0:
            self.mode_data['speed_boost_timer'] -= 1
            # 在爆发期间额外提升速度
            if self.mode_data['speed_boost_timer'] % 10 == 0:
                game_engine.current_fps = min(60, game_engine.current_fps + 1)
        
        return True
    
    def get_status_text(self) -> str:
        speed_level = self.mode_data.get('speed_level', 1)
        max_speed = self.mode_data.get('max_speed_reached', 10)
        return f"速度等级: Lv.{speed_level} | 最高速度: {max_speed} FPS"
    
    def get_score_multiplier(self) -> float:
        # 速度越高，分数倍数越高
        speed_level = self.mode_data.get('speed_level', 1)
        return 1.0 + (speed_level * 0.05)  # 每级增加0.05倍


class PerfectionMode(GameMode):
    """完美模式 - 追求零失误"""
    
    def __init__(self):
        super().__init__(
            "完美模式",
            "追求完美操作，任何碰撞都会重置分数"
        )
    
    def start(self, game_engine) -> bool:
        super().start(game_engine)
        self.mode_data['perfect_streak'] = 0
        self.mode_data['total_resets'] = 0
        self.mode_data['best_streak'] = 0
        self.mode_data['perfection_bonus'] = 1.0
        return True
    
    def update(self, game_engine) -> bool:
        if not self.is_active:
            return False
        
        # 检查是否吃到食物
        current_score = game_engine.score
        if current_score > self.mode_data.get('last_score', 0):
            self.mode_data['perfect_streak'] += 1
            self.mode_data['last_score'] = current_score
            
            if self.mode_data['perfect_streak'] > self.mode_data['best_streak']:
                self.mode_data['best_streak'] = self.mode_data['perfect_streak']
            
            # 连击奖励
            if self.mode_data['perfect_streak'] % 10 == 0:
                self.mode_data['perfection_bonus'] += 0.1
                game_engine.show_message(f"完美连击! x{self.mode_data['perfect_streak']}", GOLD)
        
        # 检查碰撞
        if game_engine.state == GAME_OVER:
            if self.mode_data['perfect_streak'] > 0:
                game_engine.show_message(f"完美连击中断! 连击数: {self.mode_data['perfect_streak']}", RED)
                self.mode_data['total_resets'] += 1
                self.mode_data['perfect_streak'] = 0
                self.mode_data['perfection_bonus'] = 1.0
                
                # 重置游戏但保持模式数据
                game_engine.restart_game()
                return True
        
        return True
    
    def get_status_text(self) -> str:
        streak = self.mode_data.get('perfect_streak', 0)
        best = self.mode_data.get('best_streak', 0)
        resets = self.mode_data.get('total_resets', 0)
        return f"完美连击: {streak} | 最佳: {best} | 重置次数: {resets}"
    
    def get_score_multiplier(self) -> float:
        base_multiplier = self.mode_data.get('perfection_bonus', 1.0)
        streak = self.mode_data.get('perfect_streak', 0)
        
        # 连击越高，分数倍数越高
        if streak >= 50:
            base_multiplier += 2.0
        elif streak >= 30:
            base_multiplier += 1.5
        elif streak >= 20:
            base_multiplier += 1.0
        elif streak >= 10:
            base_multiplier += 0.5
        
        return base_multiplier


class GameModeManager:
    """游戏模式管理器"""
    
    def __init__(self):
        """初始化游戏模式管理器"""
        self.modes = {
            'classic': ClassicMode(),
            'time_attack': TimeAttackMode(),
            'survival': SurvivalMode(),
            'zen': ZenMode(),
            'chaos': ChaosMode(),
            'speedrun': SpeedRunMode(),
            'perfection': PerfectionMode()
        }
        self.current_mode = self.modes['classic']
    
    def get_mode_list(self) -> Dict[str, GameMode]:
        """获取所有游戏模式
        
        Returns:
            模式字典
        """
        return self.modes
    
    def set_mode(self, mode_name: str) -> bool:
        """设置当前游戏模式
        
        Args:
            mode_name: 模式名称
            
        Returns:
            是否设置成功
        """
        if mode_name in self.modes:
            if self.current_mode.is_active:
                self.current_mode.end(None)
            self.current_mode = self.modes[mode_name]
            return True
        return False
    
    def get_current_mode(self) -> GameMode:
        """获取当前游戏模式
        
        Returns:
            当前模式
        """
        return self.current_mode
    
    def start_current_mode(self, game_engine) -> bool:
        """开始当前游戏模式
        
        Args:
            game_engine: 游戏引擎实例
            
        Returns:
            是否成功开始
        """
        result = self.current_mode.start(game_engine)
        return result
    
    def update_current_mode(self, game_engine) -> bool:
        """更新当前游戏模式
        
        Args:
            game_engine: 游戏引擎实例
            
        Returns:
            模式是否继续
        """
        return self.current_mode.update(game_engine)
    
    def end_current_mode(self, game_engine):
        """结束当前游戏模式
        
        Args:
            game_engine: 游戏引擎实例
        """
        self.current_mode.end(game_engine)


# 创建全局游戏模式管理器实例
game_mode_manager = GameModeManager()