"""
文章数据模型模块

定义文章相关的数据结构
"""

from datetime import datetime
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field


class ArticleMeta(BaseModel):
    """文章元数据模型"""
    title: str = Field(..., description="文章标题")
    url: str = Field(..., description="文章链接")
    publish_time: Optional[datetime] = Field(None, description="发布时间")
    account_name: str = Field(..., description="公众号名称")
    summary: Optional[str] = Field(None, description="文章摘要")
    cover_image: Optional[str] = Field(None, description="封面图片链接")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


class ArticleFeatures(BaseModel):
    """文章特征模型"""
    keywords: List[str] = Field(default_factory=list, description="关键词列表")
    summary: Optional[str] = Field(None, description="文章摘要")
    sentiment: Optional[str] = Field(None, description="情感分析结果")
    reading_time: Optional[int] = Field(None, description="预计阅读时间（分钟）")
    word_count: Optional[int] = Field(None, description="字数统计")
    paragraph_count: Optional[int] = Field(None, description="段落数量")
    has_images: bool = Field(False, description="是否包含图片")
    has_videos: bool = Field(False, description="是否包含视频")
    topic_category: Optional[str] = Field(None, description="主题分类")
    difficulty_level: Optional[str] = Field(None, description="难度等级")


class Article(BaseModel):
    """文章完整模型"""
    article_id: Optional[str] = Field(None, description="文章唯一标识")
    title: str = Field(..., description="文章标题")
    content: str = Field(..., description="文章正文（包含图片锚点）")
    publish_time: Optional[datetime] = Field(None, description="发布时间")
    account_name: str = Field(..., description="公众号名称")
    url: str = Field(..., description="原文链接")
    images: Dict[str, str] = Field(default_factory=dict, description="图片锚点映射 {img_id: image_url}")
    videos: List[str] = Field(default_factory=list, description="视频链接列表")
    tags: List[str] = Field(default_factory=list, description="标签列表")
    features: ArticleFeatures = Field(default_factory=ArticleFeatures, description="文章特征")
    local_path: Optional[str] = Field(None, description="本地存储路径")
    created_at: datetime = Field(default_factory=datetime.now, description="采集时间")
    updated_at: datetime = Field(default_factory=datetime.now, description="更新时间")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="额外元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict()
    
    def to_json(self) -> str:
        """转换为JSON格式"""
        return self.json()
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Article":
        """从字典创建文章对象"""
        return cls(**data)
    
    def update_features(self, features: ArticleFeatures) -> None:
        """更新文章特征"""
        self.features = features
        self.updated_at = datetime.now()
    
    def add_image(self, img_id: str, image_url: str) -> None:
        """添加图片链接"""
        self.images[img_id] = image_url
        self.features.has_images = True
        self.updated_at = datetime.now()
    
    def add_image_anchor(self, img_id: str, image_url: str, position: int = None) -> None:
        """添加图片锚点到内容中"""
        # 添加图片映射
        self.add_image(img_id, image_url)
        
        # 在内容中插入锚点
        anchor = f" $img_{img_id}$ "
        if position is None:
            # 如果没有指定位置，添加到内容末尾
            self.content += f"\n\n{anchor}\n"
        else:
            # 在指定位置插入锚点
            lines = self.content.split('\n')
            if position < len(lines):
                lines.insert(position, anchor)
                self.content = '\n'.join(lines)
        
        self.updated_at = datetime.now()
    
    def get_image_count(self) -> int:
        """获取图片数量"""
        return len(self.images)
    
    def get_image_urls(self) -> List[str]:
        """获取所有图片URL列表"""
        return list(self.images.values())
    
    def get_image_anchors(self) -> List[str]:
        """获取所有图片锚点"""
        return [f"$img_{img_id.replace('img_', '')}$" for img_id in self.images.keys()]
    
    def replace_image_anchors_with_urls(self) -> str:
        """将内容中的图片锚点替换为实际URL"""
        content = self.content
        for img_id, url in self.images.items():
            anchor = f"$img_{img_id.replace('img_', '')}$"
            content = content.replace(anchor, f"[图片: {url}]")
        return content
    
    def add_video(self, video_url: str) -> None:
        """添加视频链接"""
        if video_url not in self.videos:
            self.videos.append(video_url)
            self.features.has_videos = True
            self.updated_at = datetime.now()
    
    def add_tag(self, tag: str) -> None:
        """添加标签"""
        if tag not in self.tags:
            self.tags.append(tag)
            self.updated_at = datetime.now()
    
    def get_word_count(self) -> int:
        """获取字数统计"""
        return len(self.content)
    
    def get_paragraph_count(self) -> int:
        """获取段落数量"""
        return len([p for p in self.content.split('\n') if p.strip()])
    
    def calculate_reading_time(self) -> int:
        """计算预计阅读时间（分钟）"""
        word_count = self.get_word_count()
        # 假设每分钟阅读300字
        return max(1, word_count // 300)


class ArticleBatch(BaseModel):
    """文章批次模型"""
    batch_id: str = Field(..., description="批次ID")
    articles: List[Article] = Field(default_factory=list, description="文章列表")
    total_count: int = Field(0, description="总数量")
    success_count: int = Field(0, description="成功数量")
    failed_count: int = Field(0, description="失败数量")
    created_at: datetime = Field(default_factory=datetime.now, description="创建时间")
    completed_at: Optional[datetime] = Field(None, description="完成时间")
    status: str = Field("pending", description="批次状态")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_article(self, article: Article) -> None:
        """添加文章到批次"""
        self.articles.append(article)
        self.total_count += 1
    
    def mark_completed(self) -> None:
        """标记批次完成"""
        self.completed_at = datetime.now()
        self.status = "completed"
        self.success_count = len(self.articles)
        self.failed_count = self.total_count - self.success_count
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_count == 0:
            return 0.0
        return self.success_count / self.total_count 