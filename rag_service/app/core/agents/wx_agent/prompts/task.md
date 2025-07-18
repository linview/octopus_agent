# 微信公众号Agent系统 - 任务清单

## Sprint#1: MVP阶段 - 模块化Agent架构实现
**时间**: 2025-07-18 至 2025-07-25 (1周)
**目标**: 验证模块化Agent架构可行性，实现4个核心Agent基础功能

### 任务列表
- **task#1**: Agent基类与项目架构搭建
- **task#2**: CrawlerAgent开发（爬虫Agent）
- **task#3**: StorerAgent开发（存储Agent）
- **task#4**: AnalyzerAgent开发（分析Agent）
- **task#5**: GeneratorAgent开发（生成Agent）
- **task#6**: Agent协作流程集成
- **task#7**: MVP链路验证与测试

---

## task#1: Agent基类与项目架构搭建
**目标**: 建立模块化Agent架构基础，创建统一的Agent接口

**关键流程**:
```python
# 伪代码：项目架构初始化
def init_agent_architecture():
    # 1. 创建项目目录结构
    create_directories([
        'agents/',           # Agent模块目录
        'core/',             # 核心组件
        'models/',           # 数据模型
        'utils/',            # 工具类
        'config/',           # 配置文件
        'data/',             # 数据存储
        'tests/',            # 测试文件
        'dify_integration/'  # Dify集成
    ])
    
    # 2. 创建Agent基类
    create_base_agent_class({
        'execute': '统一执行接口',
        '_process': '子类实现具体逻辑',
        'get_status': '获取Agent状态',
        'setup_logger': '日志配置'
    })
    
    # 3. 配置文件模板
    create_config_template({
        'agents': {
            'crawler': {'max_articles': 10, 'delay': 2},
            'storer': {'storage_type': 'local', 'data_path': './data'},
            'analyzer': {'model_name': 'jieba', 'features': ['keywords', 'summary']},
            'generator': {'llm_model': 'Qwen2-7B-Instruct', 'max_length': 1500}
        },
        'dify': {
            'enabled': False,
            'api_url': 'http://localhost:5001',
            'api_key': 'your_api_key'
        }
    })
    
    # 4. 数据模型定义
    create_data_models([
        'Article',           # 文章模型
        'StyleProfile',      # 风格特征模型
        'AgentConfig',       # Agent配置模型
        'WorkflowResult'     # 工作流结果模型
    ])
```

**环境配置管理**:
```bash
# 使用uv进行依赖管理
# 1. 初始化项目
uv init wx_agent

# 2. 添加核心依赖
uv add playwright beautifulsoup4 requests jieba pandas transformers torch

# 3. 添加开发依赖
uv add --dev pytest pytest-asyncio black isort mypy

# 4. 安装依赖
uv sync
```

**pyproject.toml配置**:
```toml
[project]
name = "wx-agent"
version = "0.1.0"
description = "微信公众号文章爬取与个性化Agent系统"
authors = [
    {name = "linview", email = "linview@gmail.com"},
]
dependencies = [
    "playwright>=1.40.0",
    "beautifulsoup4>=4.12.2",
    "requests>=2.31.0",
    "jieba>=0.42.1",
    "pandas>=2.1.3",
    "transformers>=4.35.0",
    "torch>=2.1.0",
    "python-dotenv>=1.0.0",
    "loguru>=0.7.2",
    "aiohttp>=3.9.1",
    "pydantic>=2.6.3",
    "pydantic-settings>=2.2.1",
]
requires-python = ">=3.11, <4.0"

[project.optional-dependencies]
dev = [
    "pytest>=8.4.0",
    "pytest-asyncio>=0.23.0",
    "black>=23.7.0",
    "isort>=5.12.0",
    "mypy>=1.5.1"
]

[tool.black]
line-length = 120
target-version = ['py39']
include = '\.pyi?$'

[tool.isort]
profile = "black"
multi_line_output = 3

[tool.mypy]
python_version = "3.11"
warn_return_any = true
warn_unused_configs = true
disallow_untyped_defs = true

[tool.pytest.ini_options]
testpaths = ["tests"]
python_files = ["test_*.py"]
python_classes = ["Test*"]
python_functions = ["test_*"]
addopts = "-v --tb=short"
```

