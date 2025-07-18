# 微信公众号Agent系统

基于模块化Agent架构的微信公众号文章爬取与个性化内容生成系统。

## 项目概述

本系统采用模块化Agent设计，包含5个核心Agent：
- **CrawlerAgent**: 微信公众号文章爬取
- **StorerAgent**: 数据存储管理
- **AnalyzerAgent**: 文章特征分析和风格提取
- **GeneratorAgent**: 个性化内容生成
- **EmbeddingAgent**: 向量化和语义搜索

## 技术栈

- **Python**: 3.11+
- **依赖管理**: uv
- **网页爬虫**: Playwright
- **数据处理**: pandas, jieba
- **AI/ML**: transformers, torch
- **数据库**: MongoDB, ChromaDB
- **测试**: pytest

## 快速开始

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

## 项目结构

```
wx_agent/
├── agents/                 # Agent模块
│   ├── crawler_agent.py    # 爬虫Agent
│   ├── storer_agent.py     # 存储Agent
│   ├── analyzer_agent.py   # 分析Agent
│   └── generator_agent.py  # 生成Agent
├── core/                   # 核心组件
│   ├── base_agent.py       # Agent基类
│   ├── agent_manager.py    # Agent管理器
│   └── workflow.py         # 工作流引擎
├── models/                 # 数据模型
│   ├── article.py          # 文章模型
│   ├── style_profile.py    # 风格特征模型
│   └── agent_config.py     # Agent配置模型
├── utils/                  # 工具类
│   ├── logger.py           # 日志工具
│   ├── config.py           # 配置工具
│   └── exceptions.py       # 异常处理
├── tests/                  # 测试文件
├── docs/                   # 文档
├── data/                   # 数据存储
├── pyproject.toml          # 项目配置
└── README.md               # 项目说明
```

## 使用示例

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

### 内容生成流程

```python
# 执行内容生成流程
topic = "人工智能的发展趋势"
article = manager.execute_content_generation_workflow(topic)
print(f"生成文章标题: {article.title}")
```

## 开发指南

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

## 部署说明

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

## 贡献指南

1. Fork项目
2. 创建功能分支：`git checkout -b feature/new-feature`
3. 提交更改：`git commit -am 'Add new feature'`
4. 推送分支：`git push origin feature/new-feature`
5. 创建Pull Request

## 许可证

MIT License

## 联系方式

- 作者：linview
- 邮箱：linview@gmail.com 