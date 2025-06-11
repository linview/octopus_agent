import pytest

def pytest_configure(config):
    """注册自定义标记"""
    config.addinivalue_line("markers", "base: 基础模板测试")
    config.addinivalue_line("markers", "roles: 角色模板测试")
    config.addinivalue_line("markers", "domains: 领域模板测试")
    config.addinivalue_line("markers", "tasks: 任务模板测试")
    config.addinivalue_line("markers", "manager: 管理器测试") 