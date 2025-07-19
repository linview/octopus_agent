"""
Playwright基础功能测试

验证Playwright是否能正常工作
"""

import asyncio
from playwright.async_api import async_playwright


async def test_playwright_basic():
    """测试Playwright基础功能"""
    print("🚀 开始测试Playwright基础功能...")
    
    try:
        async with async_playwright() as p:
            # 启动浏览器
            browser = await p.chromium.launch(headless=True)
            
            # 创建页面
            page = await browser.new_page()
            
            # 访问一个简单的页面
            await page.goto('https://www.baidu.com')
            
            # 获取页面标题
            title = await page.title()
            print(f"✅ 成功访问页面，标题: {title}")
            
            # 关闭浏览器
            await browser.close()
            
            print("✅ Playwright基础功能测试通过")
            return True
            
    except Exception as e:
        print(f"❌ Playwright测试失败: {str(e)}")
        return False


async def main():
    """主函数"""
    print("=" * 50)
    print("Playwright基础功能验证")
    print("=" * 50)
    
    success = await test_playwright_basic()
    
    if success:
        print("\n🎉 Playwright环境配置成功！")
        print("可以进行下一步的爬虫开发。")
    else:
        print("\n⚠️ Playwright环境存在问题，需要修复。")
    
    print("=" * 50)


if __name__ == "__main__":
    asyncio.run(main()) 