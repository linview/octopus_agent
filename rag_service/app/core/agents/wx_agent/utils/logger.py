"""
日志工具模块

提供统一的日志记录功能
"""

import sys
from pathlib import Path

from loguru import logger

from models.agent_config import LoggingConfig


class LoggerManager:
    """日志管理器"""

    def __init__(self, config: LoggingConfig | None = None):
        """
        初始化日志管理器

        Args:
            config: 日志配置
        """
        self.config = config or LoggingConfig()
        self._setup_logger()

    def _setup_logger(self) -> None:
        """设置日志记录器"""
        # 移除默认的日志处理器
        logger.remove()

        # 确保日志目录存在
        log_dir = Path(self.config.file_path).parent
        log_dir.mkdir(parents=True, exist_ok=True)

        # 配置日志格式
        log_format = self.config.format

        # 控制台输出
        if self.config.console_output:
            logger.add(sys.stdout, format=log_format, level=self.config.level, colorize=True)

        # 文件输出
        if self.config.file_output:
            logger.add(
                self.config.file_path,
                format=log_format,
                level=self.config.level,
                rotation=self.config.max_size,
                retention=self.config.retention,
                compression="zip",
                backtrace=True,
                diagnose=True,
            )

    def get_logger(self, name: str | None = None):
        """
        获取日志记录器

        Args:
            name: 日志记录器名称

        Returns:
            日志记录器
        """
        if name:
            return logger.bind(name=name)
        return logger

    def update_config(self, config: LoggingConfig) -> None:
        """
        更新日志配置

        Args:
            config: 新的日志配置
        """
        self.config = config
        self._setup_logger()

    def set_level(self, level: str) -> None:
        """
        设置日志级别

        Args:
            level: 日志级别
        """
        self.config.level = level.upper()
        self._setup_logger()

    def enable_console_output(self, enabled: bool = True) -> None:
        """
        启用/禁用控制台输出

        Args:
            enabled: 是否启用
        """
        self.config.console_output = enabled
        self._setup_logger()

    def enable_file_output(self, enabled: bool = True) -> None:
        """
        启用/禁用文件输出

        Args:
            enabled: 是否启用
        """
        self.config.file_output = enabled
        self._setup_logger()


