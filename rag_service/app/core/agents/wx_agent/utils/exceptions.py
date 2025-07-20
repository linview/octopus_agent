"""
异常处理工具模块

定义系统自定义异常和异常处理工具
"""

from typing import Any


class WxAgentError(Exception):
    """微信公众号Agent系统基础异常类"""

    def __init__(self, message: str, error_code: str | None = None, details: dict[str, Any] | None = None):
        """
        初始化异常

        Args:
            message: 错误消息
            error_code: 错误代码
            details: 错误详情
        """
        super().__init__(message)
        self.message = message
        self.error_code = error_code
        self.details = details or {}

    def to_dict(self) -> dict[str, Any]:
        """转换为字典格式"""
        return {
            "error_type": self.__class__.__name__,
            "message": self.message,
            "error_code": self.error_code,
            "details": self.details,
        }


class AgentError(WxAgentError):
    """Agent相关异常"""

    pass


class CrawlerError(AgentError):
    """爬虫Agent异常"""

    pass


class StorerError(AgentError):
    """存储Agent异常"""

    pass


class AnalyzerError(AgentError):
    """分析Agent异常"""

    pass


class GeneratorError(AgentError):
    """生成Agent异常"""

    pass


class EmbeddingError(AgentError):
    """向量化Agent异常"""

    pass


class ConfigError(WxAgentError):
    """配置相关异常"""

    pass


class ValidationError(WxAgentError):
    """数据验证异常"""

    pass


class NetworkError(WxAgentError):
    """网络相关异常"""

    pass


class StorageError(WxAgentError):
    """存储相关异常"""

    pass


class ModelError(WxAgentError):
    """模型相关异常"""

    pass


class WorkflowError(WxAgentError):
    """工作流相关异常"""

    pass


class DifyIntegrationError(WxAgentError):
    """Dify集成异常"""

    pass


# 具体的异常类
class ArticleNotFoundError(CrawlerError):
    """文章未找到异常"""

    pass


class CrawlRateLimitError(CrawlerError):
    """爬取频率限制异常"""

    pass


class InvalidArticleDataError(ValidationError):
    """无效文章数据异常"""

    pass


class StorageConnectionError(StorageError):
    """存储连接异常"""

    pass


class ModelLoadError(ModelError):
    """模型加载异常"""

    pass


class WorkflowExecutionError(WorkflowError):
    """工作流执行异常"""

    pass


class ConfigurationError(ConfigError):
    """配置错误异常"""

    pass


class NetworkTimeoutError(NetworkError):
    """网络超时异常"""

    pass


class AuthenticationError(WxAgentError):
    """认证异常"""

    pass


class PermissionError(WxAgentError):
    """权限异常"""

    pass


class ResourceNotFoundError(WxAgentError):
    """资源未找到异常"""

    pass


class DataProcessingError(WxAgentError):
    """数据处理异常"""

    pass


class ExternalServiceError(WxAgentError):
    """外部服务异常"""

    pass


