from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List, Set
from enum import Enum
from jinja2 import Template, TemplateError
from loguru import logger
import re
from pathlib import Path
import yaml


class PromptType(str, Enum):
    PROMPT_TYPE_TASK = "TaskPrompt"
    PROMPT_TYPE_COT = "ChainOfThoughtPrompt"
    PROMPT_TYPE_FEWSHOT = "FewShotPrompt"
    PROMPT_TYPE_SELFCONSISTENCY = "SelfConsistencyPrompt"
    PROMPT_TYPE_SELFCRITIQUE = "SelfCritiquePrompt"
    PROMPT_TYPE_DOMAIN = "DomainPrompt"
    PROMPT_TYPE_ROLE = "RoleBasedPrompt"

class BasePrompt(ABC):
    """提示模板基类"""
    
    template_path: Path
    template_content: str       # default template content with j2_tags placeholder
    version: str
    desc: str
    type: str
    # variant fields in template files
    task_type: str | None = ""
    steps: List[str] | None = []
    domain: str | None = ""
    subdomains: List[str] | None = []
    role: str | None = ""
    expertise: List[str] | None = []
    
    _template: Template
    _j2_tags: Set[str]
    
    def __init__(self, template_path: str):
        """
        初始化提示模板
        
        Args:
            template_path: 模板文件路径
        """
        self.template_path = Path(template_path)
        if not self.template_path.exists():
            raise FileNotFoundError(f"模板文件不存在: {template_path}")
            
        self._load_template()
        
    def _load_variants(self, prompt_type: str, template: dict) -> list[str]:
        """
        按template type加载特有字段
        """
        variants = []
        if prompt_type == PromptType.PROMPT_TYPE_TASK:
            variants = [ "task_type", "steps" ]
        elif prompt_type == PromptType.PROMPT_TYPE_DOMAIN:
            variants = [ "domain", "subdomains" ]
        elif prompt_type == PromptType.PROMPT_TYPE_ROLE:
            variants = [ "role", "expertise" ]
        for attr in variants:
            if not hasattr(self, attr):
                raise ValueError(f"模板缺少特有字段: {attr}")
            setattr(self, attr, template.get(attr))

    
    def _load_template(self, version: Optional[str] = None):
        """
        加载模板内容
        
        Args:
            version: 指定版本号，如果为None则使用最新版本
        """
        with open(self.template_path, "r", encoding="utf-8") as f:
            templates = list(yaml.safe_load_all(f))
            
        if not templates:
            raise ValueError(f"模板文件为空: {self.template_path}")
            
        # 如果指定了版本，查找对应版本
        if version:
            for template in templates:
                if template.get("version") == version:
                    self.template_content = template["template"]
                    self.version = version
                    self.desc = template.get("desc")
                    self.type = template.get("type")
                    self._load_variants(self.type, template)
                    break
            else:
                raise ValueError(f"未找到指定版本的模板: {version}")
        else:
            # 使用最新版本（最后一个）
            template = templates[-1]
            self.template_content = template["template"]
            self.version = template.get("version")
            self.desc = template.get("desc")
            self.type = template.get("type")
            self._load_variants(self.type, template)
        self._template = Template(self.template_content)
        self._j2_tags = self._extract_tags()
        
    def _extract_tags(self) -> Set[str]:
        """提取模板中的所有占位符"""
        pattern = r'{{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*}}'
        return set(re.findall(pattern, self.template_content))
        
    def get_tags(self) -> Set[str]:
        """获取模板中所有可用的占位符"""
        return self._j2_tags.copy()
        
    def validate_tags(self, data: Dict[str, str]) -> None:
        """
        验证提供的占位符数据是否完整
        
        Args:
            data: 占位符数据字典
            
        Raises:
            ValueError: 当提供的占位符数据不完整时
        """
        missing = self._j2_tags - set(data.keys())
        if missing:
            raise ValueError(
                f"""
                    \n>>> file:\n {self.template_path} 
                    \n>>>template:\n {self.template_content} 
                    \n>>> content:\n {data} 
                    \n\n>>> Error: \nmissing tags - {', '.join(missing)}
                """)
            
        extra = set(data.keys()) - self._j2_tags
        if extra:
             logger.warning(f"提供了未使用的占位符: {', '.join(extra)}")
            
    def render(self, **kwargs) -> str:
        """
        渲染模板
        
        Args:
            **kwargs: 占位符数据
            
        Returns:
            str: 渲染后的提示文本
            
        Raises:
            ValueError: 当占位符数据不完整时
            TemplateError: 当模板渲染失败时
        """
        self.validate_tags(kwargs)
        try:
            return self._template.render(**kwargs)
        except TemplateError as e:
            raise TemplateError(f"模板渲染失败: {str(e)}")
    
    @abstractmethod
    def format(self, **kwargs) -> str:
        """格式化提示模板"""
        pass
    
    def to_dict(self) -> Dict[str, Any]:
        """转换为字典格式"""
        return {
            "template": self.template_content,
            "tags": list(self._j2_tags),
            "type": self.__class__.__name__,
            "version": self.version,
            "desc": self.desc
        }
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'BasePrompt':
        """
        从字典创建实例

        Args:
            data: 字典数据
            data["template_path"]: 模板文件路径
            data["version"]: 指定版本号，如果为None则使用最新版本
            
        Returns:
            BasePrompt: 实例
            
        """
        instance = cls(template_path=data["template_path"])
        if "version" in data:
            instance._load_template(version=data["version"])
        return instance 