**交付物**:
- [x] 完整的项目目录结构
- [x] BaseAgent基类 (core/base_agent.py)
- [x] 数据模型定义 (models/)
- [x] 配置文件模板 (.env.template)
- [x] pyproject.toml 项目配置
- [x] README.md 项目说明

---

## task#2: CrawlerAgent开发（爬虫Agent）
**目标**: 实现微信公众号文章爬取功能

**关键流程**:
```python
# 伪代码：CrawlerAgent核心实现
class CrawlerAgent(BaseAgent):
    def _process(self, input_data: Dict) -> List[Article]:
        # 1. 解析输入参数
        account_name = input_data.get('account_name')
        max_count = input_data.get('max_count', 10)
        
        # 2. 启动浏览器
        browser = await self.launch_browser()
        
        # 3. 访问公众号主页
        await self.visit_account_page(account_name)
        
        # 4. 获取文章列表
        article_list = await self.get_article_list(max_count)
        
        # 5. 获取文章详情
        articles = await self.get_article_details(article_list)
        
        # 6. 下载媒体文件
        await self.download_media(articles)
        
        return articles
    
    async def get_article_list(self, max_count: int) -> List[ArticleMeta]:
        # 滚动加载更多文章
        # 解析文章链接和标题
        # 返回文章基本信息列表
    
    async def get_article_details(self, article_list: List[ArticleMeta]) -> List[Article]:
        # 并发访问文章页面
        # 提取文章正文、发布时间
        # 提取图片链接
```

**技术要点**:
- 继承BaseAgent基类
- 使用Playwright处理动态页面
- 实现反爬虫策略（随机延迟、User-Agent）
- 支持分页获取历史文章
- 异步并发处理提高效率

**依赖管理**:
```bash
# 添加Playwright相关依赖
uv add playwright
uv run playwright install chromium
```

**交付物**:
- [ ] CrawlerAgent核心类 (agents/crawler_agent.py)
- [ ] 页面解析器 (agents/crawler/page_parser.py)
- [ ] 媒体下载器 (agents/crawler/media_downloader.py)
- [ ] 爬虫配置文件 (agents/crawler/config.py)
- [ ] 单元测试 (tests/test_crawler_agent.py)

---

## task#3: StorerAgent开发（存储Agent）
**目标**: 实现数据存储管理功能，支持多种存储后端

**关键流程**:
```python
# 伪代码：StorerAgent核心实现
class StorerAgent(BaseAgent):
    def _process(self, input_data: Dict) -> bool:
        # 1. 解析输入参数
        articles = input_data.get('articles', [])
        storage_type = input_data.get('storage_type', 'local')
        
        # 2. 根据存储类型选择后端
        if storage_type == 'local':
            return self.save_to_local(articles)
        elif storage_type == 'mongodb':
            return self.save_to_mongodb(articles)
        else:
            raise ValueError(f"Unsupported storage type: {storage_type}")
    
    def save_to_local(self, articles: List[Article]) -> bool:
        # 1. 生成文章ID
        for article in articles:
            article.article_id = self.generate_article_id(article)
        
        # 2. 保存文章JSON
        for article in articles:
            self.save_json(article, f"data/articles/{article.article_id}.json")
        
        # 3. 下载并保存图片
        for article in articles:
            self.save_images(article.images, f"data/images/{article.article_id}/")
        
        # 4. 更新文章索引
        self.update_article_index(articles)
        
        return True
    
    def load_articles(self, filters: Dict = None) -> List[Article]:
        # 从存储加载文章
        # 支持过滤条件
        # 返回文章列表
```

**存储结构**:
```
data/
├── articles/
│   ├── article_001.json
│   ├── article_002.json
│   └── ...
├── images/
│   ├── article_001/
│   ├── article_002/
│   └── ...
└── index.json
```

