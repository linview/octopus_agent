"""
Agent系统配置模型

定义各个Agent的配置参数和验证规则
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field, field_validator


class CrawlerConfig(BaseModel):
    """爬虫Agent配置"""

    max_articles: int = Field(10, description="最大爬取文章数量")
    delay: float = Field(2.0, description="请求间隔时间（秒）")
    user_agent: str = Field(
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36", description="User-Agent"
    )
    timeout: int = Field(30, description="请求超时时间（秒）")
    retry_times: int = Field(3, description="重试次数")
    headless: bool = Field(True, description="是否无头模式")
    browser_type: str = Field("chromium", description="浏览器类型")
    proxy: str | None = Field(None, description="代理设置")
    save_images: bool = Field(True, description="是否保存图片")
    save_videos: bool = Field(True, description="是否保存视频")

    @field_validator("max_articles")
    @classmethod
    def validate_max_articles(cls, v: int) -> int:
        if v <= 0 or v > 100:
            raise ValueError("max_articles must be between 1 and 100")
        return v

    @field_validator("delay")
    @classmethod
    def validate_delay(cls, v: float) -> float:
        if v < 0:
            raise ValueError("delay must be non-negative")
        return v


class StorerConfig(BaseModel):
    """存储Agent配置"""

    storage_type: str = Field("local", description="存储类型")
    data_path: str = Field("./data", description="数据存储路径")
    mongodb_uri: str | None = Field(None, description="MongoDB连接URI")
    mongodb_db: str = Field("wx_agent", description="MongoDB数据库名")
    mongodb_collection: str = Field("articles", description="MongoDB集合名")
    elasticsearch_url: str | None = Field(None, description="Elasticsearch URL")
    elasticsearch_index: str = Field("wx_articles", description="Elasticsearch索引名")
    backup_enabled: bool = Field(True, description="是否启用备份")
    backup_interval: int = Field(24, description="备份间隔（小时）")
    compression_enabled: bool = Field(False, description="是否启用压缩")

    @field_validator("storage_type")
    @classmethod
    def validate_storage_type(cls, v: str) -> str:
        allowed_types = ["local", "mongodb", "elasticsearch", "hybrid"]
        if v not in allowed_types:
            raise ValueError(f"storage_type must be one of {allowed_types}")
        return v


class AnalyzerConfig(BaseModel):
    """分析Agent配置"""

    model_name: str = Field("jieba", description="分词模型名称")
    features: list[str] = Field(
        default_factory=lambda: ["keywords", "summary", "sentiment", "style"], description="分析特征列表"
    )
    sentiment_model: str = Field("snownlp", description="情感分析模型")
    keyword_count: int = Field(10, description="关键词数量")
    summary_length: int = Field(200, description="摘要长度")
    style_confidence_threshold: float = Field(0.7, description="风格置信度阈值")
    parallel_processing: bool = Field(True, description="是否并行处理")
    cache_enabled: bool = Field(True, description="是否启用缓存")
    cache_ttl: int = Field(3600, description="缓存TTL（秒）")

    @field_validator("features")
    @classmethod
    def validate_features(cls, v: list[str]) -> list[str]:
        allowed_features = ["keywords", "summary", "sentiment", "style", "reading_time", "difficulty"]
        for feature in v:
            if feature not in allowed_features:
                raise ValueError(f"Invalid feature: {feature}. Allowed: {allowed_features}")
        return v


class GeneratorConfig(BaseModel):
    """生成Agent配置"""

    llm_model: str = Field("Qwen2-7B-Instruct", description="大语言模型名称")
    max_length: int = Field(1500, description="最大生成长度")
    temperature: float = Field(0.7, description="生成温度")
    top_p: float = Field(0.9, description="Top-p采样")
    top_k: int = Field(50, description="Top-k采样")
    repetition_penalty: float = Field(1.1, description="重复惩罚")
    do_sample: bool = Field(True, description="是否使用采样")
    num_beams: int = Field(1, description="束搜索数量")
    early_stopping: bool = Field(True, description="是否早停")
    style_weight: float = Field(0.8, description="风格权重")
    content_weight: float = Field(0.2, description="内容权重")

    @field_validator("temperature")
    @classmethod
    def validate_temperature(cls, v: float) -> float:
        if v < 0 or v > 2:
            raise ValueError("temperature must be between 0 and 2")
        return v

    @field_validator("max_length")
    @classmethod
    def validate_max_length(cls, v: int) -> int:
        if v <= 0 or v > 5000:
            raise ValueError("max_length must be between 1 and 5000")
        return v


class EmbeddingConfig(BaseModel):
    """向量化Agent配置"""

    model_name: str = Field("sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2", description="嵌入模型名称")
    vector_db_type: str = Field("chromadb", description="向量数据库类型")
    vector_db_path: str = Field("./data/vectors", description="向量数据库路径")
    collection_name: str = Field("wx_articles", description="集合名称")
    chunk_size: int = Field(512, description="文本分块大小")
    chunk_overlap: int = Field(50, description="分块重叠大小")
    batch_size: int = Field(32, description="批处理大小")
    similarity_threshold: float = Field(0.7, description="相似度阈值")
    max_results: int = Field(10, description="最大返回结果数")

    @field_validator("vector_db_type")
    @classmethod
    def validate_vector_db_type(cls, v: str) -> str:
        allowed_types = ["chromadb", "qdrant", "pinecone", "weaviate"]
        if v not in allowed_types:
            raise ValueError(f"vector_db_type must be one of {allowed_types}")
        return v


class DifyConfig(BaseModel):
    """Dify平台集成配置"""

    enabled: bool = Field(False, description="是否启用Dify集成")
    api_url: str = Field("http://localhost:5001", description="Dify API地址")
    api_key: str | None = Field(None, description="Dify API密钥")
    workspace_id: str | None = Field(None, description="工作空间ID")
    app_id: str | None = Field(None, description="应用ID")
    timeout: int = Field(30, description="API超时时间")
    retry_times: int = Field(3, description="重试次数")
    webhook_url: str | None = Field(None, description="Webhook URL")
    webhook_secret: str | None = Field(None, description="Webhook密钥")


class LoggingConfig(BaseModel):
    """日志配置"""

    level: str = Field("INFO", description="日志级别")
    file_path: str = Field("logs/wx_agent.log", description="日志文件路径")
    max_size: str = Field("10 MB", description="日志文件最大大小")
    retention: str = Field("7 days", description="日志保留时间")
    format: str = Field(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | <level>{message}</level>",
        description="日志格式",
    )
    console_output: bool = Field(True, description="是否输出到控制台")
    file_output: bool = Field(True, description="是否输出到文件")

    @field_validator("level")
    @classmethod
    def validate_level(cls, v: str) -> str:
        allowed_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if v.upper() not in allowed_levels:
            raise ValueError(f"level must be one of {allowed_levels}")
        return v.upper()


class AgentConfig(BaseModel):
    """Agent系统总配置"""

    crawler: CrawlerConfig = Field(default_factory=CrawlerConfig, description="爬虫配置")
    storer: StorerConfig = Field(default_factory=StorerConfig, description="存储配置")
    analyzer: AnalyzerConfig = Field(default_factory=AnalyzerConfig, description="分析配置")
    generator: GeneratorConfig = Field(default_factory=GeneratorConfig, description="生成配置")
    embedding: EmbeddingConfig = Field(default_factory=EmbeddingConfig, description="向量化配置")
    dify: DifyConfig = Field(default_factory=DifyConfig, description="Dify配置")
    logging: LoggingConfig = Field(default_factory=LoggingConfig, description="日志配置")

    # 系统级配置
    debug: bool = Field(False, description="调试模式")
    test_mode: bool = Field(False, description="测试模式")
    max_workers: int = Field(4, description="最大工作线程数")
    memory_limit: str = Field("2GB", description="内存限制")
    timeout: int = Field(300, description="全局超时时间（秒）")

    # 元数据
    config_version: str = Field("1.0.0", description="配置版本")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="创建时间")
    updated_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="更新时间")

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return self.model_dump()

    def to_json(self) -> str:
        """转换为JSON格式"""
        return self.model_dump_json()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "AgentConfig":
        """从字典创建配置对象"""
        return cls(**data)

    @classmethod
    def from_file(cls, file_path: str) -> "AgentConfig":
        """从文件加载配置"""
        import json

        with open(file_path, encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)

    def save_to_file(self, file_path: str) -> None:
        """保存配置到文件"""
        import json

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, ensure_ascii=False, indent=2)

    def get_agent_config(
        self, agent_name: str
    ) -> CrawlerConfig | StorerConfig | AnalyzerConfig | GeneratorConfig | EmbeddingConfig:
        """获取指定Agent的配置"""
        config_map = {
            "crawler": self.crawler,
            "storer": self.storer,
            "analyzer": self.analyzer,
            "generator": self.generator,
            "embedding": self.embedding,
        }
        return config_map.get(agent_name)

    def update_config(self, updates: dict[str, Any]) -> None:
        """更新配置"""
        for key, value in updates.items():
            if hasattr(self, key):
                setattr(self, key, value)

    def validate_config(self) -> list[str]:
        """验证配置有效性"""
        errors = []
        try:
            # Pydantic会自动验证所有字段
            self.model_validate(self.model_dump())
        except Exception as e:
            errors.append(str(e))
        return errors
