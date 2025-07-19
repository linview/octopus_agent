# 微信公众号Agent系统

基于模块化Agent架构的微信公众号文章爬取与个性化内容生成系统。

## 🎯 项目概述

本系统采用模块化Agent设计，实现微信公众号文章的智能爬取、分析和个性化内容生成。**最新版本v8**实现了重大技术突破，包括图片锚点功能和懒加载图片处理。

### 核心Agent模块
- **CrawlerAgent**: 微信公众号文章爬取（包含图片锚点功能）
- **StorerAgent**: 数据存储管理
- **AnalyzerAgent**: 文章特征分析和风格提取
- **GeneratorAgent**: 个性化内容生成
- **EmbeddingAgent**: 向量化和语义搜索

### 🚀 技术突破（v8 - 2025-07-19）

**图片锚点功能**：
- ✅ 图片语义位置保持：在文章内容中插入图片锚点，保持图片在原文中的位置
- ✅ 懒加载图片处理：支持微信公众号的懒加载机制，优先使用`data-src`属性
- ✅ 图片过滤机制：只保留文章内容图片，过滤广告、头像等非内容图片
- ✅ 数据一致性验证：确保锚点与图片数据一一对应

**数据结构示例**：
```json
{
    "content": " $img_1$ 都2025年了，作为程序员如果你还没试过Vibe Coding那就out啦... $img_2$ 2023年copilot算是当时最流行的编程助手...",
    "images": {
        "img_1": "https://mmbiz.qpic.cn/mmbiz_png/...",
        "img_2": "https://mmbiz.qpic.cn/mmbiz_jpg/...",
        "img_3": "https://mmbiz.qpic.cn/mmbiz_png/..."
    }
}
```

## 🛠️ 技术栈

- **Python**: 3.11+
- **依赖管理**: uv
- **网页爬虫**: Playwright (支持懒加载图片)
- **HTML解析**: BeautifulSoup4
- **数据处理**: pandas, jieba
- **AI/ML**: transformers, torch
- **数据库**: MongoDB, ChromaDB
- **测试**: pytest, pytest-asyncio
- **代码质量**: black, isort, mypy

## 🚀 快速开始

### 环境准备

1. 安装uv（如果未安装）：
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. 克隆项目并进入目录：
```bash
cd rag_service/app/core/agents/wx_agent
```

3. 初始化项目环境：
```bash
uv sync
```

4. 安装Playwright浏览器：
```bash
uv run playwright install chromium
```

### 配置环境

1. 复制配置文件模板：
```bash
cp .env.template .env
```

2. 编辑`.env`文件，填入实际配置：
```bash
# 编辑配置文件
vim .env
```

### 运行测试

```bash
# 运行所有测试
uv run pytest

# 运行图片锚点功能测试
uv run pytest tests/test_image_anchors.py -v -s

# 运行特定测试
uv run pytest tests/test_crawler_agent.py

# 生成覆盖率报告
uv run pytest --cov=agents --cov-report=html
```

### 代码格式化

```bash
# 格式化代码
uv run black .
uv run isort .

# 类型检查
uv run mypy .
```

## 📁 项目结构

```
wx_agent/
├── agents/                 # Agent模块
│   ├── crawler_agent.py    # 爬虫Agent（包含图片锚点功能）
│   ├── storer_agent.py     # 存储Agent
│   ├── analyzer_agent.py   # 分析Agent
│   └── generator_agent.py  # 生成Agent
├── core/                   # 核心组件
│   ├── base_agent.py       # Agent基类
│   ├── agent_manager.py    # Agent管理器
│   └── workflow.py         # 工作流引擎
├── models/                 # 数据模型
│   ├── article.py          # 文章模型（支持图片锚点）
│   ├── style_profile.py    # 风格特征模型
│   └── agent_config.py     # Agent配置模型
├── utils/                  # 工具类
│   ├── logger.py           # 日志工具
│   ├── config.py           # 配置工具
│   └── exceptions.py       # 异常处理
├── tests/                  # 测试文件
│   ├── test_image_anchors.py  # 图片锚点功能测试
│   ├── test_crawler_agent.py  # 爬虫功能测试
│   ├── test_base_agent.py     # 基础Agent测试
│   └── ...                    # 其他测试文件
├── docs/                   # 文档
├── data/                   # 数据存储（.gitkeep保持目录结构）
├── prompts/                # 提示词模板
├── pyproject.toml          # 项目配置
└── README.md               # 项目说明
```

## 💡 使用示例

### 数据采集流程

```python
from core.agent_manager import AgentManager
from utils.config import load_config

# 加载配置
config = load_config()

# 创建Agent管理器
manager = AgentManager(config)

# 执行数据采集流程
result = manager.execute_data_collection_workflow("test_account")
print(f"采集到 {result['articles_count']} 篇文章")
```