class AgentLogger:
    """Agent专用日志记录器"""

    def __init__(self, agent_name: str, config: LoggingConfig | None = None):
        """
        初始化Agent日志记录器

        Args:
            agent_name: Agent名称
            config: 日志配置
        """
        self.agent_name = agent_name
        self.logger_manager = LoggerManager(config)
        self.logger = self.logger_manager.get_logger(agent_name)

    def info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        self.logger.info(f"[{self.agent_name}] {message}", **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        self.logger.debug(f"[{self.agent_name}] {message}", **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        self.logger.warning(f"[{self.agent_name}] {message}", **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        self.logger.error(f"[{self.agent_name}] {message}", **kwargs)

    def critical(self, message: str, **kwargs) -> None:
        """记录严重错误日志"""
        self.logger.critical(f"[{self.agent_name}] {message}", **kwargs)

    def exception(self, message: str, **kwargs) -> None:
        """记录异常日志"""
        self.logger.exception(f"[{self.agent_name}] {message}", **kwargs)

    def success(self, message: str, **kwargs) -> None:
        """记录成功日志"""
        self.logger.success(f"[{self.agent_name}] {message}", **kwargs)

    def log_execution_start(self, method_name: str, **kwargs) -> None:
        """记录方法执行开始"""
        self.info(f"开始执行方法: {method_name}", **kwargs)

    def log_execution_end(self, method_name: str, duration: float, **kwargs) -> None:
        """记录方法执行结束"""
        self.info(f"方法执行完成: {method_name}, 耗时: {duration:.2f}秒", **kwargs)

    def log_execution_error(self, method_name: str, error: Exception, **kwargs) -> None:
        """记录方法执行错误"""
        self.error(f"方法执行失败: {method_name}, 错误: {str(error)}", **kwargs)

    def log_data_processing(self, data_type: str, count: int, **kwargs) -> None:
        """记录数据处理日志"""
        self.info(f"处理{data_type}数据: {count}条", **kwargs)

    def log_performance(self, operation: str, duration: float, **kwargs) -> None:
        """记录性能日志"""
        self.info(f"性能统计 - {operation}: {duration:.2f}秒", **kwargs)


class WorkflowLogger:
    """工作流专用日志记录器"""

    def __init__(self, workflow_name: str, config: LoggingConfig | None = None):
        """
        初始化工作流日志记录器

        Args:
            workflow_name: 工作流名称
            config: 日志配置
        """
        self.workflow_name = workflow_name
        self.logger_manager = LoggerManager(config)
        self.logger = self.logger_manager.get_logger(workflow_name)

    def info(self, message: str, **kwargs) -> None:
        """记录信息日志"""
        self.logger.info(f"[{self.workflow_name}] {message}", **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        """记录调试日志"""
        self.logger.debug(f"[{self.workflow_name}] {message}", **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        """记录警告日志"""
        self.logger.warning(f"[{self.workflow_name}] {message}", **kwargs)

    def error(self, message: str, **kwargs) -> None:
        """记录错误日志"""
        self.logger.error(f"[{self.workflow_name}] {message}", **kwargs)

    def log_workflow_start(self, **kwargs) -> None:
        """记录工作流开始"""
        self.info("工作流开始执行", **kwargs)

    def log_workflow_end(self, success: bool, duration: float, **kwargs) -> None:
        """记录工作流结束"""
        status = "成功" if success else "失败"
        self.info(f"工作流执行{status}, 总耗时: {duration:.2f}秒", **kwargs)

    def log_agent_execution(self, agent_name: str, success: bool, duration: float, **kwargs) -> None:
        """记录Agent执行日志"""
        status = "成功" if success else "失败"
        self.info(f"Agent {agent_name} 执行{status}, 耗时: {duration:.2f}秒", **kwargs)

    def log_workflow_step(self, step_name: str, **kwargs) -> None:
        """记录工作流步骤"""
        self.info(f"执行步骤: {step_name}", **kwargs)


# 全局日志管理器
_global_logger_manager: LoggerManager | None = None


def get_global_logger_manager() -> LoggerManager:
    """
    获取全局日志管理器

    Returns:
        全局日志管理器
    """
    global _global_logger_manager
    if _global_logger_manager is None:
        _global_logger_manager = LoggerManager()
    return _global_logger_manager


def set_global_logger_manager(manager: LoggerManager) -> None:
    """
    设置全局日志管理器

    Args:
        manager: 日志管理器
    """
    global _global_logger_manager
    _global_logger_manager = manager


def get_logger(name: str | None = None):
    """
    获取日志记录器

    Args:
        name: 日志记录器名称

    Returns:
        日志记录器
    """
    manager = get_global_logger_manager()
    return manager.get_logger(name)


def setup_logging(config: LoggingConfig) -> None:
    """
    设置日志配置

    Args:
        config: 日志配置
    """
    manager = LoggerManager(config)
    set_global_logger_manager(manager)


# 日志装饰器
def log_execution(logger_name: str | None = None):
    """
    记录方法执行的装饰器

    Args:
        logger_name: 日志记录器名称

    Returns:
        装饰器函数
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取日志记录器
            log = args[0].logger if hasattr(args[0], "logger") else get_logger(logger_name or func.__module__)

            # 记录执行开始
            log.log_execution_start(func.__name__)

            import time

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                log.log_execution_end(func.__name__, duration)
                return result
            except Exception as e:
                duration = time.time() - start_time
                log.log_execution_error(func.__name__, e)
                raise

        return wrapper

    return decorator


def log_performance(operation_name: str | None = None):
    """
    记录性能的装饰器

    Args:
        operation_name: 操作名称

    Returns:
        装饰器函数
    """

    def decorator(func):
        def wrapper(*args, **kwargs):
            # 获取日志记录器
            log = args[0].logger if hasattr(args[0], "logger") else get_logger(func.__module__)

            import time

            start_time = time.time()

            try:
                result = func(*args, **kwargs)
                duration = time.time() - start_time
                op_name = operation_name or func.__name__
                log.log_performance(op_name, duration)
                return result
            except Exception:
                duration = time.time() - start_time
                op_name = operation_name or func.__name__
                log.log_performance(f"{op_name} (失败)", duration)
                raise

        return wrapper

    return decorator
