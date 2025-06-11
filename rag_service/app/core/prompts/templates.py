from typing import Dict, List, Optional, Set
from pathlib import Path
from loguru import logger
from rag_service.app.core.prompts.base import BasePrompt

class BaseTemplate(BasePrompt):
    """基础模板类"""
    
    def __init__(self, template_path: str):
        super().__init__(template_path)

    def format(self, **kwargs):
        raise NotImplementedError("派生类必须实现format方法")

class RoleBasedPrompt(BaseTemplate):
    """基于角色的提示模板"""
    
    # 默认模板路径
    template_path: Path = Path(__file__).parent / "templates" / "roles" / "expert.yaml"
    
    # 成员变量
    role: Optional[str]
    expertise: List[str]
    
    def __init__(self, template_path: str, role: Optional[str] = None, expertise: Optional[List[str]] = None):
        super().__init__(template_path)
        self.role = role if role else self.role
        self.expertise = expertise if expertise else self.expertise
        
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "role": self.role,
            "expertise": self.expertise
        })
        return data

    def format(self, **kwargs):
        return self.render(**kwargs)

class ChainOfThoughtPrompt(BaseTemplate):
    """思维链提示模板"""
    
    # 默认模板路径
    template_path: Path = Path(__file__).parent / "templates" / "base" / "chain_of_thought.yaml"
    
    # 成员变量
    steps: List[str]
    
    def __init__(self, template_path: str, steps: Optional[List[str]] = None):
        super().__init__(template_path)
        self.steps = steps or []
        
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "steps": self.steps
        })
        return data

    def format(self, **kwargs):
        return self.render(**kwargs)

class FewShotPrompt(BaseTemplate):
    """少样本学习提示模板"""
    
    # 默认模板路径
    template_path: Path = Path(__file__).parent / "templates" / "base" / "few_shot.yaml"
    
    # 成员变量
    examples: List[Dict]
    
    def __init__(self, template_path: str, examples: Optional[List[Dict]] = None):
        super().__init__(template_path)
        self.examples = examples or []
        
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "examples": self.examples
        })
        return data

    def format(self, **kwargs):
        return self.render(**kwargs)

class SelfConsistencyPrompt(BaseTemplate):
    """自我一致性提示模板"""
    
    # 默认模板路径
    template_path: Path = Path(__file__).parent / "templates" / "base" / "self_consistency.yaml"
    
    # 成员变量
    perspectives: List[str]
    
    def __init__(self, template_path: str, perspectives: Optional[List[str]] = None):
        super().__init__(template_path)
        self.perspectives = perspectives or []
        
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "perspectives": self.perspectives
        })
        return data

    def format(self, **kwargs):
        return self.render(**kwargs)

class SelfCritiquePrompt(BaseTemplate):
    """自我批评提示模板"""
    
    # 默认模板路径
    template_path: Path = Path(__file__).parent / "templates" / "base" / "self_critique.yaml"
    
    # 成员变量
    initial_answer: Optional[str]
    
    def __init__(self, template_path: str, initial_answer: Optional[str] = None):
        super().__init__(template_path)
        self.initial_answer = initial_answer
        
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "initial_answer": self.initial_answer
        })
        return data

    def format(self, **kwargs):
        return self.render(**kwargs)

class DomainPrompt(BaseTemplate):
    """领域提示模板"""
    
    # 默认模板路径
    template_path: Path = Path(__file__).parent / "templates" / "domains" / "technical.yaml"
    
    # 成员变量
    domain: Optional[str]
    subdomains: List[str]
    
    def __init__(self, template_path: str, domain: Optional[str] = None, subdomains: Optional[List[str]] = None):
        super().__init__(template_path)
        self.domain = domain if domain else self.domain
        self.subdomains = subdomains if subdomains else self.subdomains
        
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "domain": self.domain,
            "subdomains": self.subdomains
        })
        return data

    def format(self, **kwargs):
        return self.render(**kwargs)

class TaskPrompt(BaseTemplate):
    """任务提示模板"""
    
    # 默认模板路径
    template_path: Path = Path(__file__).parent / "templates" / "tasks" / "qa.yaml"
    
    # 成员变量
    task_type: Optional[str]
    steps: List[str]
    
    def __init__(self, template_path: str, task_type: Optional[str] = None, steps: Optional[List[str]] = None):
        super().__init__(template_path)
        self.task_type = task_type if task_type else self.task_type
        self.steps = steps if steps else self.steps
        
    def to_dict(self) -> Dict:
        data = super().to_dict()
        data.update({
            "task_type": self.task_type,
            "steps": self.steps
        })
        return data

    def format(self, **kwargs):
        return self.render(**kwargs) 