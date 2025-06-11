import pytest
from pathlib import Path
from typing import Dict, Any
from loguru import logger
from rag_service.app.core.prompts.templates import (
    RoleBasedPrompt,
    ChainOfThoughtPrompt,
    FewShotPrompt,
    SelfConsistencyPrompt,
    SelfCritiquePrompt,
    DomainPrompt,
    TaskPrompt
)

# 模板类型映射
TEMPLATE_CLASSES = {
    "RoleBasedPrompt": RoleBasedPrompt,
    "ChainOfThoughtPrompt": ChainOfThoughtPrompt,
    "FewShotPrompt": FewShotPrompt,
    "SelfConsistencyPrompt": SelfConsistencyPrompt,
    "SelfCritiquePrompt": SelfCritiquePrompt,
    "DomainPrompt": DomainPrompt,
    "TaskPrompt": TaskPrompt
}

@pytest.fixture
def templates_dir():
    """获取实际模板目录"""
    return Path(__file__).parent.parent / "templates"

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

# 基础模板测试
@pytest.mark.base
@pytest.mark.parametrize("template_info", load_template_files(Path(__file__).parent.parent / "templates")["base"])
def test_base_templates(templates_dir, template_info):
    """测试基础模板"""
    template_path = template_info["path"]
    template_name = template_info["name"]
    
    # 根据模板名称确定对应的类
    if template_name == "chain_of_thought":
        prompt_class = ChainOfThoughtPrompt
        expected_type = "ChainOfThoughtPrompt"
        expected_attrs = ["steps"]
    elif template_name == "few_shot":
        prompt_class = FewShotPrompt
        expected_type = "FewShotPrompt"
        expected_attrs = ["examples"]
    elif template_name == "self_consistency":
        prompt_class = SelfConsistencyPrompt
        expected_type = "SelfConsistencyPrompt"
        expected_attrs = ["perspectives"]
    elif template_name == "self_critique":
        prompt_class = SelfCritiquePrompt
        expected_type = "SelfCritiquePrompt"
        expected_attrs = ["initial_answer"]
    else:
        pytest.skip(f"未知的基础模板类型: {template_name}")
    
    prompt = prompt_class(str(template_path))
    
    # 验证基本属性
    assert prompt.version is not None
    assert prompt.desc is not None
    
    # 验证特定属性
    for attr in expected_attrs:
        assert hasattr(prompt, attr)
        value = getattr(prompt, attr)
        if attr != "initial_answer":  # initial_answer 可能为 None
            assert value is not None
    
    # 验证数据转换
    data = prompt.to_dict()
    assert data["type"] == expected_type
    assert data["version"] is not None
    assert data["desc"] is not None

# 角色模板测试
@pytest.mark.roles
@pytest.mark.parametrize("template_info", load_template_files(Path(__file__).parent.parent / "templates")["roles"])
def test_role_templates(templates_dir, template_info):
    """测试角色模板"""
    template_path = template_info["path"]
    prompt = RoleBasedPrompt(str(template_path))
    
    # 验证基本属性
    assert prompt.role is not None
    assert prompt.expertise is not None
    assert len(prompt.expertise) > 0
    assert all(isinstance(skill, str) for skill in prompt.expertise)
    
    # 验证模板渲染
    result = prompt.render(
        domain="技术",
        expertise=["编程", "系统设计"],
        task_instruction="请回答以下问题"
    )
    assert "技术" in result
    assert "编程" in result
    assert "系统设计" in result
    
    # 验证数据转换
    data = prompt.to_dict()
    assert data["type"] == "RoleBasedPrompt"
    assert data["role"] == prompt.role
    assert data["expertise"] == prompt.expertise
    assert data["version"] is not None
    assert data["desc"] is not None

# 领域模板测试
@pytest.mark.domains
@pytest.mark.parametrize("template_info", load_template_files(Path(__file__).parent.parent / "templates")["domains"])
def test_domain_templates(templates_dir, template_info):
    """测试领域模板"""
    template_path = template_info["path"]
    prompt = DomainPrompt(str(template_path), subdomains=["子领域1", "子领域2"])
    
    # 验证基本属性
    assert prompt.domain is not None
    assert prompt.subdomains is not None
    assert len(prompt.subdomains) > 0
    assert all(isinstance(sd, str) for sd in prompt.subdomains)
    
    # 验证模板渲染
    result = prompt.format(
        domain="技术领域",
        sub_domains=[ d for d in prompt.subdomains ],
        role_instruction="你是一个测试专家，擅长编写基于pytest的测试用例"
    )
    assert "技术领域" in result
    assert "子领域1" in result
    assert "子领域2" in result
    
    # 验证数据转换
    data = prompt.to_dict()
    assert data["type"] == "DomainPrompt"
    assert data["domain"] == prompt.domain
    assert data["subdomains"] == prompt.subdomains
    assert data["version"] is not None
    assert data["desc"] is not None

# 任务模板测试
@pytest.mark.tasks
@pytest.mark.parametrize("template_info", load_template_files(Path(__file__).parent.parent / "templates")["tasks"])
def test_task_templates(templates_dir, template_info):
    """测试任务模板"""
    template_path = template_info["path"]
    template_name = template_info["name"]
    prompt = TaskPrompt(str(template_path))
    
    # 验证基本属性
    assert prompt.task_type is not None
    assert prompt.steps is not None
    assert len(prompt.steps) > 0
    assert all(isinstance(step, str) for step in prompt.steps)
    
    # 根据任务类型准备测试数据
    test_data = {
        "translation": {
            "task_type": "翻译任务",
            "steps": [ "原文理解", "翻译转换", "质量检查" ],
            "source_content": "Hello World. The quick brown fox jumps over the lazy dog.",
            "target_language": "中文",
            "requirements": "请将这段文本翻译成中文",
            "domain_knowledge": "参考牛津词典",
        },
        "classification": {
            "task_type": "文本分类",
            "steps": [ "特征分析", "分类判断", "结果验证" ],
            "text": "这是一段测试文本",
            "content": "这是一段测试文本",
            "criteria": "是中文还是英文",
            "categories": ["类别1", "类别2"],
            "domain_knowledge": "参考新华字典",
        },
        "summarization": {
            "task_type": "文本摘要",
            "steps": [ "内容分析", "摘要生成", "质量检查" ], 
            "content": "这是一段测试文本,它讲述了一个来自遥远东方国度,有一个国王和他10个儿子的故事",
            "requirements": "请总结这段文本的中心思想",
            "domain_knowledge": "参考天方夜谭",
        },
        "problem_solving": {
            "task_type": "问题解决",
            "steps": [ "问题分析", "方案设计", "实施步骤", "验证和优化" ],
            "domain_knowledge": "参考测试问题排查手册",
        }
    }
    
    # 验证模板渲染
    logger.debug(f"template_name: {template_name}, template_info: {template_info}")
    if template_name in test_data:
        result = prompt.format(**test_data[template_name])
        for value in test_data[template_name].values():
            if isinstance(value, (str, int)):
                assert str(value) in result
            elif isinstance(value, list):
                for item in value:
                    assert str(item) in result
    
    # 验证数据转换
    data = prompt.to_dict()
    assert data["type"] == "TaskPrompt"
    assert data["task_type"] == prompt.task_type
    assert data["steps"] == prompt.steps
    assert data["version"] is not None
    assert data["desc"] is not None 