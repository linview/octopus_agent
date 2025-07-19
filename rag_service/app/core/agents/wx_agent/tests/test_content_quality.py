"""
内容质量测试脚本

验证爬取内容的完整性和质量
"""

import asyncio
import json
import requests
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

from agents.crawler_agent import CrawlerAgent


async def test_content_quality():
    """测试内容质量"""
    print("=" * 60)
    print("内容质量测试")
    print("=" * 60)
    
    # 配置
    config = {
        'crawler': {
            'headless': False,
            'max_articles': 1,
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
    ]
    
    # 创建CrawlerAgent
    crawler = CrawlerAgent(config)
    
    try:
        # 执行爬取任务
        input_data = {
            'article_urls': test_urls,
            'max_count': 1
        }
        
        print(f"🚀 开始执行爬取任务...")
        
        # 执行爬取
        articles = await crawler.execute(input_data)
        
        if not articles:
            print("❌ 没有爬取到文章")
            return
        
        article = articles[0]
        
        print(f"\n✅ 爬取完成！")
        print(f"📄 标题: {article.title}")
        print(f"👤 作者: {article.account_name}")
        print(f"📅 发布时间: {article.publish_time}")
        print(f"🖼️ 图片数量: {len(article.images)}")
        print(f"📝 内容长度: {len(article.content)} 字符")
        
        # 分析内容质量
        await analyze_content_quality(article)
        
        # 测试图片下载
        await test_image_download(article)
        
    except Exception as e:
        print(f"❌ 测试失败: {str(e)}")
        raise
    finally:
        await crawler._cleanup()


async def analyze_content_quality(article):
    """分析内容质量"""
    print("\n" + "=" * 40)
    print("内容质量分析")
    print("=" * 40)
    
    content = article.content
    
    # 1. 检查段落结构
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
    print(f"📊 段落数量: {len(paragraphs)}")
    
    # 2. 检查标题结构
    lines = content.split('\n')
    title_lines = [line for line in lines if line.strip() and len(line.strip()) < 50]
    print(f"📊 可能的标题行数: {len(title_lines)}")
    
    # 3. 检查内容完整性
    print(f"📊 内容字符数: {len(content)}")
    print(f"📊 非空行数: {len([line for line in lines if line.strip()])}")
    
    # 4. 显示前几段内容
    print("\n📝 内容预览（前3段）:")
    for i, para in enumerate(paragraphs[:3], 1):
        print(f"第{i}段: {para[:100]}...")
    
    # 5. 检查是否包含HTML标签
    html_tags = ['<p>', '<div>', '<span>', '<h1>', '<h2>', '<h3>', '<ul>', '<ol>', '<li>']
    found_tags = [tag for tag in html_tags if tag in content]
    if found_tags:
        print(f"✅ 发现HTML标签: {found_tags}")
    else:
        print("⚠️ 未发现HTML标签，内容可能是纯文本")
    
    # 6. 检查特殊字符
    special_chars = ['&nbsp;', '&amp;', '&lt;', '&gt;', '&quot;']
    found_special = [char for char in special_chars if char in content]
    if found_special:
        print(f"✅ 发现HTML实体: {found_special}")
    
    # 7. 检查内容结构
    if '2023年' in content and '2024年' in content and '2025年' in content:
        print("✅ 内容包含时间线结构")
    
    if 'cursor' in content.lower() and 'lingma' in content.lower():
        print("✅ 内容包含关键词")
    
    # 8. 检查段落长度分布
    para_lengths = [len(para) for para in paragraphs]
    if para_lengths:
        avg_length = sum(para_lengths) / len(para_lengths)
        print(f"📊 平均段落长度: {avg_length:.1f} 字符")
        print(f"📊 最长段落: {max(para_lengths)} 字符")
        print(f"📊 最短段落: {min(para_lengths)} 字符")


async def test_image_download(article):
    """测试图片下载"""
    print("\n" + "=" * 40)
    print("图片下载测试")
    print("=" * 40)
    
    if not article.images:
        print("⚠️ 没有图片需要下载")
        return
    
    # 创建图片目录
    image_dir = Path("data/images") / article.article_id
    image_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"📁 图片保存目录: {image_dir}")
    
    downloaded_images = []
    
    for i, image_url in enumerate(article.images, 1):
        try:
            print(f"\n🖼️ 下载图片 {i}/{len(article.images)}: {image_url}")
            
            # 解析URL获取文件扩展名
            parsed_url = urlparse(image_url)
            path = parsed_url.path
            if '?' in path:
                path = path.split('?')[0]
            
            # 确定文件扩展名
            if 'wx_fmt=png' in image_url:
                ext = '.png'
            elif 'wx_fmt=jpeg' in image_url or 'wx_fmt=jpg' in image_url:
                ext = '.jpg'
            else:
                ext = '.jpg'  # 默认
            
            filename = f"image_{i}{ext}"
            filepath = image_dir / filename
            
            # 下载图片
            headers = {
                'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Referer': article.url
            }
            
            response = requests.get(image_url, headers=headers, timeout=30)
            response.raise_for_status()
            
            # 保存图片
            with open(filepath, 'wb') as f:
                f.write(response.content)
            
            file_size = len(response.content)
            print(f"✅ 图片下载成功: {filepath} ({file_size} bytes)")
            
            downloaded_images.append(str(filepath))
            
        except Exception as e:
            print(f"❌ 图片下载失败: {str(e)}")
            continue
    
    # 更新文章信息
    if downloaded_images:
        article.local_path = str(image_dir)
        article.images = downloaded_images  # 更新为本地路径
        
        print(f"\n✅ 图片下载完成！")
        print(f"📁 本地路径: {article.local_path}")
        print(f"🖼️ 下载成功: {len(downloaded_images)}/{len(article.images)} 张图片")
        
        # 保存更新后的文章信息
        save_updated_article(article)
    else:
        print("❌ 没有图片下载成功")


def save_updated_article(article):
    """保存更新后的文章信息"""
    output_dir = Path("data/articles")
    output_dir.mkdir(parents=True, exist_ok=True)
    
    filename = f"article_updated_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    filepath = output_dir / filename
    
    # 转换为字典
    article_dict = {
        'article_id': article.article_id,
        'title': article.title,
        'content': article.content,
        'publish_time': article.publish_time.isoformat() if article.publish_time else None,
        'account_name': article.account_name,
        'url': article.url,
        'images': article.images,  # 现在是本地路径
        'tags': article.tags,
        'local_path': article.local_path,
        'created_at': article.created_at.isoformat(),
        'features': {
            'keywords': article.features.keywords if article.features else [],
            'summary': article.features.summary if article.features else "",
            'sentiment': article.features.sentiment if article.features else "neutral",
            'topic_category': article.features.topic_category if article.features else "",
            'tags': []
        }
    }
    
    with open(filepath, 'w', encoding='utf-8') as f:
        json.dump(article_dict, f, ensure_ascii=False, indent=2)
    
    print(f"💾 更新后的文章信息已保存: {filepath}")


async def main():
    """主函数"""
    try:
        await test_content_quality()
    except Exception as e:
        print(f"❌ 测试执行失败: {str(e)}")


if __name__ == "__main__":
    asyncio.run(main()) 