"""
配置工具模块

提供配置加载、验证和管理功能
"""

import os
import json
from pathlib import Path
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from models.agent_config import AgentConfig


class ConfigManager:
    """配置管理器"""
    
    def __init__(self, config_path: Optional[str] = None):
        """
        初始化配置管理器
        
        Args:
            config_path: 配置文件路径
        """
        self.config_path = config_path or "config/config.json"
        self.config: Optional[AgentConfig] = None
        self.env_vars: Dict[str, str] = {}
        
    def load_env_file(self, env_path: str = ".env") -> None:
        """
        加载环境变量文件
        
        Args:
            env_path: 环境变量文件路径
        """
        if os.path.exists(env_path):
            load_dotenv(env_path)
            print(f"已加载环境变量文件: {env_path}")
        else:
            print(f"环境变量文件不存在: {env_path}")
    
    def load_config(self) -> AgentConfig:
        """
        加载配置文件
        
        Returns:
            AgentConfig: 配置对象
        """
        # 首先加载环境变量
        self.load_env_file()
        
        # 尝试从文件加载配置
        if os.path.exists(self.config_path):
            try:
                self.config = AgentConfig.from_file(self.config_path)
                print(f"已从文件加载配置: {self.config_path}")
            except Exception as e:
                print(f"从文件加载配置失败: {e}")
                self.config = self._create_default_config()
        else:
            print("配置文件不存在，使用默认配置")
            self.config = self._create_default_config()
        
        # 从环境变量更新配置
        self._update_from_env()
        
        # 验证配置
        errors = self.config.validate_config()
        if errors:
            print(f"配置验证发现问题: {errors}")
        
        return self.config
    
    def _create_default_config(self) -> AgentConfig:
        """创建默认配置"""
        return AgentConfig()
    
    def _update_from_env(self) -> None:
        """从环境变量更新配置"""
        if not self.config:
            return
        
        # 爬虫配置
        if os.getenv("CRAWLER_MAX_ARTICLES"):
            self.config.crawler.max_articles = int(os.getenv("CRAWLER_MAX_ARTICLES"))
        if os.getenv("CRAWLER_DELAY"):
            self.config.crawler.delay = float(os.getenv("CRAWLER_DELAY"))
        if os.getenv("CRAWLER_USER_AGENT"):
            self.config.crawler.user_agent = os.getenv("CRAWLER_USER_AGENT")
        
        # 存储配置
        if os.getenv("STORER_TYPE"):
            self.config.storer.storage_type = os.getenv("STORER_TYPE")
        if os.getenv("STORER_DATA_PATH"):
            self.config.storer.data_path = os.getenv("STORER_DATA_PATH")
        if os.getenv("STORER_MONGODB_URI"):
            self.config.storer.mongodb_uri = os.getenv("STORER_MONGODB_URI")
        
        # 分析配置
        if os.getenv("ANALYZER_MODEL_NAME"):
            self.config.analyzer.model_name = os.getenv("ANALYZER_MODEL_NAME")
        if os.getenv("ANALYZER_FEATURES"):
            features = os.getenv("ANALYZER_FEATURES").split(",")
            self.config.analyzer.features = [f.strip() for f in features]
        
        # 生成配置
        if os.getenv("GENERATOR_LLM_MODEL"):
            self.config.generator.llm_model = os.getenv("GENERATOR_LLM_MODEL")
        if os.getenv("GENERATOR_MAX_LENGTH"):
            self.config.generator.max_length = int(os.getenv("GENERATOR_MAX_LENGTH"))
        if os.getenv("GENERATOR_TEMPERATURE"):
            self.config.generator.temperature = float(os.getenv("GENERATOR_TEMPERATURE"))
        
        # Dify配置
        if os.getenv("DIFY_ENABLED"):
            self.config.dify.enabled = os.getenv("DIFY_ENABLED").lower() == "true"
        if os.getenv("DIFY_API_URL"):
            self.config.dify.api_url = os.getenv("DIFY_API_URL")
        if os.getenv("DIFY_API_KEY"):
            self.config.dify.api_key = os.getenv("DIFY_API_KEY")
        
        # 日志配置
        if os.getenv("LOG_LEVEL"):
            self.config.logging.level = os.getenv("LOG_LEVEL")
        if os.getenv("LOG_FILE"):
            self.config.logging.file_path = os.getenv("LOG_FILE")
        
        # 开发环境配置
        if os.getenv("DEBUG"):
            self.config.debug = os.getenv("DEBUG").lower() == "true"
        if os.getenv("TEST_MODE"):
            self.config.test_mode = os.getenv("TEST_MODE").lower() == "true"
    
    def save_config(self, config: AgentConfig, path: Optional[str] = None) -> None:
        """
        保存配置到文件
        
        Args:
            config: 配置对象
            path: 保存路径
        """
        save_path = path or self.config_path
        
        # 确保目录存在
        os.makedirs(os.path.dirname(save_path), exist_ok=True)
        
        try:
            config.save_to_file(save_path)
            print(f"配置已保存到: {save_path}")
        except Exception as e:
            print(f"保存配置失败: {e}")
            raise
    
    def get_config(self) -> AgentConfig:
        """
        获取配置对象
        
        Returns:
            AgentConfig: 配置对象
        """
        if self.config is None:
            self.config = self.load_config()
        return self.config
    
    def update_config(self, updates: Dict[str, Any]) -> None:
        """
        更新配置
        
        Args:
            updates: 更新内容
        """
        if self.config is None:
            self.config = self.load_config()
        
        self.config.update_config(updates)
        print(f"配置已更新: {list(updates.keys())}")
    
    def reload_config(self) -> AgentConfig:
        """
        重新加载配置
        
        Returns:
            AgentConfig: 新的配置对象
        """
        self.config = None
        return self.load_config()
    
    def create_config_template(self, output_path: str = "config/config.template.json") -> None:
        """
        创建配置模板文件
        
        Args:
            output_path: 输出路径
        """
        template_config = self._create_default_config()
        
        # 确保目录存在
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        
        try:
            template_config.save_to_file(output_path)
            print(f"配置模板已创建: {output_path}")
        except Exception as e:
            print(f"创建配置模板失败: {e}")
            raise
    
    def validate_config_file(self, config_path: str) -> list:
        """
        验证配置文件
        
        Args:
            config_path: 配置文件路径
            
        Returns:
            list: 错误列表
        """
        try:
            config = AgentConfig.from_file(config_path)
            return config.validate_config()
        except Exception as e:
            return [f"配置文件格式错误: {e}"]


