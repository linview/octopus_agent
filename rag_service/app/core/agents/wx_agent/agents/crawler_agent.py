"""
爬虫Agent模块

实现微信公众号文章爬取功能
"""

import asyncio
import random
import time
from datetime import datetime
from typing import Any

from playwright.async_api import Browser, Page, async_playwright

from config.config import ConfigManager, CrawlerConfig
from core.base_agent import AsyncBaseAgent
from models.article import Article, ArticleFeatures
from utils.exceptions import CrawlerError


class CrawlerAgent(AsyncBaseAgent):
    """微信公众号文章爬虫Agent"""

    def __init__(self, config: CrawlerConfig | None = None):
        """
        初始化爬虫Agent

        Args:
            config: CrawlerConfig实例，如果为None则使用默认配置
        """
        # 使用默认配置或传入的配置
        if config is None:
            config = ConfigManager().get_crawler_config()

        # 将CrawlerConfig转换为字典传递给父类
        super().__init__(config.model_dump())

        self.browser: Browser | None = None
        self.page: Page | None = None
        self.crawler_config = config

    async def _process(self, input_data: dict) -> list[Article]:
        """
        执行爬虫任务

        Args:
            input_data: 输入数据，包含article_urls和max_count

        Returns:
            爬取到的文章列表
        """
        try:
            # 1. 解析输入参数
            article_urls = input_data.get("article_urls", [])
            max_count = input_data.get("max_count", self.crawler_config.max_articles)

            if not article_urls:
                raise CrawlerError("article_urls is required")

            self.logger.info(f"开始爬取文章，目标数量: {min(len(article_urls), max_count)}")

            # 2. 限制爬取数量
            article_urls = article_urls[:max_count]

            # 3. 爬取文章
            articles = await self.crawl_articles_by_urls(article_urls)

            self.logger.info(f"爬取完成，共获取 {len(articles)} 篇文章")
            return articles

        except (RuntimeError, ValueError, OSError) as e:
            self.logger.error(f"爬虫执行失败: {str(e)}")
            raise
        except Exception as e:
            # 捕获其他未预期的异常
            self.logger.error(f"爬虫执行出现未预期错误: {str(e)}")
            raise CrawlerError(f"爬虫执行失败: {str(e)}") from e
        finally:
            # 清理资源
            await self._cleanup()

    async def crawl_articles_by_urls(self, article_urls: list[str]) -> list[Article]:
        """
        通过文章URL列表爬取文章

        Args:
            article_urls: 文章URL列表

        Returns:
            文章列表
        """
        articles = []

        for i, url in enumerate(article_urls, 1):
            try:
                self.logger.info(f"爬取文章 {i}/{len(article_urls)}: {url}")

                # 爬取单篇文章
                article_data = await self.crawl_single_article(url)

                # 转换为Article对象
                article = self._convert_to_article(article_data)
                articles.append(article)

                # 随机延迟，避免被反爬
                delay = self.crawler_config.delay
                await asyncio.sleep(delay + random.uniform(0, 1))

            except (RuntimeError, ValueError, OSError, TimeoutError) as e:
                self.logger.error(f"爬取文章失败 {url}: {str(e)}")
                continue
            except Exception as e:
                # 捕获其他未预期的异常
                self.logger.error(f"爬取文章出现未预期错误 {url}: {str(e)}")
                continue

        return articles

    async def crawl_single_article(self, article_url: str) -> dict[str, Any]:
        """
        爬取单篇文章

        Args:
            article_url: 文章URL

        Returns:
            文章数据字典
        """
        try:
            # 1. 启动浏览器（如果未启动）
            if not self.browser:
                await self._launch_browser()

            # 2. 创建新页面
            self.page = await self.browser.new_page()

            # 3. 设置视口大小
            await self.page.set_viewport_size({"width": 1920, "height": 1080})

            # 4. 设置用户代理
            user_agents = [
                self.crawler_config.user_agent,
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ]
            await self.page.set_extra_http_headers(
                {
                    "User-Agent": random.choice(user_agents),
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
                    "Accept-Language": "zh-CN,zh;q=0.9,en;q=0.8",
                    "Accept-Encoding": "gzip, deflate, br",
                    "Connection": "keep-alive",
                    "Upgrade-Insecure-Requests": "1",
                }
            )

            # 5. 访问文章页面
            self.logger.info("正在访问文章页面...")

            try:
                timeout_ms = self.crawler_config.timeout * 1000
                await self.page.goto(article_url, wait_until="domcontentloaded", timeout=timeout_ms)
            except TimeoutError as e:
                self.logger.warning(f"页面加载超时，尝试继续解析: {str(e)}")
            except (RuntimeError, OSError) as e:
                self.logger.warning(f"页面加载失败，尝试继续解析: {str(e)}")

            # 6. 等待页面加载完成
            await asyncio.sleep(3)

            # 7. 检查页面是否正常加载
            page_title = await self.page.title()
            self.logger.info(f"页面标题: {page_title}")

            # 8. 检查是否有反爬虫检测
            if "环境异常" in page_title or "访问受限" in page_title:
                self.logger.warning("检测到反爬虫机制，尝试绕过...")
                return await self._handle_anti_crawler()

            # 9. 解析文章内容
            article_data = await self._parse_article_content()

            self.logger.info(f"文章爬取成功: {article_data.get('title', '未知标题')}")
            return article_data

        except RuntimeError as e:
            self.logger.error(f"文章爬取失败: {str(e)}")
            # 尝试获取页面截图用于调试
            try:
                screenshot_path = f"debug_screenshot_{datetime.now().strftime('%Y%m%d_%H%M%S')}.png"
                await self.page.screenshot(path=screenshot_path)
                self.logger.info(f"调试截图已保存: {screenshot_path}")
            except Exception:
                pass
            raise
        finally:
            if self.page:
                await self.page.close()

    async def _handle_anti_crawler(self) -> dict[str, Any]:
        """处理反爬虫检测"""
        self.logger.info("尝试处理反爬虫检测...")

        try:
            # 等待一段时间
            await asyncio.sleep(5)

            # 尝试刷新页面
            await self.page.reload()
            await asyncio.sleep(3)

            # 再次检查页面内容
            page_title = await self.page.title()
            self.logger.info(f"刷新后页面标题: {page_title}")

            # 如果仍然有问题，返回错误信息
            if "环境异常" in page_title or "访问受限" in page_title:
                return {
                    "title": "反爬虫检测",
                    "content": f"页面显示: {page_title}，可能触发了微信的反爬虫机制",
                    "publish_time": None,
                    "author": None,
                    "image_urls": [],
                    "crawled_at": datetime.now().isoformat(),
                    "url": self.page.url,
                    "error": "anti_crawler_detected",
                }

            # 如果刷新成功，尝试解析
            return await self._parse_article_content()

        except (RuntimeError, OSError, TimeoutError) as e:
            return {
                "title": "反爬虫处理失败",
                "content": f"处理反爬虫检测时出错: {str(e)}",
                "publish_time": None,
                "author": None,
                "image_urls": [],
                "crawled_at": datetime.now().isoformat(),
                "url": self.page.url,
                "error": "anti_crawler_handling_failed",
            }

    async def _parse_article_content(self) -> dict[str, Any]:
        """解析文章内容"""
        try:
            # 获取页面HTML用于调试
            page_html = await self.page.content()

            # 获取文章标题 - 优化选择器
            title_selectors = [
                "#activity-name",  # 微信公众号文章标题
                "h1",
                ".rich_media_title",
                "title",  # 页面title标签
            ]
            title = "未知标题"
            for selector in title_selectors:
                try:
                    if selector == "title":
                        # 特殊处理title标签
                        title = await self.page.title()
                    else:
                        title_element = await self.page.locator(selector).first
                        if await title_element.count() > 0:
                            title = await title_element.text_content()

                    title = title.strip() if title else "未知标题"
                    if title and title != "未知标题" and len(title) > 5:
                        self.logger.info(f"找到标题: {title} (选择器: {selector})")
                        break
                except (RuntimeError, OSError, TimeoutError) as e:
                    self.logger.debug(f"标题选择器 {selector} 失败: {str(e)}")
                    continue

            # 获取文章内容 - 支持图片锚点
            content_selectors = ["#js_content", ".rich_media_content", ".content"]
            content = "无法获取文章内容"
            content_with_images = ""
            image_data = {}

            for selector in content_selectors:
                try:
                    content_elements = await self.page.locator(selector).all()
                    if content_elements:
                        # 获取纯文本内容
                        content = await content_elements[0].inner_text()

                        # 获取包含图片的HTML内容
                        html_content = await content_elements[0].inner_html()

                        if content and len(content.strip()) > 50:  # 确保内容不为空
                            self.logger.info(f"找到内容 (选择器: {selector})")

                            # 根据配置决定是否提取图片
                            if self.crawler_config.save_images:
                                # 先提取图片数据
                                image_data = await self._extract_images_with_positions()

                                # 解析HTML内容，提取图片位置信息
                                content_with_images = await self._parse_content_with_images(
                                    html_content, content, image_data
                                )

                                # 验证锚点与图片数据的一致性
                                self._validate_image_anchors(content_with_images, image_data)
                            else:
                                self.logger.info("图片保存已禁用，跳过图片提取")
                                content_with_images = content

                            break
                except (RuntimeError, OSError, TimeoutError) as e:
                    self.logger.debug(f"内容选择器 {selector} 失败: {str(e)}")
                    continue

            # 获取发布时间 - 优化选择器
            time_selectors = [
                "#publish_time",
                ".publish_time",
                ".time",
                ".rich_media_meta_text",  # 微信公众号时间
                '[id*="time"]',  # 包含time的id
                '[class*="time"]',  # 包含time的class
            ]
            publish_time = None
            for selector in time_selectors:
                try:
                    time_elements = await self.page.locator(selector).all()
                    for element in time_elements:
                        time_text = await element.text_content()
                        if time_text and ("202" in time_text or "年" in time_text or "月" in time_text):
                            publish_time = time_text.strip()
                            self.logger.info(f"找到发布时间: {publish_time} (选择器: {selector})")
                            break
                    if publish_time:
                        break
                except (RuntimeError, OSError, TimeoutError) as e:
                    self.logger.debug(f"时间选择器 {selector} 失败: {str(e)}")
                    continue

            # 获取作者信息 - 优化选择器
            author_selectors = [
                "#js_name",
                ".account_nickname",
                ".author",
                ".rich_media_meta_nickname",  # 微信公众号作者
                '[id*="name"]',  # 包含name的id
                '[class*="name"]',  # 包含name的class
            ]
            author = "未知作者"
            for selector in author_selectors:
                try:
                    author_elements = await self.page.locator(selector).all()
                    for element in author_elements:
                        author_text = await element.text_content()
                        if author_text and len(author_text.strip()) > 1:
                            author = author_text.strip()
                            self.logger.info(f"找到作者: {author} (选择器: {selector})")
                            break
                    if author and author != "未知作者":
                        break
                except (RuntimeError, OSError, TimeoutError) as e:
                    self.logger.debug(f"作者选择器 {selector} 失败: {str(e)}")
                    continue

            return {
                "title": title,
                "content": content_with_images if content_with_images else content,
                "publish_time": publish_time,
                "author": author,
                "image_data": image_data,  # 包含图片URL和位置信息
                "crawled_at": datetime.now().isoformat(),
                "url": self.page.url,
                "content_length": len(content),
                "html_length": len(page_html),
            }

        except (RuntimeError, OSError, TimeoutError, ValueError) as e:
            self.logger.error(f"解析文章内容失败: {str(e)}")
            return {
                "title": "解析失败",
                "content": f"解析失败: {str(e)}",
                "publish_time": None,
                "author": None,
                "image_data": {},
                "crawled_at": datetime.now().isoformat(),
                "url": self.page.url,
                "error": "parsing_failed",
            }

    def _validate_image_anchors(self, content: str, image_data: dict[str, str]) -> None:
        """
        验证内容中的锚点与图片数据的一致性

        Args:
            content: 包含锚点的内容
            image_data: 图片数据字典
        """
        try:
            # 提取内容中的所有锚点
            import re

            anchor_pattern = r"\$img_(\d+)\$"
            content_anchors = re.findall(anchor_pattern, content)

            # 获取图片数据中的ID
            image_ids = [img_id.replace("img_", "") for img_id in image_data]

            # 验证数量一致性
            if len(content_anchors) != len(image_ids):
                self.logger.warning(f"锚点数量不匹配: 内容中{len(content_anchors)}个，图片数据中{len(image_ids)}个")

            # 验证ID一致性
            content_anchor_set = set(content_anchors)
            image_id_set = set(image_ids)

            if content_anchor_set != image_id_set:
                self.logger.warning(f"锚点ID不匹配: 内容中{content_anchor_set}，图片数据中{image_id_set}")

            self.logger.info(f"锚点验证完成: 内容中{len(content_anchors)}个锚点，图片数据中{len(image_ids)}个图片")

        except (ValueError, RuntimeError) as e:
            self.logger.error(f"锚点验证失败: {str(e)}")

    def _convert_to_article(self, article_data: dict[str, Any]) -> Article:
        """
        将爬取的数据转换为Article对象

        Args:
            article_data: 爬取的文章数据

        Returns:
            Article对象
        """
        try:
            # 解析发布时间
            publish_time = None
            if article_data.get("publish_time"):
                try:
                    # 尝试解析时间格式
                    time_str = article_data["publish_time"]
                    if "年" in time_str and "月" in time_str:
                        # 处理中文时间格式
                        time_str = time_str.replace("年", "-").replace("月", "-").replace("日", "")
                        publish_time = datetime.strptime(time_str, "%Y-%m-%d %H:%M")
                    else:
                        publish_time = datetime.fromisoformat(time_str)
                except RuntimeError as e:
                    self.logger.error(f"解析发布时间失败: {str(e)}")
                    publish_time = datetime.now()

            # 创建ArticleFeatures
            features = ArticleFeatures(keywords=[], summary="", sentiment="neutral", category="", tags=[])

            # 创建Article对象
            article = Article(
                article_id=f"article_{int(time.time())}_{random.randint(1000, 9999)}",
                title=article_data.get("title", "未知标题"),
                content=article_data.get("content", ""),
                publish_time=publish_time or datetime.now(),
                account_name=article_data.get("author", "未知作者"),
                url=article_data.get("url", ""),
                images=article_data.get("image_data", {}),  # 使用新的图片数据结构
                tags=[],
                features=features,
                local_path="",
                created_at=datetime.now(),
            )

            return article

        except (ValueError, RuntimeError, TypeError) as e:
            self.logger.error(f"转换Article对象失败: {str(e)}")
            # 返回一个基本的Article对象
            return Article(
                article_id=f"error_{int(time.time())}",
                title="转换失败",
                content=f"转换失败: {str(e)}",
                publish_time=datetime.now(),
                account_name="未知",
                url="",
                images={},
                tags=[],
                features=ArticleFeatures(),
                local_path="",
                created_at=datetime.now(),
            )

    async def _launch_browser(self) -> None:
        """启动浏览器"""
        try:
            self.logger.info("启动浏览器...")

            playwright = await async_playwright().start()

            # 获取浏览器配置
            headless = self.crawler_config.headless
            browser_type = self.crawler_config.browser_type
            proxy = self.crawler_config.proxy

            # 准备启动参数
            launch_args = {
                "headless": headless,
                "args": [
                    "--no-sandbox",
                    "--disable-setuid-sandbox",
                    "--disable-dev-shm-usage",
                    "--disable-accelerated-2d-canvas",
                    "--no-first-run",
                    "--no-zygote",
                    "--disable-gpu",
                    "--disable-web-security",
                    "--disable-features=VizDisplayCompositor",
                ],
            }

            # 添加代理设置
            if proxy:
                launch_args["proxy"] = {"server": proxy}
                self.logger.info(f"使用代理: {proxy}")

            # 根据浏览器类型启动
            if browser_type == "chromium":
                self.browser = await playwright.chromium.launch(**launch_args)
            elif browser_type == "firefox":
                self.browser = await playwright.firefox.launch(**launch_args)
            elif browser_type == "webkit":
                self.browser = await playwright.webkit.launch(**launch_args)
            else:
                self.logger.warning(f"不支持的浏览器类型: {browser_type}，使用chromium")
                self.browser = await playwright.chromium.launch(**launch_args)

            self.logger.info(f"浏览器启动成功 (类型: {browser_type})")

        except RuntimeError as e:
            self.logger.error(f"浏览器启动失败: {str(e)}")
            raise CrawlerError(f"浏览器启动失败: {str(e)}") from e

    def _clean_image_url(self, url: str) -> str:
        """
        清理图片URL，移除重复参数

        Args:
            url: 原始图片URL

        Returns:
            清理后的URL
        """
        if not url:
            return url

        try:
            # 解析URL
            from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

            parsed = urlparse(url)
            query_params = parse_qs(parsed.query)

            # 移除可能导致重复的参数
            params_to_remove = ["wxfrom", "wx_lazy", "tp"]
            for param in params_to_remove:
                if param in query_params:
                    del query_params[param]

            # 重新构建URL
            clean_query = urlencode(query_params, doseq=True)
            clean_url = urlunparse(
                (parsed.scheme, parsed.netloc, parsed.path, parsed.params, clean_query, parsed.fragment)
            )

            return clean_url

        except (ValueError, RuntimeError, OSError) as e:
            self.logger.debug(f"URL清理失败: {str(e)}")
            return url

    async def _parse_content_with_images(self, html_content: str, text_content: str, image_data: dict[str, str]) -> str:
        """
        解析HTML内容，将图片URL替换为锚点

        Args:
            html_content: HTML内容
            text_content: 纯文本内容
            image_data: 图片数据字典 {img_id: image_url}

        Returns:
            包含图片锚点的文本内容
        """
        try:
            import re

            from bs4 import BeautifulSoup

            if not image_data:
                return text_content

            # 解析HTML
            soup = BeautifulSoup(html_content, "html.parser")

            # 找到所有图片标签
            img_tags = soup.find_all("img")

            if not img_tags:
                return text_content

            self.logger.info(f"找到 {len(img_tags)} 个图片标签")

            # 调试：查看所有图片标签的URL
            for i, img_tag in enumerate(img_tags):
                src = img_tag.get("src")
                data_src = img_tag.get("data-src")
                data_original = img_tag.get("data-original")
                self.logger.debug(f"图片标签 {i+1}: src={src}, data-src={data_src}, data-original={data_original}")

            # 创建URL到锚点ID的映射
            url_to_anchor = {}
            for img_id, url in image_data.items():
                url_to_anchor[url] = img_id

            self.logger.info(f"图片数据中的URL数量: {len(url_to_anchor)}")
            for url in list(url_to_anchor.keys())[:3]:  # 显示前3个URL
                self.logger.debug(f"图片数据URL: {url}")

            # 替换图片标签为锚点
            replaced_count = 0
            for img_tag in img_tags:
                # 获取图片URL - 优先使用data-src（懒加载图片）
                img_url = img_tag.get("data-src") or img_tag.get("data-original") or img_tag.get("src")

                if img_url and img_url.startswith("http"):
                    # 清理URL
                    clean_url = self._clean_image_url(img_url)

                    # 检查是否在图片数据中
                    if clean_url in url_to_anchor:
                        img_id = url_to_anchor[clean_url]
                        anchor_id = img_id.replace("img_", "")

                        # 在HTML中替换图片标签为锚点
                        anchor_tag = soup.new_string(f" $img_{anchor_id}$ ")
                        img_tag.replace_with(anchor_tag)

                        self.logger.info(f"替换图片 {anchor_id}: {clean_url[:50]}...")
                        replaced_count += 1
                    else:
                        self.logger.debug(f"图片不在数据中: {clean_url[:50]}...")
                else:
                    self.logger.debug(f"跳过无效图片URL: {img_url}")

            self.logger.info(f"成功替换 {replaced_count} 个图片标签")

            if replaced_count == 0:
                return text_content

            # 从修改后的HTML中提取文本内容
            content_with_anchors = soup.get_text()

            # 清理多余的空白字符
            content_with_anchors = re.sub(r"\n\s*\n", "\n\n", content_with_anchors)
            content_with_anchors = re.sub(r" +", " ", content_with_anchors)

            return content_with_anchors

        except (ValueError, RuntimeError, OSError) as e:
            self.logger.error(f"解析内容图片失败: {str(e)}")
            return text_content

    async def _extract_images_with_positions(self) -> dict[str, str]:
        """
        提取文章正文中的图片URL和位置信息

        Returns:
            图片数据字典 {img_id: image_url}
        """
        try:
            # 只获取文章正文中的图片
            content_selectors = [
                "#js_content img",  # 微信公众号文章内容中的图片
                ".rich_media_content img",  # 富媒体内容中的图片
            ]
            image_urls = []

            for selector in content_selectors:
                try:
                    images = await self.page.locator(selector).all()
                    for img in images:
                        # 获取src属性
                        src = await img.get_attribute("src")
                        if src and src.startswith("http"):
                            image_urls.append(src)

                        # 获取data-src属性（懒加载图片）
                        data_src = await img.get_attribute("data-src")
                        if data_src and data_src.startswith("http"):
                            image_urls.append(data_src)

                        # 获取data-original属性
                        data_original = await img.get_attribute("data-original")
                        if data_original and data_original.startswith("http"):
                            image_urls.append(data_original)

                    if image_urls:
                        self.logger.info(f"找到 {len(image_urls)} 张图片 (选择器: {selector})")
                        break
                except (RuntimeError, OSError, TimeoutError) as e:
                    self.logger.debug(f"图片选择器 {selector} 失败: {str(e)}")
                    continue

            # 额外处理：等待页面完全加载，再次查找懒加载图片
            try:
                await asyncio.sleep(2)  # 等待懒加载图片加载

                # 再次查找文章内容中的图片
                content_images = await self.page.locator("#js_content img").all()
                for img in content_images:
                    src = await img.get_attribute("src")
                    if src and src.startswith("http") and src not in image_urls:
                        image_urls.append(src)

                self.logger.info(f"懒加载后总图片数量: {len(image_urls)}")

            except (RuntimeError, OSError, TimeoutError) as e:
                self.logger.debug(f"懒加载图片处理失败: {str(e)}")

            # 过滤掉非文章内容的图片
            filtered_images = []
            for url in image_urls:
                # 清理URL
                clean_url = self._clean_image_url(url)
                # 过滤掉头像、广告等非文章内容图片
                if self._is_article_content_image(clean_url):
                    filtered_images.append(clean_url)

            self.logger.info(f"过滤后文章内容图片数量: {len(filtered_images)}")

            # 去重
            unique_image_urls = []
            seen_urls = set()

            for url in filtered_images:
                if url not in seen_urls:
                    seen_urls.add(url)
                    unique_image_urls.append(url)

            self.logger.info(f"去重后图片数量: {len(unique_image_urls)}")

            # 转换为图片数据字典，使用img_前缀
            image_data = {}
            for i, url in enumerate(unique_image_urls, 1):
                img_id = f"img_{i}"
                image_data[img_id] = url

            return image_data

        except (RuntimeError, OSError, TimeoutError, ValueError) as e:
            self.logger.error(f"提取图片位置信息失败: {str(e)}")
            return {}

    def _is_article_content_image(self, url: str) -> bool:
        """
        判断是否为文章内容图片

        Args:
            url: 图片URL

        Returns:
            是否为文章内容图片
        """
        if not url:
            return False

        # 过滤掉头像、广告等非文章内容图片
        exclude_patterns = [
            "avatar",  # 头像
            "logo",  # 标志
            "icon",  # 图标
            "ad",  # 广告
            "banner",  # 横幅
            "shop",  # 商城
            "op_res",  # 运营资源
            "fed_upload",  # 上传资源
        ]

        url_lower = url.lower()
        for pattern in exclude_patterns:
            if pattern in url_lower:
                return False

        # 只保留微信图片和部分其他图片
        include_patterns = [
            "mmbiz.qpic.cn",  # 微信图片
        ]

        return any(pattern in url for pattern in include_patterns)

    async def _cleanup(self) -> None:
        """清理资源"""
        try:
            if self.page:
                await self.page.close()
                self.page = None

            if self.browser:
                await self.browser.close()
                self.browser = None

            self.logger.info("资源清理完成")

        except (RuntimeError, OSError) as e:
            self.logger.error(f"资源清理失败: {str(e)}")

    async def health_check(self) -> dict[str, Any]:
        """健康检查"""
        try:
            return {
                "status": "healthy",
                "browser_running": self.browser is not None,
                "page_active": self.page is not None,
                "timestamp": datetime.now().isoformat(),
            }
        except (RuntimeError, OSError, ValueError) as e:
            return {"status": "unhealthy", "error": str(e), "timestamp": datetime.now().isoformat()}
