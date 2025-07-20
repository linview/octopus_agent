"""
配置管理模块

提供Agent配置类和配置管理器
"""

import json
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field, ValidationError


class CrawlerConfig(BaseModel):
    """爬虫Agent配置"""

    max_articles: int = Field(default=10, description="最大爬取文章数量")
    delay: float = Field(default=2.0, description="请求间隔时间（秒）")
    user_agent: str = Field(
        default="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", description="User-Agent"
    )
    timeout: int = Field(default=30, description="请求超时时间（秒）")
    retry_times: int = Field(default=3, description="重试次数")
    headless: bool = Field(default=True, description="是否无头模式")
    browser_type: str = Field(default="chromium", description="浏览器类型")
    proxy: str | None = Field(default=None, description="代理设置")
    save_images: bool = Field(default=True, description="是否保存图片")
    save_videos: bool = Field(default=True, description="是否保存视频")


class ConfigManager:
    """只读配置管理器

    从config.json文件加载配置，不提供修改和创建配置文件的功能
    """

    def __init__(self, config_path: str = "config/config.json"):
        self.config_path = Path(config_path)
        self.config = self._load_config()

    def _load_config(self) -> dict[str, Any]:
        """从JSON文件加载配置"""
        if not self.config_path.exists():
            print(f"警告: 配置文件不存在 {self.config_path}")
            return {}

        try:
            with open(self.config_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"加载配置文件失败: {e}")
            return {}

    def get_global_config(self) -> dict[str, Any]:
        """获取全局配置"""
        return self.config

    def get_crawler_config(self, overrides: dict = None) -> CrawlerConfig:
        """获取爬虫配置

        Args:
            overrides: 可选的配置覆盖参数

        Returns:
            CrawlerConfig: 爬虫配置对象

        Raises:
            ValueError: 当配置文件中的crawler配置无效时
        """
        crawler_config = self.config.get("crawler", {})
        if overrides:
            crawler_config.update(overrides)

        try:
            return CrawlerConfig(**crawler_config)
        except ValidationError as e:
            # 专门处理Pydantic验证错误
            raise ValueError(f"配置验证失败: {e}") from e
        except Exception as e:
            # 处理其他可能的异常
            raise ValueError(f"无效的crawler配置: {e}") from e

    def config_exists(self) -> bool:
        """检查配置文件是否存在"""
        return self.config_path.exists()

    def get_config_path(self) -> Path:
        """获取配置文件路径"""
        return self.config_path
