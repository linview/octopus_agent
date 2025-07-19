"""
简化版爬虫功能测试脚本

验证CrawlerAgent的基础架构，不依赖Playwright
"""

import asyncio
import json
from datetime import datetime
from typing import Dict, Any

from core.base_agent import AsyncBaseAgent
from models.article import Article, ArticleMeta, ArticleFeatures


class MockCrawlerAgent(AsyncBaseAgent):
    """模拟爬虫Agent，用于验证基础架构"""
    
    def __init__(self, config: Dict[str, Any]):
        super().__init__(config)
        self.crawler_config = self.config.get('crawler', {})
        
    async def _process(self, input_data: Dict) -> list:
        """
        模拟爬虫任务
        
        Args:
            input_data: 输入数据，包含account_name和max_count
            
        Returns:
            模拟的文章列表
        """
        try:
            # 1. 解析输入参数
            account_name = input_data.get('account_name')
            max_count = input_data.get('max_count', self.crawler_config.get('max_articles', 10))
            
            if not account_name:
                raise Exception("account_name is required")
            
            self.logger.info(f"开始模拟爬取公众号: {account_name}, 目标数量: {max_count}")
            
            # 2. 模拟浏览器启动
            await self._mock_launch_browser()
            
            # 3. 模拟访问公众号主页
            await self._mock_visit_account_page(account_name)
            
            # 4. 模拟获取文章列表
            article_list = await self._mock_get_article_list(max_count)
            
            # 5. 模拟获取文章详情
            articles = await self._mock_get_article_details(article_list)
            
            # 6. 模拟下载媒体文件
            await self._mock_download_media(articles)
            
            self.logger.info(f"模拟爬取完成，共获取 {len(articles)} 篇文章")
            return articles
            
        except Exception as e:
            self.logger.error(f"模拟爬虫执行失败: {str(e)}")
            raise
        finally:
            # 模拟清理资源
            await self._mock_cleanup()
    
    async def _mock_launch_browser(self) -> None:
        """模拟启动浏览器"""
        self.logger.info("模拟启动浏览器...")
        await asyncio.sleep(0.1)  # 模拟启动时间
        self.logger.info("模拟浏览器启动成功")
    
    async def _mock_visit_account_page(self, account_name: str) -> None:
        """模拟访问公众号主页"""
        self.logger.info(f"模拟访问公众号主页: {account_name}")
        await asyncio.sleep(0.5)  # 模拟页面加载时间
        self.logger.info(f"模拟页面加载完成: {account_name}")
    
    async def _mock_get_article_list(self, max_count: int) -> list:
        """模拟获取文章列表"""
        self.logger.info(f"模拟获取文章列表，目标数量: {max_count}")
        
        article_list = []
        for i in range(min(max_count, 5)):  # 限制为5篇进行测试
            article_meta = ArticleMeta(
                title=f"测试文章标题 {i+1}",
                url=f"https://mp.weixin.qq.com/s/test_article_{i+1}",
                publish_time=datetime.now(),
                account_name="test_account",
                summary=f"这是第{i+1}篇测试文章的摘要",
                cover_image=f"https://example.com/cover_{i+1}.jpg"
            )
            article_list.append(article_meta)
            await asyncio.sleep(0.2)  # 模拟滚动加载
        
        self.logger.info(f"模拟获取到 {len(article_list)} 篇文章")
        return article_list
    
    async def _mock_get_article_details(self, article_list: list) -> list:
        """模拟获取文章详情"""
        self.logger.info(f"模拟获取文章详情，共 {len(article_list)} 篇")
        
        articles = []
        for i, article_meta in enumerate(article_list):
            # 模拟解析文章内容
            content = f"""
            这是{article_meta.title}的完整内容。
            
            第一段：这是文章的开头部分，介绍文章的主要内容和背景。
            
            第二段：这是文章的正文部分，包含详细的分析和讨论。
            
            第三段：这是文章的结尾部分，总结全文并给出结论。
            
            文章包含了丰富的内容和深入的分析，符合公众号文章的特点。
            """
            
            # 模拟提取图片
            images = [
                f"https://example.com/image1_{i+1}.jpg",
                f"https://example.com/image2_{i+1}.jpg"
            ]
            
            # 创建默认的ArticleFeatures
            features = ArticleFeatures()
            
            # 构建完整文章对象
            article = Article(
                title=article_meta.title,
                content=content,
                publish_time=article_meta.publish_time,
                account_name=article_meta.account_name,
                url=article_meta.url,
                images=images,
                tags=["测试", "示例"],
                features=features,
                local_path=None,
                created_at=datetime.now(),
                updated_at=datetime.now(),
                metadata={
                    "crawled_by": "MockCrawlerAgent",
                    "crawl_time": datetime.now().isoformat()
                }
            )
            articles.append(article)
            await asyncio.sleep(0.3)  # 模拟处理时间
        
        self.logger.info(f"模拟成功获取 {len(articles)} 篇文章详情")
        return articles
    
    async def _mock_download_media(self, articles: list) -> None:
        """模拟下载媒体文件"""
        self.logger.info(f"模拟开始下载媒体文件，共 {len(articles)} 篇文章")
        
        for article in articles:
            if article.images:
                # 模拟下载图片
                for i, image_url in enumerate(article.images):
                    local_path = f"data/images/article_{hash(article.title)}/image_{i}.jpg"
                    self.logger.debug(f"模拟下载图片: {image_url} -> {local_path}")
                    article.images[i] = local_path
                
                # 更新文章本地路径
                article.local_path = f"data/images/article_{hash(article.title)}"
        
        self.logger.info("模拟媒体文件下载完成")
    
    async def _mock_cleanup(self) -> None:
        """模拟清理资源"""
        self.logger.info("模拟浏览器资源清理完成")
    
    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        return {
            "agent_name": self.agent_name,
            "status": "healthy",
            "browser_ready": True,  # 模拟浏览器就绪
            "config": {
                "max_articles": self.crawler_config.get('max_articles'),
                "delay": self.crawler_config.get('delay'),
                "headless": self.crawler_config.get('headless')
            }
        }


