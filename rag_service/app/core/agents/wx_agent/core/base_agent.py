"""
Agent基类模块

提供所有Agent的基础功能和统一接口
"""

import asyncio
from abc import ABC, abstractmethod
from datetime import datetime
from typing import Any, Dict, Optional

from loguru import logger


class BaseAgent(ABC):
    """Agent基类，提供统一的接口和基础功能"""
    
    def __init__(self, config: Dict[str, Any]):
        """
        初始化Agent
        
        Args:
            config: Agent配置字典
        """
        self.config = config
        self.logger = self._setup_logger()
        self.agent_name = self.__class__.__name__
        self.last_execution = None
        self.execution_count = 0
        
    def _setup_logger(self) -> logger:
        """设置日志记录器"""
        # 配置日志格式
        log_format = (
            "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
            "<level>{level: <8}</level> | "
            "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
            "<level>{message}</level>"
        )
        
        # 添加文件日志
        logger.add(
            "logs/wx_agent.log",
            format=log_format,
            level="INFO",
            rotation="10 MB",
            retention="7 days"
        )
        
        return logger.bind(agent=self.__class__.__name__)
    
    async def execute(self, input_data: Any) -> Any:
        """
        执行Agent任务的主入口
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
            
        Raises:
            Exception: 处理过程中的异常
        """
        start_time = datetime.now()
        self.execution_count += 1
        
        try:
            self.logger.info(f"开始执行 {self.agent_name}，输入数据: {type(input_data)}")
            
            # 执行具体处理逻辑
            result = await self._process(input_data)
            
            # 记录执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.last_execution = datetime.now()
            
            self.logger.info(
                f"{self.agent_name} 执行成功，耗时: {execution_time:.2f}秒，"
                f"结果类型: {type(result)}"
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(
                f"{self.agent_name} 执行失败，耗时: {execution_time:.2f}秒，"
                f"错误: {str(e)}"
            )
            raise
    
    @abstractmethod
    async def _process(self, input_data: Any) -> Any:
        """
        子类实现的具体处理逻辑
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        pass
    
    def get_status(self) -> Dict[str, Any]:
        """
        获取Agent状态信息
        
        Returns:
            Agent状态字典
        """
        return {
            "agent_name": self.agent_name,
            "status": "ready",
            "last_execution": self.last_execution.isoformat() if self.last_execution else None,
            "execution_count": self.execution_count,
            "config_keys": list(self.config.keys()) if self.config else []
        }
    
    def validate_input(self, input_data: Any) -> bool:
        """
        验证输入数据的有效性
        
        Args:
            input_data: 输入数据
            
        Returns:
            是否有效
        """
        # 子类可以重写此方法进行具体的输入验证
        return input_data is not None
    
    def preprocess_input(self, input_data: Any) -> Any:
        """
        预处理输入数据
        
        Args:
            input_data: 原始输入数据
            
        Returns:
            预处理后的数据
        """
        # 子类可以重写此方法进行数据预处理
        return input_data
    
    def postprocess_output(self, output_data: Any) -> Any:
        """
        后处理输出数据
        
        Args:
            output_data: 原始输出数据
            
        Returns:
            后处理后的数据
        """
        # 子类可以重写此方法进行数据后处理
        return output_data
    
    async def health_check(self) -> Dict[str, Any]:
        """
        Agent健康检查
        
        Returns:
            健康状态信息
        """
        return {
            "agent_name": self.agent_name,
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "config_loaded": bool(self.config),
            "logger_ready": self.logger is not None
        }
    
    def get_config(self, key: str, default: Any = None) -> Any:
        """
        获取配置值
        
        Args:
            key: 配置键
            default: 默认值
            
        Returns:
            配置值
        """
        return self.config.get(key, default)
    
    def set_config(self, key: str, value: Any) -> None:
        """
        设置配置值
        
        Args:
            key: 配置键
            value: 配置值
        """
        self.config[key] = value
        self.logger.debug(f"更新配置: {key} = {value}")


class AsyncBaseAgent(BaseAgent):
    """异步Agent基类，提供异步处理能力"""
    
    async def _process(self, input_data: Any) -> Any:
        """
        异步处理逻辑，子类必须实现
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        raise NotImplementedError("子类必须实现 _process 方法")
    
    async def execute_batch(self, input_data_list: list) -> list:
        """
        批量执行任务
        
        Args:
            input_data_list: 输入数据列表
            
        Returns:
            处理结果列表
        """
        tasks = [self.execute(input_data) for input_data in input_data_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"批量处理第{i}个任务失败: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results


class SyncBaseAgent(BaseAgent):
    """同步Agent基类，提供同步处理能力"""
    
    def _process(self, input_data: Any) -> Any:
        """
        同步处理逻辑，子类必须实现
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        raise NotImplementedError("子类必须实现 _process 方法")
    
    async def execute(self, input_data: Any) -> Any:
        """
        重写execute方法，将同步处理包装为异步
        
        Args:
            input_data: 输入数据
            
        Returns:
            处理结果
        """
        start_time = datetime.now()
        self.execution_count += 1
        
        try:
            self.logger.info(f"开始执行 {self.agent_name}，输入数据: {type(input_data)}")
            
            # 在线程池中执行同步处理
            loop = asyncio.get_event_loop()
            result = await loop.run_in_executor(None, self._process, input_data)
            
            # 记录执行时间
            execution_time = (datetime.now() - start_time).total_seconds()
            self.last_execution = datetime.now()
            
            self.logger.info(
                f"{self.agent_name} 执行成功，耗时: {execution_time:.2f}秒，"
                f"结果类型: {type(result)}"
            )
            
            return result
            
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            self.logger.error(
                f"{self.agent_name} 执行失败，耗时: {execution_time:.2f}秒，"
                f"错误: {str(e)}"
            )
            raise
    
    async def execute_batch(self, input_data_list: list) -> list:
        """
        批量执行任务
        
        Args:
            input_data_list: 输入数据列表
            
        Returns:
            处理结果列表
        """
        tasks = [self.execute(input_data) for input_data in input_data_list]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # 处理异常结果
        processed_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                self.logger.error(f"批量处理第{i}个任务失败: {result}")
                processed_results.append(None)
            else:
                processed_results.append(result)
        
        return processed_results 