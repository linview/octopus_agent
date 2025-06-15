import os
import re

from typing import List, Dict, ClassVar, Union
from dotenv import load_dotenv

from langchain.agents import Tool, AgentExecutor, LLMSingleActionAgent
from langchain.prompts import StringPromptTemplate
from langchain.chains import LLMChain
from langchain_community.chat_models import ChatOpenAI
from langchain.tools import BaseTool
from langchain.schema import AgentAction, AgentFinish
from langchain.agents.agent import AgentOutputParser

from rag_service.app.core.utils.timer import timer

MODEL_NAME = "qwen-plus"
MAX_TOKENS = 1024

load_dotenv()

# 定义提示模板
class SQLPromptTemplate(StringPromptTemplate):
    template: ClassVar[str] = """你是一个SQL专家。请将用户的自然语言查询转换为SQL语句。

用户查询: {query}

请按照以下步骤思考：
1. 分析用户查询的意图
2. 确定需要查询的表和字段
3. 构建合适的SQL语句

你的回答应该只包含SQL语句，不需要其他解释。"""

    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)

# test2swql Agent prompt template
class AgentPromptTemplate(StringPromptTemplate):
    template: ClassVar[str] = """你是一个SQL查询助手。请帮助用户将自然语言转换为SQL查询。

<input>
用户查询: {query}
</input>

<requirements>
请按照以下步骤思考：
1. 理解用户的查询意图
2. 选择合适的工具来完成任务
3. 执行必要的操作
4. 输出结果只需要提供SQL语句即可，不需要解释和测试用例
</requirements>

<tools>
可用工具:
{tools}
</tools>

<output>
请使用以下格式：
Action: 要使用的工具名称
Action Input: 工具的输入
Observation: 工具的输出
... (可以有多轮思考和行动)
Final Answer: 最终的SQL查询结果
</output>
"""

    def format(self, **kwargs) -> str:
        return self.template.format(**kwargs)

# tool: SQL generator
class SQLGeneratorTool(BaseTool):
    tool_name : ClassVar[str] = "sql_generator"
    description : ClassVar[str] = "将自然语言查询转换为SQL语句"

    @timer
    def _run(self, query: str) -> str:
        # prompt = SQLPromptTemplate(input_variables=["query"]) # repeat sql gen due to no clear end sign
        prompt = AgentPromptTemplate(input_variables=["query", "tools"])
        chain = LLMChain(
            llm=ChatOpenAI(
                model_name=MODEL_NAME,
                temperature=0,
                max_tokens=MAX_TOKENS,
                openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
                openai_api_base=os.getenv("DASHSCOPE_API_URL")
            ),
            prompt=prompt,
            stop=["\n</output>"]
        )
        tools_description = "\n".join([
            f"{tool.tool_name}: {tool.description}" for tool in [SQLGeneratorTool, SQLEvaluatorTool]
        ])
        return chain.run(query=query, tools=tools_description)

    @timer
    async def _arun(self, query: str) -> str:
        raise NotImplementedError("暂不支持异步操作")

# tool: SQL evaluator
class SQLEvaluatorTool(BaseTool):
    tool_name : ClassVar[str] = "sql_evaluator"
    description : ClassVar[str] = "评估生成的SQL语句是否正确"

    @timer
    def _run(self, sql: str) -> str:
        # TODO: implement sql evaluator
        # e.g. connect to db, execute sql, check result
        return "SQL语句评估通过"

    @timer
    async def _arun(self, sql: str) -> str:
        raise NotImplementedError("暂不支持异步操作")

# 定义输出解析器
class SQLAgentOutputParser(AgentOutputParser):
    def parse(self, text: str) -> Union[AgentAction, AgentFinish]:
        # 检查是否是最终答案
        if "Final Answer:" in text:
            return AgentFinish(
                return_values={"output": text.split("Final Answer:")[-1].strip()},
                log=text
            )
        
        # 解析动作和输入
        action_match = re.search(r"Action: (.*?)[\n]*Action Input: (.*)", text, re.DOTALL)
        if not action_match:
            return AgentFinish(
                return_values={"output": "无法解析动作"},
                log=text
            )
        
        # parse tool name and inputs
        action = action_match.group(1).strip()
        action_input = action_match.group(2).strip()
        
        return AgentAction(tool=action, tool_input=action_input, log=text)

# 创建Agent
def create_sql_agent():
    tools = [
        SQLGeneratorTool(name=SQLGeneratorTool.tool_name, description=SQLGeneratorTool.description),
        SQLEvaluatorTool(name=SQLEvaluatorTool.tool_name, description=SQLEvaluatorTool.description)
    ]

    # 创建Agent提示模板
    prompt = AgentPromptTemplate(input_variables=["query", "tools"])
    
    # 创建Agent
    agent = LLMSingleActionAgent(
        llm_chain=LLMChain(
            llm=ChatOpenAI(
                model_name=MODEL_NAME,
                temperature=0,
                max_tokens=MAX_TOKENS,
                openai_api_key=os.getenv("DASHSCOPE_API_KEY"),
                openai_api_base=os.getenv("DASHSCOPE_API_URL")
            ),
            prompt=prompt
        ),
        output_parser=SQLAgentOutputParser(),
        stop=["\n</output>"],
        allowed_tools=[tool.name for tool in tools]
    )

    return AgentExecutor.from_agent_and_tools(
        agent=agent,
        tools=tools,
        verbose=True
    )


if __name__ == "__main__":
    agent = create_sql_agent()
    
    # 工具列表
    tools_description = "\n".join([
        f"{tool.name}: {tool.description}"
        for tool in agent.tools
    ])

    # 测试用例
    test_query0 = "查询所有用户的姓名和邮箱"
    test_query1 = """
假设我知道有两个表：
```sql
create t1 (id int, curriculum  string, grate int, start_time datetime, end_time datetime);
create t2(id int, name chars, gender chars, grade int);
```

我需要找到在五年级的小明同学都选了哪些课程，并按照开始时间逆序排列

"""
  
    test_query2 = test_query1 + """
在获取到小明最早开始的课程的名称后，反查还有哪些同学选了同一个课程，且跟小明同一时间上课

"""

    for test in [test_query0, test_query1, test_query2]:
        result = agent.run(
            query=test_query2,
            tools=tools_description
        )
        print(result) 
    print("end-of-test")