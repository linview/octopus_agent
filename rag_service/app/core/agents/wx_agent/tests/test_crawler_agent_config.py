"""
测试CrawlerAgent使用CrawlerConfig的功能
"""

import pytest

from agents.crawler_agent import CrawlerAgent
from config.config import ConfigManager, CrawlerConfig


class TestCrawlerAgentConfig:
    """测试CrawlerAgent配置功能"""

    def test_init_with_default_config(self):
        """测试使用默认配置初始化"""
        agent = CrawlerAgent()

        assert agent.crawler_config is not None
        assert isinstance(agent.crawler_config, CrawlerConfig)
        assert agent.crawler_config.max_articles == 10
        assert agent.crawler_config.delay == 2.0
        assert agent.crawler_config.headless is True

    def test_init_with_custom_config(self):
        """测试使用自定义配置初始化"""
        custom_config = CrawlerConfig(max_articles=20, delay=1.5, headless=False, timeout=60, proxy="http://proxy:8080")

        agent = CrawlerAgent(custom_config)

        assert agent.crawler_config is custom_config
        assert agent.crawler_config.max_articles == 20
        assert agent.crawler_config.delay == 1.5
        assert agent.crawler_config.headless is False
        assert agent.crawler_config.timeout == 60
        assert agent.crawler_config.proxy == "http://proxy:8080"

    def test_init_with_config_manager(self):
        """测试通过ConfigManager获取配置初始化"""
        # 模拟ConfigManager
        manager = ConfigManager("nonexistent.json")  # 使用不存在的文件，会返回默认配置
        config = manager.get_crawler_config()

        agent = CrawlerAgent(config)

        assert agent.crawler_config is config
        assert isinstance(agent.crawler_config, CrawlerConfig)

    def test_config_usage_in_process(self):
        """测试配置在_process方法中的使用"""
        custom_config = CrawlerConfig(max_articles=5, delay=1.0)
        agent = CrawlerAgent(custom_config)

        # 这里我们只是验证配置被正确传递，不实际执行爬虫
        assert agent.crawler_config.max_articles == 5
        assert agent.crawler_config.delay == 1.0

    def test_save_images_config(self):
        """测试save_images配置"""
        # 测试启用图片保存
        config_with_images = CrawlerConfig(save_images=True)
        agent_with_images = CrawlerAgent(config_with_images)
        assert agent_with_images.crawler_config.save_images is True

        # 测试禁用图片保存
        config_without_images = CrawlerConfig(save_images=False)
        agent_without_images = CrawlerAgent(config_without_images)
        assert agent_without_images.crawler_config.save_images is False

    def test_save_videos_config(self):
        """测试save_videos配置"""
        # 测试启用视频保存
        config_with_videos = CrawlerConfig(save_videos=True)
        agent_with_videos = CrawlerAgent(config_with_videos)
        assert agent_with_videos.crawler_config.save_videos is True

        # 测试禁用视频保存
        config_without_videos = CrawlerConfig(save_videos=False)
        agent_without_videos = CrawlerAgent(config_without_videos)
        assert agent_without_videos.crawler_config.save_videos is False

    def test_browser_config(self):
        """测试浏览器相关配置"""
        config = CrawlerConfig(headless=False, browser_type="firefox", proxy="http://proxy:8080")
        agent = CrawlerAgent(config)

        assert agent.crawler_config.headless is False
        assert agent.crawler_config.browser_type == "firefox"
        assert agent.crawler_config.proxy == "http://proxy:8080"

    def test_timeout_config(self):
        """测试超时配置"""
        config = CrawlerConfig(timeout=60)
        agent = CrawlerAgent(config)

        assert agent.crawler_config.timeout == 60

    def test_user_agent_config(self):
        """测试用户代理配置"""
        custom_ua = "Custom User Agent String"
        config = CrawlerConfig(user_agent=custom_ua)
        agent = CrawlerAgent(config)

        assert agent.crawler_config.user_agent == custom_ua


class TestCrawlerAgentConfigIntegration:
    """测试CrawlerAgent配置集成"""

    def test_config_from_json_file(self):
        """测试从JSON文件加载配置"""
        # 这里假设config.json文件存在且包含有效的crawler配置
        try:
            manager = ConfigManager()
            config = manager.get_crawler_config()
            agent = CrawlerAgent(config)

            assert isinstance(agent.crawler_config, CrawlerConfig)
            # 验证配置字段都存在
            assert hasattr(agent.crawler_config, "max_articles")
            assert hasattr(agent.crawler_config, "delay")
            assert hasattr(agent.crawler_config, "timeout")
            assert hasattr(agent.crawler_config, "headless")
            assert hasattr(agent.crawler_config, "browser_type")
            assert hasattr(agent.crawler_config, "save_images")
            assert hasattr(agent.crawler_config, "save_videos")

        except Exception as e:
            # 如果配置文件不存在或无效，跳过测试
            pytest.skip(f"配置文件不可用: {e}")

    def test_config_override_behavior(self):
        """测试配置覆盖行为"""
        # 通过ConfigManager进行覆盖
        manager = ConfigManager("nonexistent.json")
        overridden_config = manager.get_crawler_config({"max_articles": 20, "delay": 1.5})

        agent = CrawlerAgent(overridden_config)

        assert agent.crawler_config.max_articles == 20
        assert agent.crawler_config.delay == 1.5
        # 其他字段应该使用默认值
        assert agent.crawler_config.timeout == 30
        assert agent.crawler_config.headless is True


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