**依赖管理**:
```bash
# 添加存储相关依赖
uv add pymongo chromadb
```

**交付物**:
- [ ] StorerAgent核心类 (agents/storer_agent.py)
- [ ] 本地存储管理器 (agents/storer/local_storage.py)
- [ ] 数据索引管理器 (agents/storer/index_manager.py)
- [ ] 存储接口抽象 (agents/storer/storage_interface.py)
- [ ] 单元测试 (tests/test_storer_agent.py)

---

## task#4: AnalyzerAgent开发（分析Agent）
**目标**: 实现文章特征分析和风格提取功能

**关键流程**:
```python
# 伪代码：AnalyzerAgent核心实现
class AnalyzerAgent(BaseAgent):
    def _process(self, input_data: Dict) -> StyleProfile:
        # 1. 解析输入参数
        articles = input_data.get('articles', [])
        analysis_type = input_data.get('analysis_type', 'style')
        
        # 2. 根据分析类型执行不同功能
        if analysis_type == 'style':
            return self.analyze_writing_style(articles)
        elif analysis_type == 'features':
            return self.extract_features(articles)
        else:
            raise ValueError(f"Unsupported analysis type: {analysis_type}")
    
    def analyze_writing_style(self, articles: List[Article]) -> StyleProfile:
        # 1. 分析词汇特征
        vocabulary = self.analyze_vocabulary(articles)
        
        # 2. 分析句式结构
        sentence_structure = self.analyze_sentence_structure(articles)
        
        # 3. 分析情感倾向
        emotion_tone = self.analyze_emotion_tone(articles)
        
        # 4. 分析写作习惯
        writing_habits = self.analyze_writing_habits(articles)
        
        return StyleProfile(
            vocabulary=vocabulary,
            sentence_structure=sentence_structure,
            emotion_tone=emotion_tone,
            writing_habits=writing_habits
        )
    
    def generate_style_prompt(self, style_profile: StyleProfile) -> str:
        # 根据风格特征生成提示词
        description = "你是一个专业的公众号作者，具有以下写作风格特征：\n"
        # 根据特征生成描述...
        return description
```

**分析维度**:
- **词汇特征**: 常用词汇、词汇丰富度
- **句式结构**: 句子长度、句式类型
- **情感倾向**: 情感分析、语调特征
- **写作习惯**: 引用使用、数据引用、问句使用

**依赖管理**:
```bash
# 添加分析相关依赖
uv add jieba snownlp textblob
```

**交付物**:
- [ ] AnalyzerAgent核心类 (agents/analyzer_agent.py)
- [ ] 风格分析器 (agents/analyzer/style_analyzer.py)
- [ ] 特征提取器 (agents/analyzer/feature_extractor.py)
- [ ] 提示词生成器 (agents/analyzer/prompt_generator.py)
- [ ] 单元测试 (tests/test_analyzer_agent.py)

---

## task#5: GeneratorAgent开发（生成Agent）
**目标**: 实现个性化内容生成功能

**关键流程**:
```python
# 伪代码：GeneratorAgent核心实现
class GeneratorAgent(BaseAgent):
    def _process(self, input_data: Dict) -> Article:
        # 1. 解析输入参数
        topic = input_data.get('topic')
        style_profile = input_data.get('style_profile')
        generation_type = input_data.get('generation_type', 'article')
        
        # 2. 根据生成类型执行不同功能
        if generation_type == 'article':
            return self.generate_article(topic, style_profile)
        elif generation_type == 'outline':
            return self.generate_outline(topic)
        else:
            raise ValueError(f"Unsupported generation type: {generation_type}")
    
    def generate_article(self, topic: str, style_profile: StyleProfile) -> Article:
        # 1. 构建个性化提示词
        prompt = self.build_article_prompt(topic, style_profile)
        
        # 2. 调用LLM生成内容
        content = self.llm.generate(prompt)
        
        # 3. 后处理优化
        optimized_content = self.post_process(content)
        
        # 4. 构建文章对象
        return Article(
            title=self.extract_title(optimized_content),
            content=optimized_content,
            topic=topic,
            generated_at=datetime.now()
        )
    
    def build_article_prompt(self, topic: str, style_profile: StyleProfile) -> str:
        # 1. 获取风格描述
        style_description = style_profile.to_prompt()
        
        # 2. 选择示例文章
        examples = self.select_examples(topic, style_profile)
        
        # 3. 构建完整提示词
        prompt = f"""
        {style_description}
        
        请参考以下示例文章的风格：
        {self.format_examples(examples)}
        
        请以上述风格，生成一篇关于"{topic}"的公众号文章。
        要求：
        1. 标题要吸引人，符合公众号风格
        2. 内容要有深度，观点明确
        3. 语言要符合我的写作习惯
        4. 结构要清晰，段落合理
        5. 字数控制在1000-1500字左右
        """
        return prompt
```

