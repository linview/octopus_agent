# 提示模板管理系统

## 目录结构

```
prompts/
├── templates/
│   ├── base/           # 基础提示工程模式
│   │   ├── chain_of_thought.yaml
│   │   ├── few_shot.yaml
│   │   ├── self_consistency.yaml
│   │   └── self_critique.yaml
│   ├── roles/          # 角色定义
│   │   └── expert.yaml
│   ├── domains/        # 领域知识
│   │   └── technical.yaml
│   └── tasks/          # 任务类型
│       ├── problem_solving.yaml
│       ├── summarization.yaml
│       ├── classification.yaml
│       └── translation.yaml
├── base.py            # 基础类定义
├── templates.py       # 模板类定义
└── manager.py         # 模板管理器
```

## 模板类型

### 1. 基础提示工程模式 (base/)
- Chain of Thought (思维链)
- Few-shot Learning (少样本学习)
- Self-consistency (自我一致性)
- Self-critique (自我批评)

### 2. 角色模板 (roles/)
- 专家角色
- 客服角色
- 其他专业角色

### 3. 领域模板 (domains/)
- 技术领域
- 医疗领域
- 金融领域
- 其他专业领域

### 4. 任务模板 (tasks/)
- 问题解决
- 文本摘要
- 文本分类
- 文本翻译

## 模板格式

每个模板文件 (YAML) 包含以下字段：
```yaml
template: |
  # 模板内容，使用 {{ variable }} 作为占位符
type: TemplateType  # 模板类型
desc: "模板描述"    # 新增：模板描述
version: "1.0.0"    # 新增：版本信息
# 其他类型特定字段
```

## 使用示例

### 1. 基本使用
```python
from rag_service.app.core.prompts.manager import PromptManager

# 初始化管理器
prompt_manager = PromptManager("templates")

# 获取模板信息
template_info = prompt_manager.get_template_info("chain_of_thought")
print(template_info["placeholders"])  # 查看可用占位符

# 格式化模板
prompt = prompt_manager.format_template(
    "chain_of_thought",
    role_instruction="你是一位技术专家",
    question="如何设计一个高并发系统？",
    context="现有系统每秒需要处理10万请求..."
)
```

### 2. 模板组合
```python
# 定义策略
strategy = {
    "expert": "role_instruction",
    "technical": "domain_knowledge",
    "problem_solving": "task_instruction"
}

# 组合模板
result = prompt_manager.combine_templates(
    strategy,
    domain="技术",
    expertise=["系统架构", "性能优化"],
    question="如何设计一个高并发系统？"
)
```

## 模板管理

### 1. 模板验证
- 自动检查模板文件存在性
- 验证占位符完整性
- 检查模板类型有效性

### 2. 模板查询
```python
# 列出所有模板
templates = prompt_manager.list_templates()

# 按类型查询模板
role_templates = prompt_manager.get_templates_by_type("RoleBasedPrompt")
```

### 3. 版本控制
- 每个模板包含版本信息
- 支持模板升级和回滚
- 记录模板变更历史

## 最佳实践

1. 模板设计
   - 保持模板结构清晰
   - 使用有意义的占位符名称
   - 添加详细的模板描述
   - 及时更新版本信息

2. 模板组合
   - 合理使用基础模式
   - 根据需求选择角色
   - 添加必要的领域知识
   - 明确任务类型和步骤

3. 错误处理
   - 检查模板文件存在性
   - 验证占位符完整性
   - 处理模板渲染错误
   - 记录错误日志

4. 维护建议
   - 定期检查模板有效性
   - 及时更新模板内容
   - 保持版本信息准确
   - 维护模板文档 