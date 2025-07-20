"""
图片锚点功能测试脚本

验证新的图片锚点功能是否正常工作
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

import pytest

from agents.crawler_agent import CrawlerAgent
from config.config import CrawlerConfig


@pytest.mark.asyncio
async def test_image_anchors():
    """测试图片锚点功能"""
    print("=" * 60)
    print("图片锚点功能测试")
    print("=" * 60)

    # 配置 - 使用CrawlerConfig
    config = CrawlerConfig(
        headless=False,
        max_articles=1,
        delay=2.0,
        timeout=60,
        save_images=True,  # 确保启用图片保存
    )

    # 测试文章URL
    test_urls = [
        "https://mp.weixin.qq.com/s/8xJcEI1Mx1lYeCvQsK7t9Q",
    ]

    # 创建CrawlerAgent
    crawler = CrawlerAgent(config)

    try:
        # 执行爬取任务
        input_data = {"article_urls": test_urls, "max_count": 1}

        print("🚀 开始执行爬取任务...")

        # 执行爬取
        articles = await crawler.execute(input_data)

        if not articles:
            print("❌ 没有爬取到文章")
            return

        article = articles[0]

        print("\n✅ 爬取完成！")
        print(f"📄 标题: {article.title}")
        print(f"👤 作者: {article.account_name}")
        print(f"📅 发布时间: {article.publish_time}")
        print(f"🖼️ 图片数量: {article.get_image_count()}")
        print(f"📝 内容长度: {len(article.content)} 字符")

        # 分析图片锚点
        analyze_image_anchors(article)

        # 保存结果
        save_article_with_anchors(article)

        # 断言验证
        assert article.title is not None
        assert len(article.content) > 0
        assert len(article.images) > 0

    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        raise
    finally:
        await crawler._cleanup()


def analyze_image_anchors(article):
    """分析图片锚点"""
    print("\n" + "=" * 40)
    print("图片锚点分析")
    print("=" * 40)

    # 1. 检查图片数据
    print(f"📊 图片映射数量: {len(article.images)}")
    print(f"📊 图片URL列表: {list(article.images.values())}")

    # 2. 检查内容中的锚点
    content = article.content
    anchors = article.get_image_anchors()

    print(f"📊 内容中的锚点数量: {len(anchors)}")
    print(f"📊 锚点列表: {anchors}")

    # 3. 显示内容预览
    print("\n📝 内容预览（包含锚点）:")
    lines = content.split("\n")
    for i, line in enumerate(lines[:20], 1):  # 显示前20行
        if any(anchor in line for anchor in anchors):
            print(f"  {i:2d}. [图片锚点] {line}")
        else:
            print(f"  {i:2d}. {line}")

    if len(lines) > 20:
        print(f"  ... (还有 {len(lines) - 20} 行)")

    # 4. 验证锚点与图片的对应关系
    print("\n🔗 锚点与图片对应关系:")
    for img_id, url in article.images.items():
        anchor = f"$img_{img_id.replace('img_', '')}$"
        if anchor in content:
            print(f"  ✅ {anchor} -> {url[:50]}...")
        else:
            print(f"  ❌ {anchor} -> {url[:50]}... (锚点未找到)")

    # 5. 测试锚点替换功能
    print("\n🔄 测试锚点替换功能:")
    replaced_content = article.replace_image_anchors_with_urls()
    print("📝 替换后内容预览:")
    replaced_lines = replaced_content.split("\n")
    for i, line in enumerate(replaced_lines[:10], 1):  # 显示前10行
        if "[图片:" in line:
            print(f"  {i:2d}. [图片URL] {line}")
        else:
            print(f"  {i:2d}. {line}")


def save_article_with_anchors(article):
    """保存包含锚点的文章"""
    output_dir = Path("data/articles")
    output_dir.mkdir(parents=True, exist_ok=True)

    filename = f"article_with_anchors_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = output_dir / filename

    # 转换为字典
    article_dict = {
        "article_id": article.article_id,
        "title": article.title,
        "content": article.content,
        "publish_time": article.publish_time.isoformat() if article.publish_time else None,
        "account_name": article.account_name,
        "url": article.url,
        "images": article.images,  # 现在是字典格式
        "tags": article.tags,
        "local_path": article.local_path,
        "created_at": article.created_at.isoformat(),
        "features": {
            "keywords": article.features.keywords if article.features else [],
            "summary": article.features.summary if article.features else "",
            "sentiment": article.features.sentiment if article.features else "neutral",
            "topic_category": article.features.topic_category if article.features else "",
            "tags": [],
        },
    }

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(article_dict, f, ensure_ascii=False, indent=2)

    print(f"\n💾 文章已保存: {filepath}")

    # 保存替换后的内容版本
    replaced_filename = f"article_replaced_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    replaced_filepath = output_dir / replaced_filename

    replaced_article_dict = article_dict.copy()
    replaced_article_dict["content"] = article.replace_image_anchors_with_urls()

    with open(replaced_filepath, "w", encoding="utf-8") as f:
        json.dump(replaced_article_dict, f, ensure_ascii=False, indent=2)

    print(f"💾 替换后文章已保存: {replaced_filepath}")


# 保留原来的main函数用于独立运行
async def main():
    """主函数"""
    try:
        await test_image_anchors()
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main())
