"""
CrawlerAgent配置使用示例

演示如何使用CrawlerConfig和ConfigManager来配置CrawlerAgent
"""

import asyncio
import sys
from pathlib import Path

from agents.crawler_agent import CrawlerAgent
from config.config import ConfigManager, CrawlerConfig

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


async def example_1_default_config():
    """示例1：使用默认配置"""
    print("=== 示例1：使用默认配置 ===")

    # 使用默认配置初始化CrawlerAgent
    agent = CrawlerAgent()

    print(f"最大文章数量: {agent.crawler_config.max_articles}")
    print(f"请求延迟: {agent.crawler_config.delay}秒")
    print(f"超时时间: {agent.crawler_config.timeout}秒")
    print(f"无头模式: {agent.crawler_config.headless}")
    print(f"浏览器类型: {agent.crawler_config.browser_type}")
    print(f"保存图片: {agent.crawler_config.save_images}")
    print(f"保存视频: {agent.crawler_config.save_videos}")
    print()


async def example_2_custom_config():
    """示例2：使用自定义配置"""
    print("=== 示例2：使用自定义配置 ===")

    # 创建自定义配置
    custom_config = CrawlerConfig(
        max_articles=5,
        delay=1.5,
        timeout=60,
        headless=False,  # 显示浏览器窗口
        browser_type="chromium",
        proxy="http://proxy:8080",  # 使用代理
        save_images=True,
        save_videos=False,
    )

    # 使用自定义配置初始化CrawlerAgent
    agent = CrawlerAgent(custom_config)

    print(f"最大文章数量: {agent.crawler_config.max_articles}")
    print(f"请求延迟: {agent.crawler_config.delay}秒")
    print(f"超时时间: {agent.crawler_config.timeout}秒")
    print(f"无头模式: {agent.crawler_config.headless}")
    print(f"浏览器类型: {agent.crawler_config.browser_type}")
    print(f"代理设置: {agent.crawler_config.proxy}")
    print(f"保存图片: {agent.crawler_config.save_images}")
    print(f"保存视频: {agent.crawler_config.save_videos}")
    print()


async def example_3_config_manager():
    """示例3：使用ConfigManager从配置文件加载"""
    print("=== 示例3：使用ConfigManager从配置文件加载 ===")

    # 创建ConfigManager实例
    manager = ConfigManager()

    # 检查配置文件是否存在
    if manager.config_exists():
        print(f"配置文件存在: {manager.get_config_path()}")

        # 从配置文件获取crawler配置
        config = manager.get_crawler_config()

        # 使用配置初始化CrawlerAgent
        agent = CrawlerAgent(config)

        print("从配置文件加载的配置:")
        print(f"  最大文章数量: {agent.crawler_config.max_articles}")
        print(f"  请求延迟: {agent.crawler_config.delay}秒")
        print(f"  超时时间: {agent.crawler_config.timeout}秒")
        print(f"  无头模式: {agent.crawler_config.headless}")
        print(f"  浏览器类型: {agent.crawler_config.browser_type}")
        print(f"  保存图片: {agent.crawler_config.save_images}")
        print(f"  保存视频: {agent.crawler_config.save_videos}")
    else:
        print(f"配置文件不存在: {manager.get_config_path()}")
        print("使用默认配置")

        # 使用默认配置
        config = manager.get_crawler_config()
        agent = CrawlerAgent(config)

        print("默认配置:")
        print(f"  最大文章数量: {agent.crawler_config.max_articles}")
        print(f"  请求延迟: {agent.crawler_config.delay}秒")

    print()


async def example_4_config_override():
    """示例4：配置覆盖"""
    print("=== 示例4：配置覆盖 ===")

    # 创建ConfigManager实例
    manager = ConfigManager()

    # 从配置文件获取配置，并覆盖某些参数
    config = manager.get_crawler_config(
        {
            "max_articles": 3,  # 覆盖最大文章数量
            "delay": 0.5,  # 覆盖延迟时间
            "headless": False,  # 覆盖无头模式
        }
    )

    # 使用覆盖后的配置初始化CrawlerAgent
    agent = CrawlerAgent(config)

    print("覆盖后的配置:")
    print(f"  最大文章数量: {agent.crawler_config.max_articles}")
    print(f"  请求延迟: {agent.crawler_config.delay}秒")
    print(f"  超时时间: {agent.crawler_config.timeout}秒")
    print(f"  无头模式: {agent.crawler_config.headless}")
    print(f"  浏览器类型: {agent.crawler_config.browser_type}")
    print()


async def example_5_different_browsers():
    """示例5：不同浏览器类型"""
    print("=== 示例5：不同浏览器类型 ===")

    browsers = ["chromium", "firefox", "webkit"]

    for browser_type in browsers:
        print(f"浏览器类型: {browser_type}")

        config = CrawlerConfig(
            browser_type=browser_type,
            headless=True,  # 无头模式避免打开多个窗口
            max_articles=1,
        )

        agent = CrawlerAgent(config)

        print(f"  配置的浏览器类型: {agent.crawler_config.browser_type}")
        print(f"  无头模式: {agent.crawler_config.headless}")
        print()


async def example_6_media_config():
    """示例6：媒体文件配置"""
    print("=== 示例6：媒体文件配置 ===")

    # 只保存图片，不保存视频
    config_images_only = CrawlerConfig(save_images=True, save_videos=False)

    agent_images = CrawlerAgent(config_images_only)
    print("只保存图片配置:")
    print(f"  保存图片: {agent_images.crawler_config.save_images}")
    print(f"  保存视频: {agent_images.crawler_config.save_videos}")

    # 只保存视频，不保存图片
    config_videos_only = CrawlerConfig(save_images=False, save_videos=True)

    agent_videos = CrawlerAgent(config_videos_only)
    print("只保存视频配置:")
    print(f"  保存图片: {agent_videos.crawler_config.save_images}")
    print(f"  保存视频: {agent_videos.crawler_config.save_videos}")

    # 都不保存
    config_no_media = CrawlerConfig(save_images=False, save_videos=False)

    agent_no_media = CrawlerAgent(config_no_media)
    print("不保存媒体文件配置:")
    print(f"  保存图片: {agent_no_media.crawler_config.save_images}")
    print(f"  保存视频: {agent_no_media.crawler_config.save_videos}")
    print()


async def main():
    """主函数"""
    print("CrawlerAgent配置使用示例")
    print("=" * 50)

    await example_1_default_config()
    await example_2_custom_config()
    await example_3_config_manager()
    await example_4_config_override()
    await example_5_different_browsers()
    await example_6_media_config()

    print("示例演示完成！")


if __name__ == "__main__":
    asyncio.run(main())