### 图片锚点功能演示

```python
from agents.crawler_agent import CrawlerAgent

# 创建爬虫Agent
crawler = CrawlerAgent(config)

# 爬取文章（自动处理图片锚点）
articles = await crawler.execute({
    'article_urls': ['https://mp.weixin.qq.com/s/example'],
    'max_count': 1
})

article = articles[0]
print(f"文章标题: {article.title}")
print(f"图片数量: {article.get_image_count()}")
print(f"内容预览: {article.content[:200]}...")

# 验证图片锚点
anchors = article.get_image_anchors()
print(f"锚点列表: {anchors}")

# 替换锚点为URL
replaced_content = article.replace_image_anchors_with_urls()
print(f"替换后内容: {replaced_content[:200]}...")
```

### 内容生成流程

```python
# 执行内容生成流程
topic = "人工智能的发展趋势"
article = manager.execute_content_generation_workflow(topic)
print(f"生成文章标题: {article.title}")
```

## 🔧 开发指南

### 添加新的Agent

1. 继承BaseAgent基类：
```python
from core.base_agent import BaseAgent

class NewAgent(BaseAgent):
    def _process(self, input_data: Dict) -> Any:
        # 实现具体逻辑
        pass
```

2. 在AgentManager中注册：
```python
self.agents['new_agent'] = NewAgent(config)
```

### 添加新的工作流

1. 在workflow.py中定义新工作流：
```python
def new_workflow(self, params: Dict) -> Dict:
    # 实现工作流逻辑
    pass
```

2. 在AgentManager中调用：
```python
result = self.new_workflow(params)
```

### 图片锚点功能扩展

```python
# 自定义图片锚点格式
class CustomCrawlerAgent(CrawlerAgent):
    def _parse_content_with_images(self, html_content: str, text_content: str, image_data: Dict[str, str]) -> str:
        # 自定义锚点处理逻辑
        # 例如：使用不同的锚点格式
        pass
```

## 📊 测试验证

### 图片锚点功能测试

```bash
# 运行图片锚点功能测试
uv run pytest tests/test_image_anchors.py -v -s
```

**测试结果示例**：
```
✅ 爬取完成！
📄 标题: 编程助手怎么选？左手lingma，右手cursor
👤 作者: 琳时闲话
🖼️ 图片数量: 7
📝 内容长度: 3211 字符

📊 图片映射数量: 7
📊 内容中的锚点数量: 7
🔗 锚点与图片对应关系:
  ✅ $img_1$ -> https://mmbiz.qpic.cn/mmbiz_png/...
  ✅ $img_2$ -> https://mmbiz.qpic.cn/mmbiz_jpg/...
  ...
```

### 测试覆盖率

```bash
# 生成测试覆盖率报告
uv run pytest --cov=agents --cov-report=html
```

## 🚀 部署说明

### 本地部署

1. 安装依赖：
```bash
uv sync
```

2. 配置环境变量：
```bash
cp .env.template .env
# 编辑 .env 文件
```

3. 启动服务：
```bash
uv run python main.py
```

### Docker部署

```bash
# 构建镜像
docker build -t wx-agent .

# 运行容器
docker run -d --name wx-agent -p 8000:8000 wx-agent
```

## 📈 版本历史

- **v8 (2025-07-19)**: 🎯 重大技术突破 - 实现图片锚点功能，增强图文语义关联性
- **v7 (2025-07-19)**: ⚠️ 重要更新 - 发现微信公众号主页反爬虫限制，调整爬取策略
- **v6**: 基于模块化Agent架构重新设计，适配Dify等低代码平台
- **v5**: 简化技术细节，突出关键流程和架构设计
- **v4**: 修正微信公众号API限制，调研网页爬虫方案
- **v3**: 优化语言风格训练方案，将Prompt Engineering作为MVP优先方案
- **v2**: 基于用户反馈优化，重点突出MVP方案
- **v1**: 初始设计版本，包含完整技术方案

## 🤝 贡献指南

1. Fork项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建Pull Request

### 开发规范

- 遵循PEP 8代码风格
- 添加适当的类型注解
- 编写单元测试
- 更新相关文档

## 📄 许可证

MIT License

## 📞 联系方式

- 作者：linview
- 邮箱：linview@gmail.com
- 项目地址：https://github.com/your-username/wx-agent

## 🙏 致谢

感谢以下开源项目的支持：
- [Playwright](https://playwright.dev/) - 现代浏览器自动化
- [BeautifulSoup](https://www.crummy.com/software/BeautifulSoup/) - HTML解析
- [pytest](https://docs.pytest.org/) - Python测试框架
- [uv](https://github.com/astral-sh/uv) - 快速Python包管理器 