import pytest
from pathlib import Path
from typing import Dict, Any
from rag_service.app.core.prompts.manager import PromptManager

def load_template_files(templates_dir: Path) -> Dict[str, Dict[str, Any]]:
    """加载所有模板文件信息"""
    templates = {}
    for yaml_file in templates_dir.rglob("*.yaml"):
        category = yaml_file.parent.name
        if category not in templates:
            templates[category] = []
        templates[category].append({
            "path": yaml_file,
            "name": yaml_file.stem,
            "category": category
        })
    return templates

@pytest.fixture
def templates_dir():
    """获取实际模板目录"""
    return Path(__file__).parent.parent / "templates"

@pytest.fixture
def manager(templates_dir):
    """创建PromptManager实例"""
    return PromptManager(str(templates_dir))

@pytest.mark.manager
def test_init(manager, templates_dir):
    """测试初始化"""
    assert manager.templates_dir == templates_dir
    assert len(manager.templates) > 0

@pytest.mark.manager
@pytest.mark.parametrize("template_info", load_template_files(Path(__file__).parent.parent / "templates")["roles"])
def test_get_template(manager, template_info):
    """测试获取模板"""
    template_name = template_info["name"]
    
    # 测试获取存在的模板
    template = manager.get_template(template_name)
    assert template.version is not None
    assert template.desc is not None
    
    # 测试获取指定版本
    template = manager.get_template(template_name, version=template.version)
    assert template.version is not None
    
    # 测试获取不存在的模板
    with pytest.raises(KeyError):
        manager.get_template("not_exist")

@pytest.mark.manager
@pytest.mark.parametrize("template_info", load_template_files(Path(__file__).parent.parent / "templates")["roles"])
def test_get_template_info(manager, template_info):
    """测试获取模板信息"""
    template_name = template_info["name"]
    info = manager.get_template_info(template_name)
    
    assert info["type"] is not None
    assert info["version"] is not None
    assert info["desc"] is not None
    assert "tags" in info

@pytest.mark.manager
def test_list_templates(manager):
    """测试列出模板"""
    templates = manager.list_templates()
    assert len(templates) > 0
    
    # 验证所有模板文件都存在
    for template_name in templates:
        template = manager.get_template(template_name)
        assert template.version is not None
        assert template.desc is not None

@pytest.mark.manager
def test_get_templates_by_type(manager):
    """测试按类型获取模板"""
    # 测试获取角色模板
    role_templates = manager.get_templates_by_type("RoleBasedPrompt")
    assert len(role_templates) > 0
    for template_name in role_templates:
        template = manager.get_template(template_name)
        assert template.role is not None
    
    # 测试获取思维链模板
    cot_templates = manager.get_templates_by_type("ChainOfThoughtPrompt")
    assert len(cot_templates) > 0
    for template_name in cot_templates:
        template = manager.get_template(template_name)
        assert template.steps is not None

@pytest.mark.manager
@pytest.mark.parametrize("template_info", load_template_files(Path(__file__).parent.parent / "templates")["roles"])
def test_format_template(manager, template_info):
    """测试格式化模板"""
    template_name = template_info["name"]
    
    # 测试格式化角色模板
    result = manager.format_template(
        template_name,
        domain="技术",
        expertise=["编程", "系统设计"],
        task_instruction="请回答以下问题"
    )
    assert "技术" in result
    assert "编程" in result
    assert "系统设计" in result

@pytest.mark.manager
def test_combine_templates(manager):
    """测试组合模板"""
    # 测试组合角色和领域模板
    strategy = {
        "expert": "role_prompt",
        "technical": "domain_prompt",
    }
    result = manager.combine_templates(
        strategy,
        # for role: expert
        domain="技术",
        expertise=["编程"],
#        subdomains=["软件开发"],
        task_instruction="开发一款聊天软件",
        # for domain: technical
        role_instruction="你是一个js专家，擅长编写前端对话软件",
        sub_domains=["软件开发", "前端开发", "全栈应用"],
    )
    
    assert "role_prompt" in result
    assert "domain_prompt" in result
    assert "技术" in result["role_prompt"]
    assert "软件开发" in result["domain_prompt"] 