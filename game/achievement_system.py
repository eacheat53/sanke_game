"""
成就系统
跟踪玩家的游戏成就和统计数据
"""

import json
import os
import time
from typing import Dict, List, Any, Callable
from datetime import datetime


class Achievement:
    """成就类"""
    
    def __init__(self, id: str, name: str, description: str, 
                 condition: Callable, reward_points: int = 10,
                 hidden: bool = False, category: str = "general"):
        """初始化成就
        
        Args:
            id: 成就ID
            name: 成就名称
            description: 成就描述
            condition: 达成条件函数
            reward_points: 奖励点数
            hidden: 是否为隐藏成就
            category: 成就分类
        """
        self.id = id
        self.name = name
        self.description = description
        self.condition = condition
        self.reward_points = reward_points
        self.hidden = hidden
        self.category = category
        self.unlocked = False
        self.unlock_time = None
        self.progress = 0.0  # 进度百分比 (0.0 - 1.0)
    
    def check_condition(self, stats: Dict[str, Any]) -> bool:
        """检查成就条件
        
        Args:
            stats: 游戏统计数据
            
        Returns:
            是否达成条件
        """
        try:
            result = self.condition(stats)
            if isinstance(result, tuple):
                # 返回 (是否达成, 进度)
                achieved, progress = result
                self.progress = max(0.0, min(1.0, progress))
                return achieved
            else:
                # 只返回是否达成
                if result:
                    self.progress = 1.0
                return result
        except Exception as e:
            print(f"检查成就条件失败 {self.id}: {e}")
            return False
    
    def unlock(self):
        """解锁成就"""
        if not self.unlocked:
            self.unlocked = True
            self.unlock_time = time.time()
            self.progress = 1.0
            print(f"🏆 成就解锁: {self.name}")
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            'id': self.id,
            'name': self.name,
            'description': self.description,
            'reward_points': self.reward_points,
            'hidden': self.hidden,
            'category': self.category,
            'unlocked': self.unlocked,
            'unlock_time': self.unlock_time,
            'progress': self.progress
        }


