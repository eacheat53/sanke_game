"""
环境变量加载器
用于从.env文件加载环境变量
"""

import os
import re
from typing import Dict, Any, Optional


class EnvLoader:
    """环境变量加载器类"""
    
    def __init__(self, env_file: str = ".env"):
        """初始化环境变量加载器
        
        Args:
            env_file: .env文件路径
        """
        self.env_file = env_file
        self.env_vars = {}
        self.load_env()
    
    def load_env(self) -> Dict[str, str]:
        """加载.env文件中的环境变量
        
        Returns:
            包含环境变量的字典
        """
        if not os.path.exists(self.env_file):
            print(f"警告: 环境变量文件 {self.env_file} 不存在")
            return {}
        
        env_vars = {}
        
        try:
            with open(self.env_file, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    
                    # 跳过空行和注释
                    if not line or line.startswith('#'):
                        continue
                    
                    # 解析变量
                    if '=' in line:
                        key, value = line.split('=', 1)
                        key = key.strip()
                        value = value.strip()
                        
                        # 去除引号
                        if (value.startswith('"') and value.endswith('"')) or \
                           (value.startswith("'") and value.endswith("'")):
                            value = value[1:-1]
                        
                        env_vars[key] = value
                        
                        # 同时设置到系统环境变量
                        os.environ[key] = value
            
            self.env_vars = env_vars
            return env_vars
        
        except Exception as e:
            print(f"加载环境变量文件出错: {e}")
            return {}
    
    def get(self, key: str, default: Any = None) -> Any:
        """获取环境变量值
        
        Args:
            key: 环境变量名
            default: 默认值
            
        Returns:
            环境变量值或默认值
        """
        # 优先从系统环境变量获取
        value = os.environ.get(key)
        
        # 如果系统环境变量中没有，从加载的.env文件中获取
        if value is None:
            value = self.env_vars.get(key)
        
        # 如果都没有，返回默认值
        if value is None:
            return default
        
        return value
    
    def get_bool(self, key: str, default: bool = False) -> bool:
        """获取布尔类型环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            
        Returns:
            布尔值
        """
        value = self.get(key, default)
        
        if isinstance(value, bool):
            return value
        
        if isinstance(value, str):
            return value.lower() in ('true', 'yes', '1', 'y', 'on')
        
        return bool(value)
    
    def get_int(self, key: str, default: int = 0) -> int:
        """获取整数类型环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            
        Returns:
            整数值
        """
        value = self.get(key, default)
        
        if isinstance(value, int):
            return value
        
        try:
            return int(value)
        except (ValueError, TypeError):
            return default
    
    def get_float(self, key: str, default: float = 0.0) -> float:
        """获取浮点类型环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            
        Returns:
            浮点值
        """
        value = self.get(key, default)
        
        if isinstance(value, float):
            return value
        
        try:
            return float(value)
        except (ValueError, TypeError):
            return default
    
    def get_list(self, key: str, default: Optional[list] = None, 
                 separator: str = ',') -> list:
        """获取列表类型环境变量
        
        Args:
            key: 环境变量名
            default: 默认值
            separator: 分隔符
            
        Returns:
            列表值
        """
        if default is None:
            default = []
        
        value = self.get(key)
        
        if value is None:
            return default
        
        if isinstance(value, list):
            return value
        
        return [item.strip() for item in value.split(separator)]
    
    def get_rgb(self, key: str, default: tuple = (0, 0, 0)) -> tuple:
        """获取RGB颜色值
        
        Args:
            key: 环境变量名
            default: 默认RGB元组
            
        Returns:
            RGB颜色元组 (r, g, b)
        """
        value = self.get(key)
        
        if value is None:
            return default
        
        if isinstance(value, tuple) and len(value) == 3:
            return value
        
        try:
            # 尝试解析 "r,g,b" 格式
            rgb = [int(x.strip()) for x in value.split(',')]
            if len(rgb) == 3:
                return tuple(rgb)
        except:
            pass
        
        return default


# 创建默认环境变量加载器实例
env = EnvLoader()