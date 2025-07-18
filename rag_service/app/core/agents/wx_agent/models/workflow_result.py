"""
工作流结果数据模型模块

定义工作流执行结果相关的数据结构
"""

from datetime import datetime
from typing import Dict, List, Optional, Any, Union
from pydantic import BaseModel, Field

from .article import Article
from .style_profile import StyleProfile


class AgentExecutionResult(BaseModel):
    """Agent执行结果模型"""
    agent_name: str = Field(..., description="Agent名称")
    status: str = Field("pending", description="执行状态")
    start_time: datetime = Field(default_factory=datetime.now, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="执行时长（秒）")
    success: bool = Field(False, description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    input_data: Optional[Dict[str, Any]] = Field(None, description="输入数据")
    output_data: Optional[Any] = Field(None, description="输出数据")
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def mark_completed(self, success: bool, output_data: Any = None, error_message: str = None) -> None:
        """标记执行完成"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.status = "completed" if success else "failed"
        self.output_data = output_data
        self.error_message = error_message
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取执行摘要"""
        return {
            "agent_name": self.agent_name,
            "status": self.status,
            "success": self.success,
            "duration": self.duration,
            "error_message": self.error_message
        }


class WorkflowResult(BaseModel):
    """工作流执行结果模型"""
    workflow_id: str = Field(..., description="工作流ID")
    workflow_name: str = Field(..., description="工作流名称")
    workflow_type: str = Field(..., description="工作流类型")
    status: str = Field("pending", description="工作流状态")
    start_time: datetime = Field(default_factory=datetime.now, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="总执行时长（秒）")
    success: bool = Field(False, description="是否成功")
    error_message: Optional[str] = Field(None, description="错误信息")
    
    # 输入参数
    input_params: Dict[str, Any] = Field(default_factory=dict, description="输入参数")
    
    # 执行结果
    agent_results: List[AgentExecutionResult] = Field(default_factory=list, description="Agent执行结果")
    articles: List[Article] = Field(default_factory=list, description="文章列表")
    style_profile: Optional[StyleProfile] = Field(None, description="风格特征")
    generated_content: Optional[str] = Field(None, description="生成的内容")
    
    # 统计信息
    total_agents: int = Field(0, description="总Agent数量")
    successful_agents: int = Field(0, description="成功Agent数量")
    failed_agents: int = Field(0, description="失败Agent数量")
    articles_count: int = Field(0, description="文章数量")
    
    # 元数据
    metadata: Dict[str, Any] = Field(default_factory=dict, description="元数据")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_agent_result(self, result: AgentExecutionResult) -> None:
        """添加Agent执行结果"""
        self.agent_results.append(result)
        self.total_agents += 1
        
        if result.success:
            self.successful_agents += 1
        else:
            self.failed_agents += 1
    
    def mark_completed(self, success: bool, error_message: str = None) -> None:
        """标记工作流完成"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        self.success = success
        self.status = "completed" if success else "failed"
        self.error_message = error_message
        
        # 更新文章数量
        self.articles_count = len(self.articles)
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_agents == 0:
            return 0.0
        return self.successful_agents / self.total_agents
    
    def get_failed_agents(self) -> List[str]:
        """获取失败的Agent列表"""
        return [result.agent_name for result in self.agent_results if not result.success]
    
    def get_successful_agents(self) -> List[str]:
        """获取成功的Agent列表"""
        return [result.agent_name for result in self.agent_results if result.success]
    
    def get_agent_result(self, agent_name: str) -> Optional[AgentExecutionResult]:
        """获取指定Agent的执行结果"""
        for result in self.agent_results:
            if result.agent_name == agent_name:
                return result
        return None
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return self.dict()
    
    def to_json(self) -> str:
        """转换为JSON格式"""
        return self.json()
    
    def get_summary(self) -> Dict[str, Any]:
        """获取工作流摘要"""
        return {
            "workflow_id": self.workflow_id,
            "workflow_name": self.workflow_name,
            "workflow_type": self.workflow_type,
            "status": self.status,
            "success": self.success,
            "duration": self.duration,
            "success_rate": self.get_success_rate(),
            "total_agents": self.total_agents,
            "successful_agents": self.successful_agents,
            "failed_agents": self.failed_agents,
            "articles_count": self.articles_count,
            "error_message": self.error_message
        }


class DataCollectionResult(WorkflowResult):
    """数据采集工作流结果"""
    workflow_type: str = Field("data_collection", description="工作流类型")
    account_name: str = Field(..., description="公众号名称")
    target_count: int = Field(0, description="目标采集数量")
    actual_count: int = Field(0, description="实际采集数量")
    crawl_success_rate: float = Field(0.0, description="爬取成功率")
    
    def update_crawl_stats(self, target_count: int, actual_count: int) -> None:
        """更新爬取统计"""
        self.target_count = target_count
        self.actual_count = actual_count
        self.articles_count = actual_count
        self.crawl_success_rate = actual_count / target_count if target_count > 0 else 0.0


class ContentGenerationResult(WorkflowResult):
    """内容生成工作流结果"""
    workflow_type: str = Field("content_generation", description="工作流类型")
    topic: str = Field(..., description="生成主题")
    style_profile_id: Optional[str] = Field(None, description="风格特征ID")
    generation_quality_score: Optional[float] = Field(None, description="生成质量评分")
    content_length: Optional[int] = Field(None, description="内容长度")
    generation_time: Optional[float] = Field(None, description="生成耗时")
    
    def update_generation_stats(self, content: str, quality_score: float = None) -> None:
        """更新生成统计"""
        self.generated_content = content
        self.content_length = len(content) if content else 0
        self.generation_quality_score = quality_score


class StyleLearningResult(WorkflowResult):
    """风格学习工作流结果"""
    workflow_type: str = Field("style_learning", description="工作流类型")
    account_name: str = Field(..., description="公众号名称")
    articles_analyzed: int = Field(0, description="分析的文章数量")
    style_confidence: float = Field(0.0, description="风格置信度")
    feature_extraction_time: Optional[float] = Field(None, description="特征提取耗时")
    
    def update_learning_stats(self, articles_count: int, confidence: float) -> None:
        """更新学习统计"""
        self.articles_analyzed = articles_count
        self.style_confidence = confidence
        self.articles_count = articles_count


class WorkflowBatchResult(BaseModel):
    """工作流批次结果模型"""
    batch_id: str = Field(..., description="批次ID")
    batch_name: str = Field(..., description="批次名称")
    workflow_type: str = Field(..., description="工作流类型")
    total_workflows: int = Field(0, description="总工作流数量")
    successful_workflows: int = Field(0, description="成功工作流数量")
    failed_workflows: int = Field(0, description="失败工作流数量")
    start_time: datetime = Field(default_factory=datetime.now, description="开始时间")
    end_time: Optional[datetime] = Field(None, description="结束时间")
    duration: Optional[float] = Field(None, description="总执行时长（秒）")
    workflow_results: List[WorkflowResult] = Field(default_factory=list, description="工作流结果列表")
    summary: Dict[str, Any] = Field(default_factory=dict, description="批次摘要")
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }
    
    def add_workflow_result(self, result: WorkflowResult) -> None:
        """添加工作流结果"""
        self.workflow_results.append(result)
        self.total_workflows += 1
        
        if result.success:
            self.successful_workflows += 1
        else:
            self.failed_workflows += 1
    
    def mark_completed(self) -> None:
        """标记批次完成"""
        self.end_time = datetime.now()
        self.duration = (self.end_time - self.start_time).total_seconds()
        
        # 生成摘要
        self.summary = {
            "batch_id": self.batch_id,
            "batch_name": self.batch_name,
            "workflow_type": self.workflow_type,
            "total_workflows": self.total_workflows,
            "successful_workflows": self.successful_workflows,
            "failed_workflows": self.failed_workflows,
            "success_rate": self.get_success_rate(),
            "duration": self.duration,
            "start_time": self.start_time.isoformat(),
            "end_time": self.end_time.isoformat()
        }
    
    def get_success_rate(self) -> float:
        """获取成功率"""
        if self.total_workflows == 0:
            return 0.0
        return self.successful_workflows / self.total_workflows
    
    def get_summary(self) -> Dict[str, Any]:
        """获取批次摘要"""
        return self.summary 