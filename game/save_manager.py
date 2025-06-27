"""
游戏存档管理器
支持游戏状态的保存和加载
"""

import json
import os
import time
from typing import Dict, List, Optional, Any
from datetime import datetime


class SaveManager:
    """游戏存档管理器"""
    
    def __init__(self, save_dir: str = "saves"):
        """初始化存档管理器
        
        Args:
            save_dir: 存档目录
        """
        self.save_dir = save_dir
        self.ensure_save_dir()
    
    def ensure_save_dir(self):
        """确保存档目录存在"""
        if not os.path.exists(self.save_dir):
            try:
                os.makedirs(self.save_dir)
            except Exception as e:
                print(f"创建存档目录失败: {e}")
    
    def save_game(self, game_state: Dict[str, Any], slot_name: str = None) -> bool:
        """保存游戏状态
        
        Args:
            game_state: 游戏状态字典
            slot_name: 存档槽名称，如果为None则使用时间戳
            
        Returns:
            是否保存成功
        """
        try:
            if slot_name is None:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                slot_name = f"save_{timestamp}"
            
            # 添加保存时间戳
            game_state['save_timestamp'] = time.time()
            game_state['save_date'] = datetime.now().isoformat()
            
            save_file = os.path.join(self.save_dir, f"{slot_name}.json")
            
            with open(save_file, 'w', encoding='utf-8') as f:
                json.dump(game_state, f, indent=2, ensure_ascii=False)
            
            print(f"游戏已保存到: {save_file}")
            return True
            
        except Exception as e:
            print(f"保存游戏失败: {e}")
            return False
    
    def load_game(self, slot_name: str) -> Optional[Dict[str, Any]]:
        """加载游戏状态
        
        Args:
            slot_name: 存档槽名称
            
        Returns:
            游戏状态字典，如果加载失败返回None
        """
        try:
            save_file = os.path.join(self.save_dir, f"{slot_name}.json")
            
            if not os.path.exists(save_file):
                print(f"存档文件不存在: {save_file}")
                return None
            
            with open(save_file, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            print(f"游戏已从 {save_file} 加载")
            return game_state
            
        except Exception as e:
            print(f"加载游戏失败: {e}")
            return None
    
    def get_save_list(self) -> List[Dict[str, Any]]:
        """获取存档列表
        
        Returns:
            存档信息列表
        """
        saves = []
        
        try:
            if not os.path.exists(self.save_dir):
                return saves
            
            for filename in os.listdir(self.save_dir):
                if filename.endswith('.json'):
                    slot_name = filename[:-5]  # 移除.json扩展名
                    save_file = os.path.join(self.save_dir, filename)
                    
                    try:
                        # 获取文件信息
                        stat = os.stat(save_file)
                        
                        # 尝试读取存档信息
                        with open(save_file, 'r', encoding='utf-8') as f:
                            game_state = json.load(f)
                        
                        save_info = {
                            'slot_name': slot_name,
                            'file_size': stat.st_size,
                            'modified_time': stat.st_mtime,
                            'score': game_state.get('score', 0),
                            'snake_length': game_state.get('snake_length', 0),
                            'game_time': game_state.get('game_time', 0),
                            'difficulty': game_state.get('difficulty', 'normal'),
                            'save_date': game_state.get('save_date', 'Unknown')
                        }
                        
                        saves.append(save_info)
                        
                    except Exception as e:
                        print(f"读取存档信息失败 {filename}: {e}")
            
            # 按修改时间排序（最新的在前）
            saves.sort(key=lambda x: x['modified_time'], reverse=True)
            
        except Exception as e:
            print(f"获取存档列表失败: {e}")
        
        return saves
    
    def delete_save(self, slot_name: str) -> bool:
        """删除存档
        
        Args:
            slot_name: 存档槽名称
            
        Returns:
            是否删除成功
        """
        try:
            save_file = os.path.join(self.save_dir, f"{slot_name}.json")
            
            if os.path.exists(save_file):
                os.remove(save_file)
                print(f"存档已删除: {save_file}")
                return True
            else:
                print(f"存档文件不存在: {save_file}")
                return False
                
        except Exception as e:
            print(f"删除存档失败: {e}")
            return False
    
    def export_save(self, slot_name: str, export_path: str) -> bool:
        """导出存档
        
        Args:
            slot_name: 存档槽名称
            export_path: 导出路径
            
        Returns:
            是否导出成功
        """
        try:
            save_file = os.path.join(self.save_dir, f"{slot_name}.json")
            
            if not os.path.exists(save_file):
                print(f"存档文件不存在: {save_file}")
                return False
            
            with open(save_file, 'r', encoding='utf-8') as src:
                with open(export_path, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            print(f"存档已导出到: {export_path}")
            return True
            
        except Exception as e:
            print(f"导出存档失败: {e}")
            return False
    
    def import_save(self, import_path: str, slot_name: str = None) -> bool:
        """导入存档
        
        Args:
            import_path: 导入路径
            slot_name: 存档槽名称，如果为None则使用文件名
            
        Returns:
            是否导入成功
        """
        try:
            if not os.path.exists(import_path):
                print(f"导入文件不存在: {import_path}")
                return False
            
            # 验证文件格式
            with open(import_path, 'r', encoding='utf-8') as f:
                game_state = json.load(f)
            
            if slot_name is None:
                slot_name = os.path.splitext(os.path.basename(import_path))[0]
            
            save_file = os.path.join(self.save_dir, f"{slot_name}.json")
            
            with open(import_path, 'r', encoding='utf-8') as src:
                with open(save_file, 'w', encoding='utf-8') as dst:
                    dst.write(src.read())
            
            print(f"存档已导入为: {save_file}")
            return True
            
        except Exception as e:
            print(f"导入存档失败: {e}")
            return False
    
    def get_save_statistics(self) -> Dict[str, Any]:
        """获取存档统计信息
        
        Returns:
            统计信息字典
        """
        saves = self.get_save_list()
        
        if not saves:
            return {
                'total_saves': 0,
                'total_size': 0,
                'highest_score': 0,
                'longest_snake': 0,
                'total_play_time': 0
            }
        
        total_size = sum(save['file_size'] for save in saves)
        highest_score = max(save['score'] for save in saves)
        longest_snake = max(save['snake_length'] for save in saves)
        total_play_time = sum(save['game_time'] for save in saves)
        
        return {
            'total_saves': len(saves),
            'total_size': total_size,
            'highest_score': highest_score,
            'longest_snake': longest_snake,
            'total_play_time': total_play_time
        }


# 创建全局存档管理器实例
save_manager = SaveManager()