"""
微信公众号Agent系统演示脚本

展示Agent基类的基本功能和使用方法
"""

import asyncio
import time
from typing import Any, Dict

from core.base_agent import AsyncBaseAgent, SyncBaseAgent
from utils.config import load_config
from utils.logger import setup_logging, get_logger


class DemoAsyncAgent(AsyncBaseAgent):
    """演示用的异步Agent"""
    
    async def _process(self, input_data: Any) -> Any:
        """模拟异步处理逻辑"""
        await asyncio.sleep(0.5)  # 模拟异步处理时间
        return f"异步处理结果: {input_data}"


class DemoSyncAgent(SyncBaseAgent):
    """演示用的同步Agent"""
    
    def _process(self, input_data: Any) -> Any:
        """模拟同步处理逻辑"""
        time.sleep(0.3)  # 模拟同步处理时间
        return f"同步处理结果: {input_data}"


async def demo_async_agent():
    """演示异步Agent"""
    print("\n🔄 演示异步Agent...")
    
    config = {"demo_mode": True, "timeout": 10}
    agent = DemoAsyncAgent(config)
    
    # 测试单个执行
    print("📝 测试单个执行...")
    result = await agent.execute("测试数据1")
    print(f"结果: {result}")
    
    # 测试批量执行
    print("📝 测试批量执行...")
    inputs = ["数据1", "数据2", "数据3", "数据4"]
    results = await agent.execute_batch(inputs)
    print(f"批量结果: {results}")
    
    # 测试状态查询
    print("📝 测试状态查询...")
    status = agent.get_status()
    print(f"Agent状态: {status}")
    
    # 测试健康检查
    print("📝 测试健康检查...")
    health = await agent.health_check()
    print(f"健康状态: {health}")


async def demo_sync_agent():
    """演示同步Agent"""
    print("\n🔄 演示同步Agent...")
    
    config = {"demo_mode": True, "timeout": 10}
    agent = DemoSyncAgent(config)
    
    # 测试单个执行
    print("📝 测试单个执行...")
    result = await agent.execute("测试数据1")
    print(f"结果: {result}")
    
    # 测试批量执行
    print("📝 测试批量执行...")
    inputs = ["数据1", "数据2", "数据3", "数据4"]
    results = await agent.execute_batch(inputs)
    print(f"批量结果: {results}")
    
    # 测试状态查询
    print("📝 测试状态查询...")
    status = agent.get_status()
    print(f"Agent状态: {status}")
    
    # 测试健康检查
    print("📝 测试健康检查...")
    health = await agent.health_check()
    print(f"健康状态: {health}")


async def demo_error_handling():
    """演示错误处理"""
    print("\n🔄 演示错误处理...")
    
    class ErrorAgent(AsyncBaseAgent):
        async def _process(self, input_data: Any) -> Any:
            raise Exception("模拟处理错误")
    
    config = {"demo_mode": True}
    agent = ErrorAgent(config)
    
    try:
        result = await agent.execute("测试数据")
        print(f"结果: {result}")
    except Exception as e:
        print(f"捕获到错误: {e}")
    
    # 检查执行计数
    status = agent.get_status()
    print(f"执行计数: {status['execution_count']}")


async def demo_config_management():
    """演示配置管理"""
    print("\n🔄 演示配置管理...")
    
    config = {
        "demo_mode": True,
        "max_retries": 3,
        "timeout": 30,
        "feature_flags": {
            "enable_cache": True,
            "enable_logging": True
        }
    }
    
    agent = DemoAsyncAgent(config)
    
    # 获取配置
    print(f"最大重试次数: {agent.get_config('max_retries')}")
    print(f"超时时间: {agent.get_config('timeout')}")
    print(f"默认值测试: {agent.get_config('nonexistent', 'default_value')}")
    
    # 设置配置
    agent.set_config("new_setting", "new_value")
    print(f"新设置: {agent.get_config('new_setting')}")
    
    # 验证输入
    print(f"有效输入验证: {agent.validate_input('valid_data')}")
    print(f"无效输入验证: {agent.validate_input(None)}")


async def demo_logging():
    """演示日志功能"""
    print("\n🔄 演示日志功能...")
    
    logger = get_logger("demo")
    
    logger.info("这是一条信息日志")
    logger.warning("这是一条警告日志")
    logger.error("这是一条错误日志")
    
    print("✓ 日志记录完成，请查看 logs/wx_agent.log 文件")


async def main():
    """主演示函数"""
    print("🚀 微信公众号Agent系统演示")
    print("=" * 50)
    
    # 加载配置
    try:
        config = load_config()
        print(f"✓ 配置加载成功，版本: {config.config_version}")
        
        # 设置日志
        setup_logging(config.logging)
    except Exception as e:
        print(f"⚠️  配置加载失败: {e}")
        config = {}
    
    # 演示异步Agent
    await demo_async_agent()
    
    # 演示同步Agent
    await demo_sync_agent()
    
    # 演示错误处理
    await demo_error_handling()
    
    # 演示配置管理
    await demo_config_management()
    
    # 演示日志功能
    await demo_logging()
    
    print("\n" + "=" * 50)
    print("🎉 演示完成！")
    print("\n📋 演示内容：")
    print("- Agent基类功能")
    print("- 异步和同步处理")
    print("- 批量执行")
    print("- 错误处理")
    print("- 配置管理")
    print("- 日志记录")
    print("- 状态监控")


if __name__ == "__main__":
    asyncio.run(main()) 