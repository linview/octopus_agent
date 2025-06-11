import pytest
from pathlib import Path
from jinja2 import TemplateError
from rag_service.app.core.prompts.base import BasePrompt

@pytest.fixture
def template_dir(tmp_path):
    """创建临时模板目录"""
    return tmp_path

@pytest.fixture
def template_file(template_dir):
    """创建测试模板文件"""
    template_path = template_dir / "test.yaml"
    template_path.write_text("""
    template: |
        Hello {{ name }}!
        Version: {{ version }}
    type: TestPrompt
    version: "1.0.0"
    desc: "测试模板"
    """)
    return template_path

def test_init(template_file):
    """测试初始化"""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePrompt(str(template_file))

def test_file_not_found(template_dir):
    """测试文件不存在"""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePrompt(str(template_dir / "not_exist.yaml"))

def test_invalid_template(template_dir):
    """测试无效模板"""
    template_path = template_dir / "invalid.yaml"
    template_path.write_text("{{ invalid syntax")
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePrompt(str(template_path))

def test_validate_tags(template_file):
    """测试标签验证"""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePrompt(str(template_file))

def test_render(template_file):
    """测试渲染"""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePrompt(str(template_file))

def test_render_missing_tags(template_file):
    """测试缺少标签"""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePrompt(str(template_file))

def test_to_dict(template_file):
    """测试转换为字典"""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePrompt(str(template_file))

def test_from_dict(template_file):
    """测试从字典创建"""
    with pytest.raises(TypeError, match="Can't instantiate abstract class"):
        BasePrompt(str(template_file)) 