"""
配置模块测试

验证配置类的字段定义和配置管理器的功能
"""

import json
from pathlib import Path
from tempfile import NamedTemporaryFile

import pytest

from config.config import ConfigManager, CrawlerConfig


class TestCrawlerConfig:
    """测试CrawlerConfig类"""

    def test_default_values(self):
        """测试默认值"""
        config = CrawlerConfig()

        assert config.max_articles == 10
        assert config.delay == 2.0
        assert config.timeout == 30
        assert config.retry_times == 3
        assert config.headless is True
        assert config.browser_type == "chromium"
        assert config.proxy is None
        assert config.save_images is True
        assert config.save_videos is True
        assert "Mozilla/5.0" in config.user_agent

    def test_custom_values(self):
        """测试自定义值"""
        config = CrawlerConfig(max_articles=20, delay=1.5, timeout=60, headless=False, proxy="http://proxy:8080")

        assert config.max_articles == 20
        assert config.delay == 1.5
        assert config.timeout == 60
        assert config.headless is False
        assert config.proxy == "http://proxy:8080"

    def test_field_validation(self):
        """测试字段验证"""
        # 测试无效的max_articles（应该是int）
        with pytest.raises(ValueError):
            CrawlerConfig(max_articles="invalid")

        # 测试无效的delay（应该是float）
        with pytest.raises(ValueError):
            CrawlerConfig(delay="invalid")

        # 测试无效的timeout（应该是int）
        with pytest.raises(ValueError):
            CrawlerConfig(timeout="invalid")

        # 测试无效的headless（应该是bool）
        with pytest.raises(ValueError):
            CrawlerConfig(headless="invalid")

    def test_model_dump(self):
        """测试模型序列化"""
        config = CrawlerConfig(max_articles=15, delay=3.0)
        config_dict = config.model_dump()

        assert config_dict["max_articles"] == 15
        assert config_dict["delay"] == 3.0
        assert "user_agent" in config_dict
        assert "timeout" in config_dict
        assert "retry_times" in config_dict
        assert "headless" in config_dict
        assert "browser_type" in config_dict
        assert "proxy" in config_dict
        assert "save_images" in config_dict
        assert "save_videos" in config_dict


class TestConfigManager:
    """测试ConfigManager类"""

    def test_init_with_nonexistent_file(self):
        """测试初始化时文件不存在"""
        with NamedTemporaryFile(suffix=".json", delete=True) as tmp_file:
            config_path = tmp_file.name

        # 删除临时文件
        Path(config_path).unlink(missing_ok=True)

        manager = ConfigManager(config_path)
        assert manager.config == {}
        assert not manager.config_exists()

    def test_load_valid_config(self):
        """测试加载有效配置"""
        test_config = {"crawler": {"max_articles": 25, "delay": 1.5, "timeout": 45, "headless": False}}

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(test_config, tmp_file)
            config_path = tmp_file.name

        try:
            manager = ConfigManager(config_path)
            assert manager.config == test_config
            assert manager.config_exists()
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_load_invalid_json(self):
        """测试加载无效JSON"""
        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            tmp_file.write("invalid json content")
            config_path = tmp_file.name

        try:
            manager = ConfigManager(config_path)
            assert manager.config == {}
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_get_crawler_config_default(self):
        """测试获取爬虫配置（使用默认值）"""
        manager = ConfigManager("nonexistent.json")
        config = manager.get_crawler_config()

        assert isinstance(config, CrawlerConfig)
        assert config.max_articles == 10  # 默认值
        assert config.delay == 2.0  # 默认值

    def test_get_crawler_config_from_file(self):
        """测试从文件获取爬虫配置"""
        test_config = {"crawler": {"max_articles": 30, "delay": 2.5, "timeout": 60}}

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(test_config, tmp_file)
            config_path = tmp_file.name

        try:
            manager = ConfigManager(config_path)
            config = manager.get_crawler_config()

            assert config.max_articles == 30
            assert config.delay == 2.5
            assert config.timeout == 60
            assert config.headless is True  # 使用默认值
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_get_crawler_config_with_overrides(self):
        """测试获取爬虫配置（带覆盖）"""
        test_config = {"crawler": {"max_articles": 20, "delay": 2.0}}

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(test_config, tmp_file)
            config_path = tmp_file.name

        try:
            manager = ConfigManager(config_path)
            config = manager.get_crawler_config({"max_articles": 50, "timeout": 90})

            assert config.max_articles == 50  # 被覆盖
            assert config.delay == 2.0  # 来自文件
            assert config.timeout == 90  # 被覆盖
            assert config.headless is True  # 默认值
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_get_crawler_config_invalid_config(self):
        """测试获取爬虫配置（无效配置）"""
        test_config = {
            "crawler": {
                "max_articles": "invalid",  # 应该是int
                "delay": 2.0,
            }
        }

        with NamedTemporaryFile(mode="w", suffix=".json", delete=False) as tmp_file:
            json.dump(test_config, tmp_file)
            config_path = tmp_file.name

        try:
            manager = ConfigManager(config_path)
            with pytest.raises(ValueError, match="无效的crawler配置"):
                manager.get_crawler_config()
        finally:
            Path(config_path).unlink(missing_ok=True)

    def test_config_path_methods(self):
        """测试配置文件路径相关方法"""
        config_path = "test_config.json"
        manager = ConfigManager(config_path)

        assert str(manager.get_config_path()) == config_path
        assert isinstance(manager.get_config_path(), Path)


class TestConfigIntegration:
    """测试配置集成"""

    def test_config_json_structure_validation(self):
        """测试config.json文件结构与CrawlerConfig字段的一致性"""
        # 这个测试确保config.json中的字段与CrawlerConfig类定义一致
        config_path = Path("config/config.json")

        if config_path.exists():
            with open(config_path, encoding="utf-8") as f:
                config_data = json.load(f)

            if "crawler" in config_data:
                crawler_data = config_data["crawler"]

                # 验证所有字段都能被CrawlerConfig接受
                try:
                    config = CrawlerConfig(**crawler_data)
                    # 如果成功创建，说明字段结构正确
                    assert isinstance(config, CrawlerConfig)
                except Exception as e:
                    pytest.fail(f"config.json中的crawler配置与CrawlerConfig类不匹配: {e}")
        else:
            # 如果配置文件不存在，跳过测试
            pytest.skip("config.json文件不存在")

    def test_all_crawler_config_fields_covered(self):
        """测试CrawlerConfig的所有字段都有对应的测试"""
        # 获取CrawlerConfig的所有字段
        config = CrawlerConfig()
        config_dict = config.model_dump()

        # 验证关键字段存在
        required_fields = [
            "max_articles",
            "delay",
            "user_agent",
            "timeout",
            "retry_times",
            "headless",
            "browser_type",
            "proxy",
            "save_images",
            "save_videos",
        ]

        for field in required_fields:
            assert field in config_dict, f"缺少字段: {field}"
            assert field in CrawlerConfig.model_fields, f"字段未在模型中定义: {field}"

    def test_config_manager_readonly_behavior(self):
        """测试ConfigManager的只读行为"""
        # 验证ConfigManager没有写入方法
        manager = ConfigManager()

        # 检查没有save_config方法
        assert not hasattr(manager, "save_config")

        # 检查没有create_default_config方法
        assert not hasattr(manager, "create_default_config")

        # 验证只读方法存在
        assert hasattr(manager, "get_global_config")
        assert hasattr(manager, "get_crawler_config")
        assert hasattr(manager, "config_exists")
        assert hasattr(manager, "get_config_path")


if __name__ == "__main__":
    # 运行测试
    pytest.main([__file__, "-v"])