**生成策略**:
- **Few-shot Learning**: 基于示例文章生成
- **Prompt Engineering**: 动态构建提示词
- **风格匹配**: 根据风格特征调整生成策略

**依赖管理**:
```bash
# 添加生成相关依赖
uv add transformers torch accelerate
```

**交付物**:
- [ ] GeneratorAgent核心类 (agents/generator_agent.py)
- [ ] 提示词构建器 (agents/generator/prompt_builder.py)
- [ ] LLM接口封装 (agents/generator/llm_client.py)
- [ ] 内容后处理器 (agents/generator/post_processor.py)
- [ ] 单元测试 (tests/test_generator_agent.py)

---

## task#6: Agent协作流程集成
**目标**: 实现Agent间的协作机制，完成端到端工作流

**关键流程**:
```python
# 伪代码：Agent协作流程
class AgentManager:
    def __init__(self, config: Dict):
        self.config = config
        self.agents = {
            'crawler': CrawlerAgent(config),
            'storer': StorerAgent(config),
            'analyzer': AnalyzerAgent(config),
            'generator': GeneratorAgent(config)
        }
    
    def execute_data_collection_workflow(self, account_name: str) -> Dict:
        # 1. CrawlerAgent爬取文章
        crawler_result = self.agents['crawler'].execute({
            'account_name': account_name,
            'max_count': 10
        })
        
        # 2. StorerAgent保存文章
        storer_result = self.agents['storer'].execute({
            'articles': crawler_result,
            'storage_type': 'local'
        })
        
        # 3. AnalyzerAgent分析特征
        analyzer_result = self.agents['analyzer'].execute({
            'articles': crawler_result,
            'analysis_type': 'style'
        })
        
        return {
            'articles_count': len(crawler_result),
            'style_profile': analyzer_result,
            'status': 'completed'
        }
    
    def execute_content_generation_workflow(self, topic: str) -> Article:
        # 1. 加载风格特征
        style_profile = self.load_style_profile()
        
        # 2. GeneratorAgent生成文章
        generator_result = self.agents['generator'].execute({
            'topic': topic,
            'style_profile': style_profile,
            'generation_type': 'article'
        })
        
        # 3. StorerAgent保存生成的文章
        self.agents['storer'].execute({
            'articles': [generator_result],
            'storage_type': 'local'
        })
        
        return generator_result
```

**工作流类型**:
- **数据采集流程**: Crawler → Storer → Analyzer
- **内容生成流程**: Generator → Storer
- **风格学习流程**: Analyzer → 风格模板更新

**依赖管理**:
```bash
# 添加工作流相关依赖
uv add asyncio aiofiles
```

**交付物**:
- [ ] Agent管理器 (core/agent_manager.py)
- [ ] 工作流引擎 (core/workflow.py)
- [ ] 协作流程定义 (core/workflows/)
- [ ] 集成测试 (tests/test_agent_integration.py)

---

## task#7: MVP链路验证与测试
**目标**: 验证完整功能链路，输出MVP总结