def load_config(config_path: Optional[str] = None) -> AgentConfig:
    """
    快速加载配置的便捷函数
    
    Args:
        config_path: 配置文件路径
        
    Returns:
        AgentConfig: 配置对象
    """
    manager = ConfigManager(config_path)
    return manager.load_config()


def save_config(config: AgentConfig, path: Optional[str] = None) -> None:
    """
    快速保存配置的便捷函数
    
    Args:
        config: 配置对象
        path: 保存路径
    """
    manager = ConfigManager()
    manager.save_config(config, path)


def create_default_config_file(output_path: str = "config/config.json") -> None:
    """
    创建默认配置文件
    
    Args:
        output_path: 输出路径
    """
    manager = ConfigManager()
    manager.create_config_template(output_path)


# 全局配置实例
_global_config: Optional[AgentConfig] = None


def get_global_config() -> AgentConfig:
    """
    获取全局配置实例
    
    Returns:
        AgentConfig: 全局配置对象
    """
    global _global_config
    if _global_config is None:
        _global_config = load_config()
    return _global_config


def set_global_config(config: AgentConfig) -> None:
    """
    设置全局配置实例
    
    Args:
        config: 配置对象
    """
    global _global_config
    _global_config = config


def reload_global_config() -> AgentConfig:
    """
    重新加载全局配置
    
    Returns:
        AgentConfig: 新的全局配置对象
    """
    global _global_config
    _global_config = None
    return get_global_config() 