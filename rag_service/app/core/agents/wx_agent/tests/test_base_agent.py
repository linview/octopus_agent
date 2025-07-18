"""
BaseAgent测试模块

测试Agent基类的功能
"""

import pytest
import asyncio
from datetime import datetime
from typing import Dict, Any

from core.base_agent import BaseAgent, AsyncBaseAgent, SyncBaseAgent


class TestAsyncAgent(AsyncBaseAgent):
    """测试用的异步Agent"""
    
    async def _process(self, input_data: Any) -> Any:
        """测试处理逻辑"""
        await asyncio.sleep(0.1)  # 模拟异步处理
        return f"processed: {input_data}"


class TestSyncAgent(SyncBaseAgent):
    """测试用的同步Agent"""
    
    def _process(self, input_data: Any) -> Any:
        """测试处理逻辑"""
        return f"processed: {input_data}"


class TestFailingAgent(AsyncBaseAgent):
    """测试用的失败Agent"""
    
    async def _process(self, input_data: Any) -> Any:
        """总是失败的处理逻辑"""
        raise Exception("Test error")


@pytest.fixture
def sample_config():
    """测试配置"""
    return {
        "test_key": "test_value",
        "max_retries": 3,
        "timeout": 30
    }


@pytest.fixture
def async_agent(sample_config):
    """异步Agent实例"""
    return TestAsyncAgent(sample_config)


@pytest.fixture
def sync_agent(sample_config):
    """同步Agent实例"""
    return TestSyncAgent(sample_config)


@pytest.fixture
def failing_agent(sample_config):
    """失败Agent实例"""
    return TestFailingAgent(sample_config)


class TestBaseAgent:
    """BaseAgent测试类"""
    
    def test_agent_initialization(self, async_agent, sample_config):
        """测试Agent初始化"""
        assert async_agent.config == sample_config
        assert async_agent.agent_name == "TestAsyncAgent"
        assert async_agent.execution_count == 0
        assert async_agent.last_execution is None
        assert async_agent.logger is not None
    
    def test_get_status(self, async_agent):
        """测试获取状态"""
        status = async_agent.get_status()
        
        assert status["agent_name"] == "TestAsyncAgent"
        assert status["status"] == "ready"
        assert status["execution_count"] == 0
        assert status["last_execution"] is None
        assert "test_key" in status["config_keys"]
    
    def test_get_config(self, async_agent):
        """测试获取配置"""
        assert async_agent.get_config("test_key") == "test_value"
        assert async_agent.get_config("nonexistent", "default") == "default"
    
    def test_set_config(self, async_agent):
        """测试设置配置"""
        async_agent.set_config("new_key", "new_value")
        assert async_agent.get_config("new_key") == "new_value"
    
    def test_validate_input(self, async_agent):
        """测试输入验证"""
        assert async_agent.validate_input("test") is True
        assert async_agent.validate_input(None) is False
    
    def test_preprocess_input(self, async_agent):
        """测试输入预处理"""
        result = async_agent.preprocess_input("test")
        assert result == "test"
    
    def test_postprocess_output(self, async_agent):
        """测试输出后处理"""
        result = async_agent.postprocess_output("test")
        assert result == "test"
    
    @pytest.mark.asyncio
    async def test_health_check(self, async_agent):
        """测试健康检查"""
        health = await async_agent.health_check()
        
        assert health["agent_name"] == "TestAsyncAgent"
        assert health["status"] == "healthy"
        assert health["config_loaded"] is True
        assert health["logger_ready"] is True
        assert "timestamp" in health


class TestAsyncBaseAgent:
    """AsyncBaseAgent测试类"""
    
    @pytest.mark.asyncio
    async def test_async_execute_success(self, async_agent):
        """测试异步执行成功"""
        result = await async_agent.execute("test_input")
        
        assert result == "processed: test_input"
        assert async_agent.execution_count == 1
        assert async_agent.last_execution is not None
    
    @pytest.mark.asyncio
    async def test_async_execute_failure(self, failing_agent):
        """测试异步执行失败"""
        with pytest.raises(Exception, match="Test error"):
            await failing_agent.execute("test_input")
        
        assert failing_agent.execution_count == 1
    
    @pytest.mark.asyncio
    async def test_batch_execute(self, async_agent):
        """测试批量执行"""
        inputs = ["input1", "input2", "input3"]
        results = await async_agent.execute_batch(inputs)
        
        expected = ["processed: input1", "processed: input2", "processed: input3"]
        assert results == expected
        assert async_agent.execution_count == 3
    
    @pytest.mark.asyncio
    async def test_batch_execute_with_failures(self, failing_agent):
        """测试批量执行包含失败"""
        inputs = ["input1", "input2", "input3"]
        results = await failing_agent.execute_batch(inputs)
        
        # 所有任务都应该失败，返回None
        assert results == [None, None, None]
        assert failing_agent.execution_count == 3


class TestSyncBaseAgent:
    """SyncBaseAgent测试类"""
    
    @pytest.mark.asyncio
    async def test_sync_execute_success(self, sync_agent):
        """测试同步执行成功"""
        result = await sync_agent.execute("test_input")
        
        assert result == "processed: test_input"
        assert sync_agent.execution_count == 1
        assert sync_agent.last_execution is not None
    
    def test_sync_process_direct(self, sync_agent):
        """测试直接调用同步处理"""
        result = sync_agent._process("test_input")
        assert result == "processed: test_input"


class TestAgentLogging:
    """Agent日志测试类"""
    
    def test_logger_setup(self, async_agent):
        """测试日志设置"""
        assert async_agent.logger is not None
        
        # 测试日志记录
        async_agent.logger.info("Test log message")
    
    def test_execution_logging(self, async_agent):
        """测试执行日志"""
        # 这里可以添加更详细的日志测试
        # 由于loguru的复杂性，我们主要测试日志器是否存在
        assert async_agent.logger is not None


class TestAgentConfiguration:
    """Agent配置测试类"""
    
    def test_config_validation(self):
        """测试配置验证"""
        config = {"test": "value"}
        agent = TestAsyncAgent(config)
        
        # 测试配置访问
        assert agent.get_config("test") == "value"
        assert agent.get_config("missing", "default") == "default"
    
    def test_config_update(self, async_agent):
        """测试配置更新"""
        async_agent.set_config("updated_key", "updated_value")
        assert async_agent.get_config("updated_key") == "updated_value"


class TestAgentErrorHandling:
    """Agent错误处理测试类"""
    
    @pytest.mark.asyncio
    async def test_execution_error_logging(self, failing_agent):
        """测试执行错误日志"""
        with pytest.raises(Exception):
            await failing_agent.execute("test")
        
        # 验证执行计数增加
        assert failing_agent.execution_count == 1
    
    def test_invalid_input_handling(self, async_agent):
        """测试无效输入处理"""
        # 测试输入验证
        assert async_agent.validate_input("valid") is True
        assert async_agent.validate_input(None) is False


if __name__ == "__main__":
    pytest.main([__file__]) 