class AchievementSystem:
    """成就系统"""
    
    def __init__(self, save_file: str = "achievements.json"):
        """初始化成就系统
        
        Args:
            save_file: 成就保存文件
        """
        self.save_file = save_file
        self.achievements: Dict[str, Achievement] = {}
        self.game_stats = self._load_stats()
        
        # 初始化成就
        self._init_achievements()
        
        # 加载成就进度
        self._load_achievements()
    
    def _init_achievements(self):
        """初始化所有成就"""
        # 分数相关成就
        self._add_achievement("first_score", "初次得分", "获得第一分", 
                            lambda s: s.get('total_score', 0) > 0, 5)
        
        self._add_achievement("score_100", "百分达人", "单局得分达到100分", 
                            lambda s: s.get('highest_score', 0) >= 100, 10)
        
        self._add_achievement("score_500", "五百强者", "单局得分达到500分", 
                            lambda s: s.get('highest_score', 0) >= 500, 25)
        
        self._add_achievement("score_1000", "千分传说", "单局得分达到1000分", 
                            lambda s: s.get('highest_score', 0) >= 1000, 50)
        
        # 长度相关成就
        self._add_achievement("length_10", "小蛇成长", "蛇长度达到10节", 
                            lambda s: s.get('max_snake_length', 0) >= 10, 10)
        
        self._add_achievement("length_25", "中蛇进化", "蛇长度达到25节", 
                            lambda s: s.get('max_snake_length', 0) >= 25, 20)
        
        self._add_achievement("length_50", "大蛇传奇", "蛇长度达到50节", 
                            lambda s: s.get('max_snake_length', 0) >= 50, 40)
        
        # 时间相关成就
        self._add_achievement("time_60", "一分钟挑战", "单局游戏时间达到60秒", 
                            lambda s: s.get('max_game_time', 0) >= 60, 15)
        
        self._add_achievement("time_300", "五分钟马拉松", "单局游戏时间达到5分钟", 
                            lambda s: s.get('max_game_time', 0) >= 300, 30)
        
        # 游戏次数相关成就
        self._add_achievement("games_10", "新手玩家", "完成10局游戏", 
                            lambda s: s.get('total_games', 0) >= 10, 10)
        
        self._add_achievement("games_50", "经验玩家", "完成50局游戏", 
                            lambda s: s.get('total_games', 0) >= 50, 25)
        
        self._add_achievement("games_100", "资深玩家", "完成100局游戏", 
                            lambda s: s.get('total_games', 0) >= 100, 50)
        
        # 特殊成就
        self._add_achievement("special_food_10", "特殊美食家", "吃掉10个特殊食物", 
                            lambda s: s.get('special_food_eaten', 0) >= 10, 20)
        
        self._add_achievement("perfect_start", "完美开局", "游戏开始后30秒内不死亡", 
                            lambda s: s.get('perfect_starts', 0) >= 1, 15)
        
        self._add_achievement("speed_demon", "速度恶魔", "在最高速度下生存30秒", 
                            lambda s: s.get('high_speed_survival', 0) >= 30, 35)
        
        # 隐藏成就
        self._add_achievement("konami_code", "秘籍大师", "输入经典秘籍", 
                            lambda s: s.get('konami_used', False), 100, True)
        
        self._add_achievement("no_death_hour", "不死传说", "连续游戏1小时不死亡", 
                            lambda s: s.get('max_survival_time', 0) >= 3600, 200, True)
    
    def _add_achievement(self, id: str, name: str, description: str, 
                        condition: Callable, points: int = 10, 
                        hidden: bool = False, category: str = "general"):
        """添加成就"""
        achievement = Achievement(id, name, description, condition, points, hidden, category)
        self.achievements[id] = achievement
    
    def update_stats(self, **kwargs):
        """更新游戏统计数据"""
        for key, value in kwargs.items():
            if key in ['highest_score', 'max_snake_length', 'max_game_time', 'max_survival_time']:
                # 这些是最大值统计
                self.game_stats[key] = max(self.game_stats.get(key, 0), value)
            elif key in ['total_score', 'total_games', 'special_food_eaten', 'perfect_starts']:
                # 这些是累计统计
                self.game_stats[key] = self.game_stats.get(key, 0) + value
            else:
                # 其他直接设置
                self.game_stats[key] = value
        
        # 检查成就
        self._check_achievements()
    
    def _check_achievements(self):
        """检查所有成就"""
        newly_unlocked = []
        
        for achievement in self.achievements.values():
            if not achievement.unlocked:
                if achievement.check_condition(self.game_stats):
                    achievement.unlock()
                    newly_unlocked.append(achievement)
        
        return newly_unlocked
    
    def get_achievement_progress(self, achievement_id: str) -> float:
        """获取成就进度
        
        Args:
            achievement_id: 成就ID
            
        Returns:
            进度百分比 (0.0 - 1.0)
        """
        if achievement_id in self.achievements:
            return self.achievements[achievement_id].progress
        return 0.0
    
    def get_unlocked_achievements(self) -> List[Achievement]:
        """获取已解锁的成就"""
        return [a for a in self.achievements.values() if a.unlocked]
    
    def get_locked_achievements(self, include_hidden: bool = False) -> List[Achievement]:
        """获取未解锁的成就"""
        return [a for a in self.achievements.values() 
                if not a.unlocked and (include_hidden or not a.hidden)]
    
    def get_achievements_by_category(self, category: str) -> List[Achievement]:
        """按分类获取成就"""
        return [a for a in self.achievements.values() if a.category == category]
    
    def get_total_points(self) -> int:
        """获取总成就点数"""
        return sum(a.reward_points for a in self.achievements.values() if a.unlocked)
    
    def get_completion_percentage(self) -> float:
        """获取成就完成百分比"""
        total = len(self.achievements)
        unlocked = len(self.get_unlocked_achievements())
        return (unlocked / total * 100) if total > 0 else 0.0
    
    def _load_stats(self) -> Dict[str, Any]:
        """加载游戏统计数据"""
        stats_file = "game_stats.json"
        try:
            if os.path.exists(stats_file):
                with open(stats_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
        except Exception as e:
            print(f"加载统计数据失败: {e}")
        
        return {
            'total_games': 0,
            'total_score': 0,
            'highest_score': 0,
            'max_snake_length': 0,
            'max_game_time': 0,
            'special_food_eaten': 0,
            'perfect_starts': 0,
            'max_survival_time': 0
        }
    
    def _save_stats(self):
        """保存游戏统计数据"""
        stats_file = "game_stats.json"
        try:
            with open(stats_file, 'w', encoding='utf-8') as f:
                json.dump(self.game_stats, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"保存统计数据失败: {e}")
    
    def _load_achievements(self):
        """加载成就进度"""
        try:
            if os.path.exists(self.save_file):
                with open(self.save_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    for achievement_data in data.get('achievements', []):
                        achievement_id = achievement_data.get('id')
                        if achievement_id in self.achievements:
                            achievement = self.achievements[achievement_id]
                            achievement.unlocked = achievement_data.get('unlocked', False)
                            achievement.unlock_time = achievement_data.get('unlock_time')
                            achievement.progress = achievement_data.get('progress', 0.0)
        except Exception as e:
            print(f"加载成就数据失败: {e}")
    
    def save_achievements(self):
        """保存成就进度"""
        try:
            data = {
                'achievements': [a.to_dict() for a in self.achievements.values()],
                'save_time': time.time()
            }
            
            with open(self.save_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2, ensure_ascii=False)
            
            # 同时保存统计数据
            self._save_stats()
            
        except Exception as e:
            print(f"保存成就数据失败: {e}")
    
    def reset_achievements(self):
        """重置所有成就"""
        for achievement in self.achievements.values():
            achievement.unlocked = False
            achievement.unlock_time = None
            achievement.progress = 0.0
        
        self.game_stats = {
            'total_games': 0,
            'total_score': 0,
            'highest_score': 0,
            'max_snake_length': 0,
            'max_game_time': 0,
            'special_food_eaten': 0,
            'perfect_starts': 0,
            'max_survival_time': 0
        }
        
        self.save_achievements()
        print("所有成就已重置")


# 创建全局成就系统实例
achievement_system = AchievementSystem()