**关键流程**:
```python
# 伪代码：MVP验证流程
def mvp_validation_workflow():
    # 1. 端到端测试
    test_full_pipeline()
    
    # 2. 各Agent功能验证
    test_crawler_agent()
    test_storer_agent()
    test_analyzer_agent()
    test_generator_agent()
    
    # 3. Agent协作验证
    test_agent_collaboration()
    
    # 4. 性能测试
    test_performance()
    
    # 5. 错误处理测试
    test_error_scenarios()
    
    # 6. 输出测试报告
    generate_mvp_report()

def test_full_pipeline():
    # 1. 数据采集流程测试
    account_name = "test_account"
    result = agent_manager.execute_data_collection_workflow(account_name)
    assert result['status'] == 'completed'
    assert result['articles_count'] > 0
    
    # 2. 内容生成流程测试
    topic = "测试主题"
    article = agent_manager.execute_content_generation_workflow(topic)
    assert article.title is not None
    assert len(article.content) > 500
    
    # 3. 验证生成质量
    validate_generated_content(article)
```

**测试场景**:
- 正常爬取流程测试
- 网络异常处理测试
- 内容解析准确性测试
- 文章生成质量测试
- Agent协作效率测试
- 性能压力测试

**测试运行**:
```bash
# 运行所有测试
uv run pytest

# 运行特定测试
uv run pytest tests/test_crawler_agent.py

# 运行集成测试
uv run pytest tests/test_agent_integration.py

# 生成覆盖率报告
uv run pytest --cov=agents --cov-report=html
```

**交付物**:
- [ ] 集成测试脚本 (tests/integration_test.py)
- [ ] 功能测试用例 (tests/functional_tests.py)
- [ ] 性能测试报告 (tests/performance_report.md)
- [ ] MVP阶段总结文档 (docs/mvp_summary.md)
- [ ] 部署指南 (docs/deployment_guide.md)

---

## 后续阶段规划

### Sprint#2: POC阶段 (2-3周)
- **EmbeddingAgent**: 向量化功能开发
- **StorerAgent**: MongoDB集成
- **AnalyzerAgent**: 高级风格分析
- **GeneratorAgent**: RAG增强生成
- **Dify平台集成**: 工具函数和工作流集成

### Sprint#3: 生产阶段 (2-3周)  
- **性能优化**: Agent间通信优化
- **监控告警**: 各Agent状态监控
- **错误处理**: 完善异常处理机制
- **部署配置**: 生产环境部署
- **文档完善**: 用户手册和API文档

**总工期**: 5-7周

## 技术架构总结

### 目录结构
```
wx_agent/
├── agents/
│   ├── crawler_agent.py
│   ├── storer_agent.py
│   ├── analyzer_agent.py
│   └── generator_agent.py
├── core/
│   ├── base_agent.py      # Agent基类
│   ├── agent_manager.py   # Agent管理器
│   └── workflow.py        # 工作流引擎
├── models/
│   ├── article.py
│   ├── style_profile.py
│   └── agent_config.py
├── utils/
│   ├── logger.py
│   ├── config.py
│   └── exceptions.py
├── tests/
│   ├── test_crawler_agent.py
│   ├── test_storer_agent.py
│   ├── test_analyzer_agent.py
│   ├── test_generator_agent.py
│   └── test_agent_integration.py
├── docs/
│   ├── mvp_summary.md
│   └── deployment_guide.md
├── pyproject.toml         # 项目配置
├── uv.lock               # 依赖锁定文件
└── README.md             # 项目说明
```

### 环境管理
```bash
# 项目初始化
uv init wx_agent

# 安装依赖
uv sync

# 运行开发环境
uv run python main.py

# 运行测试
uv run pytest

# 代码格式化
uv run black .
uv run isort .

# 类型检查
uv run mypy .
```

### 关键成功因素
1. **模块化设计**: 每个Agent职责单一，便于开发和测试
2. **标准化接口**: 统一的Agent接口，便于协作
3. **渐进式实现**: MVP优先，逐步完善功能
4. **平台兼容**: 为Dify等低代码平台集成做准备
5. **质量保证**: 完善的测试覆盖和错误处理
6. **现代化工具链**: 使用uv进行依赖管理，提高开发效率
