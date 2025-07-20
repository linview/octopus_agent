"""
数据模型包

包含所有数据模型定义
"""

from .agent_config import (
    AgentConfig,
    AnalyzerConfig,
    CrawlerConfig,
    DifyConfig,
    EmbeddingConfig,
    GeneratorConfig,
    LoggingConfig,
    StorerConfig,
)
from .article import Article, ArticleBatch, ArticleFeatures, ArticleMeta
from .style_profile import (
    EmotionToneFeatures,
    SentenceStructureFeatures,
    StyleProfile,
    VocabularyFeatures,
    WritingHabitsFeatures,
)
from .workflow_result import (
    AgentExecutionResult,
    ContentGenerationResult,
    DataCollectionResult,
    StyleLearningResult,
    WorkflowBatchResult,
    WorkflowResult,
)

__all__ = [
    # 文章相关模型
    "Article",
    "ArticleMeta",
    "ArticleFeatures",
    "ArticleBatch",
    # 风格特征模型
    "StyleProfile",
    "VocabularyFeatures",
    "SentenceStructureFeatures",
    "EmotionToneFeatures",
    "WritingHabitsFeatures",
    # 配置模型
    "AgentConfig",
    "CrawlerConfig",
    "StorerConfig",
    "AnalyzerConfig",
    "GeneratorConfig",
    "EmbeddingConfig",
    "DifyConfig",
    "LoggingConfig",
    # 工作流结果模型
    "WorkflowResult",
    "AgentExecutionResult",
    "DataCollectionResult",
    "ContentGenerationResult",
    "StyleLearningResult",
    "WorkflowBatchResult",
]