async def test_mock_crawler():
    """测试模拟爬虫功能"""
    print("🚀 开始测试MockCrawlerAgent基础功能...")
    
    # 创建模拟配置
    config = {
        'crawler': {
            'max_articles': 10,
            'delay': 2.0,
            'headless': True,
            'browser_type': 'chromium'
        }
    }
    
    # 创建MockCrawlerAgent
    crawler = MockCrawlerAgent(config)
    
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
        
        print(f"\n✅ 模拟爬虫测试完成!")
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


async def test_error_handling():
    """测试错误处理"""
    print("\n🛡️ 测试错误处理...")
    
    config = {'crawler': {}}
    crawler = MockCrawlerAgent(config)
    
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
    print("MockCrawlerAgent 第一阶段功能验证")
    print("=" * 60)
    
    # 测试基础功能
    basic_success = await test_mock_crawler()
    
    # 测试错误处理
    error_success = await test_error_handling()
    
    # 总结
    print("\n" + "=" * 60)
    print("测试总结:")
    print(f"基础功能测试: {'✅ 通过' if basic_success else '❌ 失败'}")
    print(f"错误处理测试: {'✅ 通过' if error_success else '❌ 失败'}")
    
    if basic_success and error_success:
        print("\n🎉 第一阶段功能验证成功!")
        print("CrawlerAgent基础架构工作正常，可以进行下一步开发。")
        print("\n下一步计划:")
        print("1. 安装Playwright并实现真实浏览器控制")
        print("2. 实现真实的页面解析逻辑")
        print("3. 实现真实的媒体文件下载")
    else:
        print("\n⚠️ 存在问题需要修复。")
    
    print("=" * 60)


if __name__ == "__main__":
    asyncio.run(main()) 