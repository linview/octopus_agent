"""
图片解析测试脚本

验证是否完整获取了文章中的所有图片URL
"""

import asyncio
import json
import re
from datetime import datetime
from pathlib import Path

from playwright.async_api import async_playwright


class ImageParsingTester:
    """图片解析测试器"""
    
    def __init__(self):
        self.browser = None
        self.page = None
    
    async def __aenter__(self):
        """异步上下文管理器入口"""
        self.playwright = await async_playwright().start()
        self.browser = await self.playwright.chromium.launch(
            headless=False,  # 有头模式，便于调试
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
    
    async def test_image_parsing(self, article_url: str):
        """测试图片解析"""
        print(f"🚀 开始测试图片解析: {article_url}")
        
        try:
            # 创建新页面
            self.page = await self.browser.new_page()
            
            # 设置视口大小
            await self.page.set_viewport_size({"width": 1920, "height": 1080})
            
            # 设置用户代理
            await self.page.set_extra_http_headers({
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
                'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
                'Accept-Encoding': 'gzip, deflate, br',
                'Connection': 'keep-alive',
                'Upgrade-Insecure-Requests': '1'
            })
            
            # 访问文章页面
            print("📄 正在访问文章页面...")
            
            try:
                await self.page.goto(article_url, wait_until='domcontentloaded', timeout=60000)
            except Exception as e:
                print(f"⚠️ 页面加载超时，尝试继续解析: {str(e)}")
            
            # 等待页面加载完成
            await asyncio.sleep(3)
            
            # 检查页面是否正常加载
            page_title = await self.page.title()
            print(f"📄 页面标题: {page_title}")
            
            # 开始图片解析测试
            await self.analyze_all_images()
            
        except Exception as e:
            print(f"❌ 测试失败: {str(e)}")
            raise
        finally:
            if self.page:
                await self.page.close()
    
    async def analyze_all_images(self):
        """分析页面中的所有图片"""
        print("\n" + "=" * 50)
        print("图片解析分析")
        print("=" * 50)
        
        # 1. 获取页面HTML
        page_html = await self.page.content()
        
        # 2. 使用正则表达式查找所有图片
        print("🔍 使用正则表达式查找图片...")
        img_patterns = [
            r'<img[^>]+src=["\']([^"\']+)["\'][^>]*>',  # 标准img标签
            r'background-image:\s*url\(["\']?([^"\')\s]+)["\']?\)',  # CSS背景图片
            r'data-src=["\']([^"\']+)["\']',  # 懒加载图片
            r'data-original=["\']([^"\']+)["\']',  # 另一种懒加载
        ]
        
        all_images = []
        for pattern in img_patterns:
            matches = re.findall(pattern, page_html, re.IGNORECASE)
            all_images.extend(matches)
        
        # 去重并过滤
        unique_images = list(set(all_images))
        valid_images = [img for img in unique_images if img.startswith('http')]
        
        print(f"📊 正则表达式找到图片数量: {len(valid_images)}")
        
        # 3. 使用Playwright选择器查找图片
        print("\n🔍 使用Playwright选择器查找图片...")
        selectors_to_test = [
            'img',  # 所有img标签
            '#js_content img',  # 文章内容中的图片
            '.rich_media_content img',  # 富媒体内容中的图片
            '[data-src]',  # 有data-src属性的元素
            '[data-original]',  # 有data-original属性的元素
            '[style*="background-image"]',  # 有背景图片的元素
        ]
        
        playwright_images = []
        for selector in selectors_to_test:
            try:
                elements = await self.page.locator(selector).all()
                print(f"  {selector}: 找到 {len(elements)} 个元素")
                
                for element in elements:
                    # 获取src属性
                    src = await element.get_attribute('src')
                    if src and src.startswith('http'):
                        playwright_images.append(src)
                    
                    # 获取data-src属性（懒加载）
                    data_src = await element.get_attribute('data-src')
                    if data_src and data_src.startswith('http'):
                        playwright_images.append(data_src)
                    
                    # 获取data-original属性
                    data_original = await element.get_attribute('data-original')
                    if data_original and data_original.startswith('http'):
                        playwright_images.append(data_original)
                    
                    # 获取style属性中的背景图片
                    style = await element.get_attribute('style')
                    if style and 'background-image' in style:
                        bg_match = re.search(r'url\(["\']?([^"\')\s]+)["\']?\)', style)
                        if bg_match:
                            bg_url = bg_match.group(1)
                            if bg_url.startswith('http'):
                                playwright_images.append(bg_url)
                
            except Exception as e:
                print(f"  ❌ {selector} 选择器失败: {str(e)}")
        
        # 去重
        playwright_images = list(set(playwright_images))
        print(f"📊 Playwright选择器找到图片数量: {len(playwright_images)}")
        
        # 4. 合并所有找到的图片
        all_found_images = list(set(valid_images + playwright_images))
        print(f"📊 总共找到图片数量: {len(all_found_images)}")
        
        # 5. 分析图片类型
        wechat_images = [img for img in all_found_images if 'mmbiz.qpic.cn' in img]
        other_images = [img for img in all_found_images if 'mmbiz.qpic.cn' not in img]
        
        print(f"📊 微信图片数量: {len(wechat_images)}")
        print(f"📊 其他图片数量: {len(other_images)}")
        
        # 6. 显示所有图片URL
        print(f"\n📋 所有图片URL列表:")
        for i, img_url in enumerate(all_found_images, 1):
            img_type = "微信图片" if 'mmbiz.qpic.cn' in img_url else "其他图片"
            print(f"  {i:2d}. [{img_type}] {img_url}")
        
        # 7. 保存分析结果
        analysis_result = {
            'total_images': len(all_found_images),
            'wechat_images': len(wechat_images),
            'other_images': len(other_images),
            'all_image_urls': all_found_images,
            'wechat_image_urls': wechat_images,
            'other_image_urls': other_images,
            'regex_images': valid_images,
            'playwright_images': playwright_images,
            'analysis_time': datetime.now().isoformat()
        }
        
        # 保存结果
        output_dir = Path("data/analysis")
        output_dir.mkdir(parents=True, exist_ok=True)
        
        filename = f"image_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        filepath = output_dir / filename
        
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(analysis_result, f, ensure_ascii=False, indent=2)
        
        print(f"\n💾 分析结果已保存: {filepath}")
        
        # 8. 与当前CrawlerAgent的结果对比
        await self.compare_with_crawler_result(all_found_images)
    
    async def compare_with_crawler_result(self, all_found_images):
        """与CrawlerAgent的结果对比"""
        print("\n" + "=" * 50)
        print("与CrawlerAgent结果对比")
        print("=" * 50)
        
        # 导入CrawlerAgent
        from agents.crawler_agent import CrawlerAgent
        
        # 创建CrawlerAgent并爬取同一篇文章
        config = {
            'crawler': {
                'headless': False,
                'max_articles': 1,
                'delay': 1.0,
                'timeout': 60
            }
        }
        
        crawler = CrawlerAgent(config)
        
        try:
            # 获取当前页面URL
            current_url = self.page.url
            
            # 使用CrawlerAgent爬取
            input_data = {
                'article_urls': [current_url],
                'max_count': 1
            }
            
            articles = await crawler.execute(input_data)
            
            if articles:
                article = articles[0]
                crawler_images = article.images
                
                print(f"📊 CrawlerAgent找到图片数量: {len(crawler_images)}")
                print(f"📊 完整分析找到图片数量: {len(all_found_images)}")
                
                # 找出缺失的图片
                missing_images = [img for img in all_found_images if img not in crawler_images]
                extra_images = [img for img in crawler_images if img not in all_found_images]
                
                print(f"📊 缺失的图片数量: {len(missing_images)}")
                print(f"📊 额外的图片数量: {len(extra_images)}")
                
                if missing_images:
                    print(f"\n❌ CrawlerAgent缺失的图片:")
                    for i, img_url in enumerate(missing_images, 1):
                        print(f"  {i}. {img_url}")
                
                if extra_images:
                    print(f"\n⚠️ CrawlerAgent额外的图片:")
                    for i, img_url in enumerate(extra_images, 1):
                        print(f"  {i}. {img_url}")
                
                # 计算准确率
                if all_found_images:
                    accuracy = len(crawler_images) / len(all_found_images) * 100
                    print(f"\n📊 CrawlerAgent图片解析准确率: {accuracy:.1f}%")
                
        except Exception as e:
            print(f"❌ 对比测试失败: {str(e)}")
        finally:
            await crawler._cleanup()


async def main():
    """主函数"""
    test_url = "https://mp.weixin.qq.com/s/8xJcEI1Mx1lYeCvQsK7t9Q"
    
    async with ImageParsingTester() as tester:
        await tester.test_image_parsing(test_url)


if __name__ == "__main__":
    asyncio.run(main()) 