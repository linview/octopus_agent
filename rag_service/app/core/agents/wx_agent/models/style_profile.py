"""
风格特征数据模型模块

定义写作风格相关的数据结构
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class VocabularyFeatures(BaseModel):
    """词汇特征模型"""

    common_words: list[str] = Field(default_factory=list, description="常用词汇")
    unique_words: list[str] = Field(default_factory=list, description="独特词汇")
    vocabulary_richness: float = Field(0.0, description="词汇丰富度")
    avg_word_length: float = Field(0.0, description="平均词长")
    word_frequency: dict[str, int] = Field(default_factory=dict, description="词汇频率")
    technical_terms: list[str] = Field(default_factory=list, description="专业术语")
    emotional_words: list[str] = Field(default_factory=list, description="情感词汇")


class SentenceStructureFeatures(BaseModel):
    """句式结构特征模型"""

    avg_sentence_length: float = Field(0.0, description="平均句长")
    sentence_types: dict[str, int] = Field(default_factory=dict, description="句式类型分布")
    paragraph_length: float = Field(0.0, description="平均段落长度")
    punctuation_usage: dict[str, int] = Field(default_factory=dict, description="标点符号使用")
    transition_words: list[str] = Field(default_factory=list, description="过渡词使用")
    question_frequency: float = Field(0.0, description="问句使用频率")
    exclamation_frequency: float = Field(0.0, description="感叹句使用频率")


class EmotionToneFeatures(BaseModel):
    """情感语调特征模型"""

    overall_sentiment: str = Field("neutral", description="整体情感倾向")
    sentiment_score: float = Field(0.0, description="情感得分")
    tone_formality: str = Field("neutral", description="语调正式程度")
    tone_confidence: float = Field(0.0, description="语调自信度")
    emotion_distribution: dict[str, float] = Field(default_factory=dict, description="情感分布")
    humor_level: float = Field(0.0, description="幽默程度")
    authority_level: float = Field(0.0, description="权威程度")


class WritingHabitsFeatures(BaseModel):
    """写作习惯特征模型"""

    citation_style: str = Field("none", description="引用风格")
    data_usage: float = Field(0.0, description="数据使用频率")
    example_usage: float = Field(0.0, description="举例使用频率")
    metaphor_usage: float = Field(0.0, description="比喻使用频率")
    personal_pronouns: list[str] = Field(default_factory=list, description="人称代词使用")
    opening_patterns: list[str] = Field(default_factory=list, description="开头模式")
    closing_patterns: list[str] = Field(default_factory=list, description="结尾模式")
    call_to_action: bool = Field(False, description="是否包含行动号召")


class StyleProfile(BaseModel):
    """写作风格特征模型"""

    profile_id: str | None = Field(None, description="风格特征ID")
    account_name: str = Field(..., description="公众号名称")
    vocabulary: VocabularyFeatures = Field(default_factory=VocabularyFeatures, description="词汇特征")
    sentence_structure: SentenceStructureFeatures = Field(
        default_factory=SentenceStructureFeatures, description="句式结构"
    )
    emotion_tone: EmotionToneFeatures = Field(default_factory=EmotionToneFeatures, description="情感语调")
    writing_habits: WritingHabitsFeatures = Field(default_factory=WritingHabitsFeatures, description="写作习惯")
    sample_articles: list[str] = Field(default_factory=list, description="示例文章ID列表")
    confidence_score: float = Field(0.0, description="特征置信度")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    metadata: dict[str, Any] = Field(default_factory=dict, description="额外元数据")

    class Config:
        json_encoders = {datetime: lambda v: v.isoformat()}

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return self.dict()

    def to_json(self) -> str:
        """转换为JSON格式"""
        return self.json()

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "StyleProfile":
        """从字典创建风格特征对象"""
        return cls(**data)

    def to_prompt(self) -> str:
        """生成风格描述提示词"""
        prompt_parts = []

        # 词汇特征描述
        if self.vocabulary.common_words:
            prompt_parts.append(f"常用词汇：{', '.join(self.vocabulary.common_words[:10])}")

        if self.vocabulary.technical_terms:
            prompt_parts.append(f"专业术语：{', '.join(self.vocabulary.technical_terms[:5])}")

        # 句式结构描述
        if self.sentence_structure.avg_sentence_length > 0:
            prompt_parts.append(f"平均句长：{self.sentence_structure.avg_sentence_length:.1f}字")

        if self.sentence_structure.transition_words:
            prompt_parts.append(f"常用过渡词：{', '.join(self.sentence_structure.transition_words[:5])}")

        # 情感语调描述
        if self.emotion_tone.overall_sentiment != "neutral":
            prompt_parts.append(f"情感倾向：{self.emotion_tone.overall_sentiment}")

        if self.emotion_tone.tone_formality != "neutral":
            prompt_parts.append(f"语调风格：{self.emotion_tone.tone_formality}")

        # 写作习惯描述
        if self.writing_habits.citation_style != "none":
            prompt_parts.append(f"引用风格：{self.writing_habits.citation_style}")

        if self.writing_habits.call_to_action:
            prompt_parts.append("经常使用行动号召")

        if self.writing_habits.opening_patterns:
            prompt_parts.append(f"开头模式：{', '.join(self.writing_habits.opening_patterns[:3])}")

        # 组合成完整提示词
        if prompt_parts:
            return "写作风格特征：\n" + "\n".join(f"- {part}" for part in prompt_parts)
        else:
            return "写作风格特征：暂无具体特征"

    def update_confidence(self, new_score: float) -> None:
        """更新置信度"""
        self.confidence_score = new_score
        self.updated_at = datetime.now()

    def add_sample_article(self, article_id: str) -> None:
        """添加示例文章"""
        if article_id not in self.sample_articles:
            self.sample_articles.append(article_id)
            self.updated_at = datetime.now()

    def get_feature_summary(self) -> dict[str, Any]:
        """获取特征摘要"""
        return {
            "profile_id": self.profile_id,
            "account_name": self.account_name,
            "vocabulary_richness": self.vocabulary.vocabulary_richness,
            "avg_sentence_length": self.sentence_structure.avg_sentence_length,
            "overall_sentiment": self.emotion_tone.overall_sentiment,
            "confidence_score": self.confidence_score,
            "sample_count": len(self.sample_articles),
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
        }

    def merge_with(self, other: "StyleProfile") -> "StyleProfile":
        """与另一个风格特征合并"""
        # 创建新的风格特征对象
        merged = StyleProfile(
            account_name=self.account_name, confidence_score=(self.confidence_score + other.confidence_score) / 2
        )

        # 合并词汇特征
        merged.vocabulary.common_words = list(set(self.vocabulary.common_words + other.vocabulary.common_words))
        merged.vocabulary.technical_terms = list(
            set(self.vocabulary.technical_terms + other.vocabulary.technical_terms)
        )
        merged.vocabulary.vocabulary_richness = (
            self.vocabulary.vocabulary_richness + other.vocabulary.vocabulary_richness
        ) / 2

        # 合并句式结构特征
        merged.sentence_structure.avg_sentence_length = (
            self.sentence_structure.avg_sentence_length + other.sentence_structure.avg_sentence_length
        ) / 2
        merged.sentence_structure.transition_words = list(
            set(self.sentence_structure.transition_words + other.sentence_structure.transition_words)
        )

        # 合并情感语调特征
        merged.emotion_tone.overall_sentiment = self.emotion_tone.overall_sentiment  # 保持原样
        merged.emotion_tone.sentiment_score = (
            self.emotion_tone.sentiment_score + other.emotion_tone.sentiment_score
        ) / 2

        # 合并写作习惯特征
        merged.writing_habits.call_to_action = self.writing_habits.call_to_action or other.writing_habits.call_to_action
        merged.writing_habits.opening_patterns = list(
            set(self.writing_habits.opening_patterns + other.writing_habits.opening_patterns)
        )

        # 合并示例文章
        merged.sample_articles = list(set(self.sample_articles + other.sample_articles))

        return merged
