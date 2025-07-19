"""
单篇文章爬取功能测试

验证通过Playwright爬取微信公众号单篇文章的可行性
"""

import asyncio
import json
import random
import sys
from datetime import datetime
from pathlib import Path
from playwright.async_api import async_playwright

# 添加项目根目录到Python路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


class SingleArticleCrawler:
    """单篇文章爬取器"""
    
    def __init__(self):
        self.browser = None
        self.page = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # 改为有头模式，便于调试
            args=[
                '--no-sandbox',
                '--disable-setuid-sandbox',
                '--disable-dev-shm-usage',
                '--disable-accelerated-2d-canvas',
                '--no-first-run',
                '--no-zygote',
                '--disable-gpu',
                '--disable-web-security',
                '--disable-features=VizDisplayCompositor'
            ]
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        if self.browser:
            await self.browser.close()
        if self.playwright:
            await self.playwright.stop()
    
    async def crawl_article(self, article_url: str) -> dict:
        """爬取单篇文章"""
        print(f"🚀 开始爬取文章: {article_url}")
        
        try:
            # 创建新页面
            self.page = await self.browser.new_page()
            
            # 设置视口大小
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 设置用户代理
            user_agents = [
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
                'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
            ]
            await self.page.set_extra_http_headers({
                'User-Agent': random.choice(user_agents),
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # 访问文章页面
            print("📄 正在访问文章页面...")
            
            # 使用更宽松的等待条件
            try:
                await self.page.goto(article_url, wait_until='domcontentloaded', timeout=60000)
            except Exception as e:
                print(f"⚠️ 页面加载超时，尝试继续解析: {str(e)}")
                # 即使超时也尝试解析页面内容
            
            # 等待页面加载完成
            await asyncio.sleep(3)
            
            # 检查页面是否正常加载
            page_title = await self.page.title()
            print(f"📄 页面标题: {page_title}")
            
            # 检查是否有反爬虫检测
            if "环境异常" in page_title or "访问受限" in page_title:
                print("⚠️ 检测到反爬虫机制，尝试绕过...")
                return await self.handle_anti_crawler()
            
            # 解析文章内容
            article_data = await self.parse_article_content()
            
            print(f"✅ 文章爬取成功: {article_data.get('title', '未知标题')}")
            return article_data
            
        except Exception as e:
            print(f"❌ 文章爬取失败: {str(e)}")
            # 尝试获取页面截图用于调试
            try:
                screenshot_path = f"debug_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.page.screenshot(path=screenshot_path)
                print(f"📸 调试截图已保存: {screenshot_path}")
            except:
                pass
            raise
        finally:
            if self.page:
                await self.page.close()
    
    async def handle_anti_crawler(self) -> dict:
        """处理反爬虫检测"""
        print("🔄 尝试处理反爬虫检测...")
        
        try:
            # 等待一段时间
            await asyncio.sleep(5)
            
            # 尝试刷新页面
            await self.page.reload()
            await asyncio.sleep(3)
            
            # 再次检查页面内容
            page_title = await self.page.title()
            print(f"🔄 刷新后页面标题: {page_title}")
            
            # 如果仍然有问题，返回错误信息
            if "环境异常" in page_title or "访问受限" in page_title:
                return {
                    'title': '反爬虫检测',
                    'content': f'页面显示: {page_title}，可能触发了微信的反爬虫机制',
                    'publish_time': None,
                    'author': None,
                    'image_urls': [],
                    'crawled_at': datetime.now().isoformat(),
                    'url': self.page.url,
                    'error': 'anti_crawler_detected'
                }
            
            # 如果刷新成功，尝试解析
            return await self.parse_article_content()
            
        except Exception as e:
            return {
                'title': '反爬虫处理失败',
                'content': f'处理反爬虫检测时出错: {str(e)}',
                'publish_time': None,
                'author': None,
                'image_urls': [],
                'crawled_at': datetime.now().isoformat(),
                'url': self.page.url,
                'error': 'anti_crawler_handling_failed'
            }
    
    async def parse_article_content(self) -> dict:
        """解析文章内容"""
        try:
            # 获取页面HTML用于调试
            page_html = await self.page.content()
            
            # 获取文章标题 - 优化选择器
            title_selectors = [
                '#activity-name',  # 微信公众号文章标题
                'h1', 
                '.rich_media_title',
                'title'  # 页面title标签
            ]
            title = "未知标题"
            for selector in title_selectors:
                try:
                    if selector == 'title':
                        # 特殊处理title标签
                        title = await self.page.title()
                    else:
                        title_element = await self.page.locator(selector).first
                        if await title_element.count() > 0:
                            title = await title_element.text_content()
                    
                    title = title.strip() if title else "未知标题"
                    if title and title != "未知标题" and len(title) > 5:
                        print(f"✅ 找到标题: {title} (选择器: {selector})")
                        break
                except Exception as e:
                    print(f"❌ 标题选择器 {selector} 失败: {str(e)}")
                    continue
            
            # 获取文章内容
            content_selectors = ['#js_content', '.rich_media_content', '.content']
            content = "无法获取文章内容"
            for selector in content_selectors:
                try:
                    content_elements = await self.page.locator(selector).all()
                    if content_elements:
                        content = await content_elements[0].inner_text()
                        if content and len(content.strip()) > 50:  # 确保内容不为空
                            print(f"✅ 找到内容 (选择器: {selector})")
                            break
                except Exception as e:
                    print(f"❌ 内容选择器 {selector} 失败: {str(e)}")
                    continue
            
            # 获取发布时间 - 优化选择器
            time_selectors = [
                '#publish_time', 
                '.publish_time', 
                '.time',
                '.rich_media_meta_text',  # 微信公众号时间
                '[id*="time"]',  # 包含time的id
                '[class*="time"]'  # 包含time的class
            ]
            publish_time = None
            for selector in time_selectors:
                try:
                    time_elements = await self.page.locator(selector).all()
                    for element in time_elements:
                        time_text = await element.text_content()
                        if time_text and ('202' in time_text or '年' in time_text or '月' in time_text):
                            publish_time = time_text.strip()
                            print(f"✅ 找到发布时间: {publish_time} (选择器: {selector})")
                            break
                    if publish_time:
                        break
                except Exception as e:
                    print(f"❌ 时间选择器 {selector} 失败: {str(e)}")
                    continue
            
            # 获取作者信息 - 优化选择器
            author_selectors = [
                '#js_name', 
                '.account_nickname', 
                '.author',
                '.rich_media_meta_nickname',  # 微信公众号作者
                '[id*="name"]',  # 包含name的id
                '[class*="name"]'  # 包含name的class
            ]
            author = "未知作者"
            for selector in author_selectors:
                try:
                    author_elements = await self.page.locator(selector).all()
                    for element in author_elements:
                        author_text = await element.text_content()
                        if author_text and len(author_text.strip()) > 1:
                            author = author_text.strip()
                            print(f"✅ 找到作者: {author} (选择器: {selector})")
                            break
                    if author and author != "未知作者":
                        break
                except Exception as e:
                    print(f"❌ 作者选择器 {selector} 失败: {str(e)}")
                    continue
            
            # 获取图片链接
            image_selectors = ['#js_content img', '.rich_media_content img', 'img']
            image_urls = []
            for selector in image_selectors:
                try:
                    images = await self.page.locator(selector).all()
                    for img in images:
                        src = await img.get_attribute('src')
                        if src and src.startswith('http'):
                            image_urls.append(src)
                    if image_urls:
                        print(f"✅ 找到 {len(image_urls)} 张图片 (选择器: {selector})")
                        break
                except Exception as e:
                    print(f"❌ 图片选择器 {selector} 失败: {str(e)}")
                    continue
            
            return {
                'title': title,
                'content': content,
                'publish_time': publish_time,
                'author': author,
                'image_urls': image_urls,
                'crawled_at': datetime.now().isoformat(),
                'url': self.page.url,
                'content_length': len(content),
                'html_length': len(page_html)
            }
            
        except Exception as e:
            print(f"❌ 解析文章内容失败: {str(e)}")
            return {
                'title': '解析失败',
                'content': f'解析失败: {str(e)}',
                'publish_time': None,
                'author': None,
                'image_urls': [],
                'crawled_at': datetime.now().isoformat(),
                'url': self.page.url,
                'error': 'parsing_failed'
            }


async def test_single_article_crawling():
    """测试单篇文章爬取功能"""
    print("=" * 60)
    print("单篇文章爬取功能测试")
    print("=" * 60)
    
    # 测试文章URL（需要替换为真实的微信公众号文章URL）
    test_urls = [
        "https://mp.weixin.qq.com/s/8xJcEI1Mx1lYeCvQsK7t9Q",
        # "https://mp.weixin.qq.com/s/example1",  # 替换为真实URL
        # "https://mp.weixin.qq.com/s/example2",  # 替换为真实URL
    ]
    
    if not test_urls:
        print("⚠️ 请提供测试用的微信公众号文章URL")
        print("示例格式: https://mp.weixin.qq.com/s/xxxxx")
        return
    
    # 创建输出目录 - 从tests目录执行时，需要回到项目根目录
    project_root = Path(__file__).parent.parent
    output_dir = project_root / "data" / "test_articles"
    output_dir.mkdir(parents=True, exist_ok=True)
    
    async with SingleArticleCrawler() as crawler:
        for i, url in enumerate(test_urls, 1):
            print(f"\n📝 测试文章 {i}/{len(test_urls)}")
            
            try:
                # 爬取文章
                article_data = await crawler.crawl_article(url)
                
                # 保存文章数据
                filename = f"article_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
                filepath = output_dir / filename
                
                with open(filepath, 'w', encoding='utf-8') as f:
                    json.dump(article_data, f, ensure_ascii=False, indent=2)
                
                print(f"💾 文章数据已保存: {filepath}")
                
                # 显示文章基本信息
                print(f"📄 标题: {article_data['title']}")
                print(f"👤 作者: {article_data['author']}")
                print(f"📅 发布时间: {article_data['publish_time']}")
                print(f"🖼️ 图片数量: {len(article_data['image_urls'])}")
                print(f"📝 内容长度: {article_data.get('content_length', len(article_data['content']))} 字符")
                
                if 'error' in article_data:
                    print(f"⚠️ 错误类型: {article_data['error']}")
                
            except Exception as e:
                print(f"❌ 测试失败: {str(e)}")
                continue
    
    print("\n" + "=" * 60)
    print("测试完成")
    print("=" * 60)


async def main():
    """主函数"""
    try:
        await test_single_article_crawling()
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 