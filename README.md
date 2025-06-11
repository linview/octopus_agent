# RAG Service

一个灵活的RAG（检索增强生成）服务，基于FastAPI构建。

## 特性

- 基于FastAPI的RESTful API
- 可插拔的LLM服务接口
- 支持FAISS和Milvus向量数据库
- 文档自动分块和向量化
- 检索结果评估
- 可自定义的提示模板
- 失败重试机制

## 安装

1. 创建并激活虚拟环境：

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
source .venv/bin/activate  # Linux/macOS
# 或
.venv\Scripts\activate  # Windows
```

2. 同步项目依赖：

```bash
# 同步所有依赖
uv sync

# 如果遇到依赖冲突，可以尝试
uv pip install --upgrade pip
uv sync --upgrade

# 如果缺少某些依赖，可以使用以下命令添加
uv add <package-name>
```

3. 配置环境变量：

创建`.env`文件并设置必要的环境变量：

```env
OPENAI_API_KEY=your_api_key
OPENAI_API_BASE=your_api_base  # 可选
```

## 运行

```bash
python rag_service/run.py
```

服务将在 http://localhost:8000 启动

## API文档

访问 http://localhost:8000/docs 查看完整的API文档

## 主要API端点

- POST `/api/v1/query` - 查询RAG系统
- POST `/api/v1/documents` - 添加文档到RAG系统

## 开发

1. 安装开发依赖：

```bash
# 安装开发依赖
uv sync --dev

# 如果遇到依赖冲突，可以尝试
uv pip install --upgrade pip
uv sync --dev --upgrade
```

2. 代码格式化：

```bash
# 使用black格式化代码
black rag_service/

# 使用isort排序导入
isort rag_service/
```

## 项目结构

```
rag_service/
├── app/
│   ├── api/
│   │   └── endpoints.py
│   ├── core/
│   │   ├── llm/
│   │   ├── vectordb/
│   │   └── rag_service.py
│   ├── config/
│   │   └── settings.py
│   └── main.py
├── pyproject.toml
└── README.md
```

## 依赖管理

本项目使用 `uv` 进行依赖管理，主要命令包括：

- `uv sync`: 同步所有依赖
- `uv add <package>`: 添加新的依赖
- `uv remove <package>`: 移除依赖
- `uv pip freeze`: 导出依赖列表

### 常见问题解决

1. 依赖冲突：
```bash
uv pip install --upgrade pip
uv sync --upgrade
```

2. 开发依赖安装失败：
```bash
uv sync --dev --upgrade
```

3. 特定包安装失败：
```bash
uv add <package-name> --upgrade
```

注意：本项目使用 `pyproject.toml` 进行依赖管理，不再支持 `requirements.txt`。 