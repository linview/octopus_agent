"""
基础爬虫功能测试脚本

验证CrawlerAgent的第一阶段功能
"""

import asyncio
import json
from datetime import datetime

from agents.crawler_agent import CrawlerAgent
from utils.config import load_config


async def test_crawler_basic():
    """测试基础爬虫功能"""
    print("🚀 开始测试CrawlerAgent基础功能...")
    
    # 加载配置
    config = load_config()
    
    # 创建CrawlerAgent
    crawler = CrawlerAgent(config.to_dict())
    
    try:
        # 测试健康检查
        print("\n📋 测试健康检查...")
        health = await crawler.health_check()
        print(f"健康状态: {json.dumps(health, ensure_ascii=False, indent=2)}")
        
        # 测试基础爬虫功能
        print("\n🕷️ 测试基础爬虫功能...")
        input_data = {
            'account_name': 'test_account',
            'max_count': 3  # 只爬取3篇进行测试
        }
        
        start_time = datetime.now()
        articles = await crawler.execute(input_data)
        end_time = datetime.now()
        
        print(f"\n✅ 爬虫测试完成!")
        print(f"耗时: {(end_time - start_time).total_seconds():.2f}秒")
        print(f"获取文章数量: {len(articles)}")
        
        # 显示文章信息
        for i, article in enumerate(articles, 1):
            print(f"\n📄 文章 {i}:")
            print(f"  标题: {article.title}")
            print(f"  链接: {article.url}")
            print(f"  发布时间: {article.publish_time}")
            print(f"  内容长度: {len(article.content)} 字符")
            print(f"  图片数量: {len(article.images)}")
            print(f"  本地路径: {article.local_path}")
        
        # 测试状态信息
        print(f"\n📊 Agent状态:")
        status = crawler.get_status()
        print(f"  执行次数: {status['execution_count']}")
        print(f"  最后执行: {status['last_execution']}")
        
        return True
        
    except Exception as e:
        print(f"\n❌ 测试失败: {str(e)}")
        return False


async def test_crawler_error_handling():
    """测试错误处理"""
    print("\n🛡️ 测试错误处理...")
    
    config = load_config()
    crawler = CrawlerAgent(config.to_dict())
    
    try:
        # 测试缺少必要参数
        print("测试缺少account_name参数...")
        await crawler.execute({'max_count': 5})
        print("❌ 应该抛出异常但没有")
        return False
        
    except Exception as e:
        print(f"✅ 正确捕获异常: {str(e)}")
        return True


async def main():
    """主测试函数"""
    print("=" * 60)
    print("CrawlerAgent 第一阶段功能验证")
    print("=" * 60)
    
    # 测试基础功能
    basic_success = await test_crawler_basic()
    
    # 测试错误处理
    error_success = await test_crawler_error_handling()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"基础功能测试: {'✅ 通过' if basic_success else '❌ 失败'}")
    print(f"错误处理测试: {'✅ 通过' if error_success else '❌ 失败'}")
    
    if basic_success and error_success:
        print("\n🎉 第一阶段功能验证成功!")
        print("CrawlerAgent基础架构工作正常，可以进行下一步开发。")
    else:
        print("\n⚠️ 存在问题需要修复。")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 