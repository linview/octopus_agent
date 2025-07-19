"""
测试CrawlerAgent功能

验证第一版CrawlerAgent的基本功能
"""

import asyncio
import json
from datetime import datetime
from pathlib import Path

from agents.crawler_agent import CrawlerAgent


async def test_crawler_agent():
    """测试CrawlerAgent功能"""
    print("=" * 60)
    print("CrawlerAgent功能测试")
    print("=" * 60)
    
    # 配置
    config = {
        'crawler': {
            'headless': False,  # 有头模式，便于调试
            'max_articles': 5,
            'delay': 2.0,
            'timeout': 60
        },
        'logging': {
            'level': 'INFO',
            'format': '{time:YYYY-MM-DD HH:mm:ss} | {level} | {message}'
        }
    }
    
    # 测试文章URL
    test_urls = [
        "https://mp.weixin.qq.com/s/8xJcEI1Mx1lYeCvQsK7t9Q",
        # 可以添加更多测试URL
    ]
    
    # 创建CrawlerAgent
    crawler = CrawlerAgent(config)
    
    try:
        # 健康检查
        health = await crawler.health_check()
        print(f"🔄 Agent健康状态: {health}")
        
        # 执行爬取任务
        input_data = {
            'article_urls': test_urls,
            'max_count': 2
        }
        
        print(f"\n🚀 开始执行爬取任务...")
        print(f"📝 目标URL数量: {len(test_urls)}")
        print(f"📊 最大爬取数量: {input_data['max_count']}")
        
        # 执行爬取
        articles = await crawler.execute(input_data)
        
        print(f"\n✅ 爬取完成！")
        print(f"📊 成功爬取文章数量: {len(articles)}")
        
        # 保存结果
        output_dir = Path("data/articles")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        for i, article in enumerate(articles, 1):
            # 保存为JSON
            filename = f"article_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
            filepath = output_dir / filename
            
            # 转换为字典
            article_dict = {
                'article_id': article.article_id,
                'title': article.title,
                'content': article.content,
                'publish_time': article.publish_time.isoformat() if article.publish_time else None,
                'account_name': article.account_name,
                'url': article.url,
                'images': article.images,
                'tags': article.tags,
                'local_path': article.local_path,
                'created_at': article.created_at.isoformat(),
                'features': {
                    'keywords': article.features.keywords if article.features else [],
                    'summary': article.features.summary if article.features else "",
                    'sentiment': article.features.sentiment if article.features else "neutral",
                    'topic_category': article.features.topic_category if article.features else "",
                    'tags': []  # ArticleFeatures没有tags属性
                }
            }
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(article_dict, f, ensure_ascii=False, indent=2)
            
            print(f"💾 文章 {i} 已保存: {filepath}")
            
            # 显示文章基本信息
            print(f"📄 标题: {article.title}")
            print(f"👤 作者: {article.account_name}")
            print(f"📅 发布时间: {article.publish_time}")
            print(f"🖼️ 图片数量: {len(article.images)}")
            print(f"📝 内容长度: {len(article.content)} 字符")
            print("-" * 40)
        
        # 最终健康检查
        final_health = await crawler.health_check()
        print(f"🔄 最终健康状态: {final_health}")
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        raise
    finally:
        # 清理资源
        await crawler._cleanup()


async def main():
    """主函数"""
    try:
        await test_crawler_agent()
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 