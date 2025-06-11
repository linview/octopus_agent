import os
import yaml
from typing import Dict, Any, Optional, List, Set, Type
from pathlib import Path

from rag_service.app.core.prompts.base import BasePrompt
from rag_service.app.core.prompts.templates import BaseTemplate
from .templates import (
    RoleBasedPrompt,
    ChainOfThoughtPrompt,
    FewShotPrompt,
    SelfConsistencyPrompt,
    SelfCritiquePrompt,
    DomainPrompt,
    TaskPrompt
)

class PromptManager:
    """提示模板管理器"""
    
    # 模板类型映射
    TEMPLATE_TYPES: Dict[str, Type[BaseTemplate]] = {
        # role
        "RoleBasedPrompt": RoleBasedPrompt,
        # policy
        "ChainOfThoughtPrompt": ChainOfThoughtPrompt,
        "FewShotPrompt": FewShotPrompt,
        "SelfConsistencyPrompt": SelfConsistencyPrompt,
        "SelfCritiquePrompt": SelfCritiquePrompt,
        # domain
        "DomainPrompt": DomainPrompt,
        # task
        "TaskPrompt": TaskPrompt
    }
    
    # 成员变量
    templates_dir: Path
    templates: Dict[str, BaseTemplate]
    
    def __init__(self, templates_dir: str):
        """
        初始化提示模板管理器
        
        Args:
            templates_dir: 模板文件目录
        """
        self.templates_dir = Path(templates_dir)
        self.templates = {}
        self._load_templates()
    
    def _load_templates(self):
        """加载所有模板文件"""
        for template_file in self.templates_dir.rglob("*.yaml"):
            with open(template_file, "r", encoding="utf-8") as f:
                template_data = yaml.safe_load(f)
                
            template_type = template_data.get("type")
            if template_type not in self.TEMPLATE_TYPES:
                raise ValueError(f"未知的模板类型: {template_type}")
                
            template_class = self.TEMPLATE_TYPES[template_type]
            template = template_class(
                template_path=str(template_file),
                **{k: v for k, v in template_data.items() if k not in ["template", "type", "desc", "version"]}
            )
            
            self.templates[template_file.stem] = template
    
    def get_template(self, name: str, version: Optional[str] = None) -> BaseTemplate:
        """
        获取指定名称的模板
        
        Args:
            name: 模板名称
            version: 指定版本号，如果为None则使用最新版本
            
        Returns:
            BaseTemplate: 模板实例
            
        Raises:
            KeyError: 当模板不存在时
        """
        if name not in self.templates:
            raise KeyError(f"模板不存在: {name}")
            
        template = self.templates[name]
        if version and version != template.version:
            template._load_template(version)
        return template
    
    def get_template_info(self, name: str, version: Optional[str] = None) -> Dict:
        """
        获取模板信息
        
        Args:
            name: 模板名称
            version: 指定版本号
            
        Returns:
            Dict: 模板信息字典
        """
        template = self.get_template(name, version)
        return template.to_dict()
    
    def list_templates(self) -> List[str]:
        """
        列出所有可用的模板名称
        
        Returns:
            List[str]: 模板名称列表
        """
        return list(self.templates.keys())
    
    def get_templates_by_type(self, template_type: str) -> List[str]:
        """
        获取指定类型的所有模板名称
        
        Args:
            template_type: 模板类型
            
        Returns:
            List[str]: 模板名称列表
        """
        return [
            name for name, template in self.templates.items()
            if template.__class__.__name__ == template_type
        ]
    
    def format_template(self, name: str, version: Optional[str] = None, **kwargs) -> str:
        """
        格式化模板
        
        Args:
            name: 模板名称
            version: 指定版本号
            **kwargs: 模板参数
            
        Returns:
            str: 格式化后的提示文本
        """
        template = self.get_template(name, version)
        return template.render(**kwargs)
    
    def combine_templates(self, strategy: Dict[str, str], version: Optional[str] = None, **kwargs) -> Dict[str, str]:
        """
        组合多个模板
        
        Args:
            strategy: 策略字典，键为模板名称，值为参数名称
            version: 指定版本号
            **kwargs: 模板参数
            
        Returns:
            Dict[str, str]: 组合后的提示文本字典
        """
        result = {}
        for template_name, param_name in strategy.items():
            template = self.get_template(template_name, version)
            result[param_name] = template.format(**kwargs)
        return result 