# 异常处理工具类
class ExceptionHandler:
    """异常处理器"""

    @staticmethod
    def handle_agent_exception(exception: AgentError, agent_name: str) -> dict[str, Any]:
        """
        处理Agent异常

        Args:
            exception: Agent异常
            agent_name: Agent名称

        Returns:
            处理结果
        """
        error_info = {
            "agent_name": agent_name,
            "error_type": exception.__class__.__name__,
            "message": exception.message,
            "error_code": exception.error_code,
            "details": exception.details,
            "handled": True,
        }

        # 根据异常类型进行特殊处理
        if isinstance(exception, CrawlRateLimitError):
            error_info["retry_after"] = 60  # 1分钟后重试
            error_info["suggestion"] = "建议降低爬取频率"
        elif isinstance(exception, NetworkTimeoutError):
            error_info["retry_after"] = 30  # 30秒后重试
            error_info["suggestion"] = "检查网络连接"
        elif isinstance(exception, StorageConnectionError):
            error_info["suggestion"] = "检查存储服务状态"
        elif isinstance(exception, ModelLoadError):
            error_info["suggestion"] = "检查模型文件是否存在"

        return error_info

    @staticmethod
    def handle_workflow_exception(exception: WorkflowError, workflow_name: str) -> dict[str, Any]:
        """
        处理工作流异常

        Args:
            exception: 工作流异常
            workflow_name: 工作流名称

        Returns:
            处理结果
        """
        error_info = {
            "workflow_name": workflow_name,
            "error_type": exception.__class__.__name__,
            "message": exception.message,
            "error_code": exception.error_code,
            "details": exception.details,
            "handled": True,
        }

        return error_info

    @staticmethod
    def is_retryable_exception(exception: Exception) -> bool:
        """
        判断异常是否可重试

        Args:
            exception: 异常对象

        Returns:
            是否可重试
        """
        retryable_exceptions = [NetworkTimeoutError, CrawlRateLimitError, StorageConnectionError, ExternalServiceError]

        return any(isinstance(exception, exc_type) for exc_type in retryable_exceptions)

    @staticmethod
    def get_retry_delay(exception: Exception) -> int:
        """
        获取重试延迟时间（秒）

        Args:
            exception: 异常对象

        Returns:
            重试延迟时间
        """
        if isinstance(exception, CrawlRateLimitError):
            return 60  # 1分钟
        elif isinstance(exception, NetworkTimeoutError):
            return 30  # 30秒
        elif isinstance(exception, StorageConnectionError):
            return 10  # 10秒
        elif isinstance(exception, ExternalServiceError):
            return 15  # 15秒
        else:
            return 5  # 默认5秒


# 异常装饰器
def handle_exceptions(func):
    """
    异常处理装饰器

    Args:
        func: 被装饰的函数

    Returns:
        装饰后的函数
    """

    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except WxAgentError as e:
            # 记录异常
            if hasattr(args[0], "logger"):
                args[0].logger.error(f"捕获到系统异常: {e.message}")
            raise
        except Exception as e:
            # 将未知异常转换为系统异常
            if hasattr(args[0], "logger"):
                args[0].logger.error(f"捕获到未知异常: {str(e)}")

    return wrapper


def retry_on_exception(max_retries: int = 3, exceptions: tuple = None):
    """
    异常重试装饰器

    Args:
        max_retries: 最大重试次数
        exceptions: 需要重试的异常类型

    Returns:
        装饰器函数
    """
    if exceptions is None:
        exceptions = (NetworkTimeoutError, CrawlRateLimitError, StorageConnectionError)

    def decorator(func):
        def wrapper(*args, **kwargs):
            last_exception = None

            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e

                    if attempt < max_retries:
                        delay = ExceptionHandler.get_retry_delay(e)
                        if hasattr(args[0], "logger"):
                            args[0].logger.warning(f"第{attempt + 1}次重试失败: {e.message}, " f"{delay}秒后重试")
                        import time

                        time.sleep(delay)
                    else:
                        if hasattr(args[0], "logger"):
                            args[0].logger.error(f"重试{max_retries}次后仍然失败: {e.message}")
                        raise

            # 如果所有重试都失败了
            raise last_exception

        return wrapper

    return decorator


# 异常上下文管理器
class ExceptionContext:
    """异常上下文管理器"""

    def __init__(self, logger=None, error_handler=None):
        """
        初始化异常上下文管理器

        Args:
            logger: 日志记录器
            error_handler: 错误处理器
        """
        self.logger = logger
        self.error_handler = error_handler
        self.exception = None

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.exception = exc_val

            if self.logger:
                self.logger.error(f"上下文异常: {exc_val}")

            if self.error_handler:
                self.error_handler(exc_val)

            # 如果是系统异常，不重新抛出
            if isinstance(exc_val, WxAgentError):
                return True

            # 其他异常重新抛出
            return False

        return True

    def get_exception(self):
        """获取异常对象"""
        return self.exception
